"""Regras de fluxo dos quizzes (REQ-QZ-*, REQ-RET-*).

Modelo unificado (ADR-0003): um quiz é um conjunto de perguntas; cada pessoa
pode registrar respostas SOBRE_SI (que viram gabarito) e PALPITES sobre o
gabarito do parceiro.

- PERSONALIZADO / RETROSPECTIVA (unilaterais): o autor responde sobre si,
  o parceiro palpita.
- SINTONIA (mútuo): os dois respondem sobre si e os dois palpitam.

    RASCUNHO --gabarito do autor--> ABERTO --todos palpitaram--> ENCERRADO
                                       |                            ^
                                       +--há texto livre pendente-> EM_CORRECAO
    RASCUNHO|ABERTO --prazo vencido sem todos os envios--> EXPIRADO (sem pontos)
    EM_CORRECAO --prazo vencido--> pendentes viram PARCIAL --> ENCERRADO
"""
from collections.abc import Sequence
from datetime import datetime, timedelta

from .enums import FormatoPergunta, Papel, StatusQuiz, TipoQuiz
from .erros import AcessoNegado, RegraViolada, TransicaoInvalida
from .pontuacao import validar_pergunta

MIN_PERGUNTAS = 1
MIN_PERGUNTAS_RETROSPECTIVA = 3
MAX_PERGUNTAS = 15
PRAZO_PADRAO = timedelta(days=7)

TRANSICOES: dict[StatusQuiz, frozenset[StatusQuiz]] = {
    StatusQuiz.RASCUNHO: frozenset({StatusQuiz.ABERTO, StatusQuiz.EXPIRADO}),
    StatusQuiz.ABERTO: frozenset({StatusQuiz.EM_CORRECAO, StatusQuiz.ENCERRADO, StatusQuiz.EXPIRADO}),
    StatusQuiz.EM_CORRECAO: frozenset({StatusQuiz.ENCERRADO}),
    StatusQuiz.ENCERRADO: frozenset(),
    StatusQuiz.EXPIRADO: frozenset(),
}


def transicionar(atual: StatusQuiz, novo: StatusQuiz) -> StatusQuiz:
    if atual == novo:
        return atual
    if novo not in TRANSICOES[atual]:
        raise TransicaoInvalida(f"Quiz {atual.value} não pode passar para {novo.value}.")
    return novo


def status_inicial(tipo: TipoQuiz) -> StatusQuiz:
    return StatusQuiz.ABERTO if tipo.mutuo else StatusQuiz.RASCUNHO


def validar_estrutura(tipo: TipoQuiz, perguntas: Sequence[tuple[FormatoPergunta, list[str] | None, int]]) -> None:
    minimo = MIN_PERGUNTAS_RETROSPECTIVA if tipo is TipoQuiz.RETROSPECTIVA else MIN_PERGUNTAS
    if not minimo <= len(perguntas) <= MAX_PERGUNTAS:
        raise RegraViolada(f"Este quiz precisa ter de {minimo} a {MAX_PERGUNTAS} perguntas.", "QTD_PERGUNTAS")
    for formato, opcoes, pontos in perguntas:
        validar_pergunta(formato, opcoes, pontos)


def quem_responde_sobre_si(tipo: TipoQuiz, autor: Papel) -> frozenset[Papel]:
    return frozenset({Papel.A, Papel.B}) if tipo.mutuo else frozenset({autor})


def quem_palpita(tipo: TipoQuiz, autor: Papel) -> frozenset[Papel]:
    return frozenset({Papel.A, Papel.B}) if tipo.mutuo else frozenset({autor.outro})


def validar_envio_sobre_si(tipo: TipoQuiz, status: StatusQuiz, autor: Papel, solicitante: Papel, ja_enviou: bool) -> None:
    if solicitante not in quem_responde_sobre_si(tipo, autor):
        raise AcessoNegado("Neste quiz só o autor registra o gabarito.", "NAO_AUTOR")
    esperado = StatusQuiz.ABERTO if tipo.mutuo else StatusQuiz.RASCUNHO
    if status is not esperado:
        raise TransicaoInvalida("O gabarito não pode mais ser alterado.", "GABARITO_FECHADO")
    if ja_enviou:
        raise TransicaoInvalida("Você já registrou suas respostas sobre si.", "ENVIO_DUPLICADO")


def validar_envio_palpites(
    tipo: TipoQuiz, status: StatusQuiz, autor: Papel, solicitante: Papel,
    ja_enviou: bool, agora: datetime, prazo: datetime | None,
) -> None:
    if solicitante not in quem_palpita(tipo, autor):
        raise AcessoNegado("Você não pode palpitar no seu próprio gabarito.", "PALPITE_PROPRIO")
    if status is not StatusQuiz.ABERTO:
        raise TransicaoInvalida("Este quiz não está aceitando palpites.", "QUIZ_FECHADO")
    if prazo is not None and agora >= prazo:
        raise TransicaoInvalida("O prazo para palpites terminou.", "PRAZO_ENCERRADO")
    if ja_enviou:
        raise TransicaoInvalida("Você já enviou seus palpites.", "ENVIO_DUPLICADO")


def validar_cobertura(ids_perguntas: set[str], ids_respondidos: list[str]) -> None:
    """Envio é tudo-ou-nada: exatamente uma resposta por pergunta."""
    if len(ids_respondidos) != len(set(ids_respondidos)) or set(ids_respondidos) != ids_perguntas:
        raise RegraViolada("Responda todas as perguntas, uma vez cada.", "COBERTURA_INCOMPLETA")


def proximo_status(
    tipo: TipoQuiz, status: StatusQuiz, autor: Papel,
    enviaram_sobre_si: set[Papel], enviaram_palpites: set[Papel], palpites_pendentes: int,
) -> StatusQuiz:
    """Status resultante depois de um envio ou correção."""
    if not quem_responde_sobre_si(tipo, autor) <= enviaram_sobre_si:
        return status
    if not quem_palpita(tipo, autor) <= enviaram_palpites:
        return transicionar(status, StatusQuiz.ABERTO)
    alvo = StatusQuiz.EM_CORRECAO if palpites_pendentes else StatusQuiz.ENCERRADO
    return transicionar(status, alvo)


def status_ao_vencer_prazo(status: StatusQuiz) -> StatusQuiz | None:
    """None = nada a fazer. EM_CORRECAO encerra (pendentes viram PARCIAL)."""
    if status in (StatusQuiz.RASCUNHO, StatusQuiz.ABERTO):
        return StatusQuiz.EXPIRADO
    if status is StatusQuiz.EM_CORRECAO:
        return StatusQuiz.ENCERRADO
    return None
