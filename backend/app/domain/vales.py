"""Ciclo de vida do vale (REQ-VAL-*).

Um vale é uma OFERTA do criador para o parceiro: "Vale massagem" criado pela
Beatris só pode ser resgatado pelo Lucas, e é a Beatris quem o cumpre.

    DISPONIVEL --resgatar (parceiro, consome 1 crédito)--> RESGATADO
    RESGATADO  --confirmar uso (quem resgatou)-----------> UTILIZADO
    DISPONIVEL --cancelar (criador)----------------------> CANCELADO
"""
from .enums import StatusVale
from .erros import AcessoNegado, RegraViolada, TransicaoInvalida

TAMANHO_TITULO = (3, 80)
LIMITE_DISPONIVEIS_POR_CRIADOR = 20

TRANSICOES: dict[StatusVale, frozenset[StatusVale]] = {
    StatusVale.DISPONIVEL: frozenset({StatusVale.RESGATADO, StatusVale.CANCELADO}),
    StatusVale.RESGATADO: frozenset({StatusVale.UTILIZADO}),
    StatusVale.UTILIZADO: frozenset(),
    StatusVale.CANCELADO: frozenset(),
}


def transicionar(atual: StatusVale, novo: StatusVale) -> StatusVale:
    if novo not in TRANSICOES[atual]:
        raise TransicaoInvalida(f"Vale {atual.value} não pode passar para {novo.value}.")
    return novo


def validar_criacao(titulo: str, disponiveis_do_criador: int) -> None:
    minimo, maximo = TAMANHO_TITULO
    if not minimo <= len(titulo.strip()) <= maximo:
        raise RegraViolada(f"O título do vale deve ter de {minimo} a {maximo} caracteres.", "TITULO_INVALIDO")
    if disponiveis_do_criador >= LIMITE_DISPONIVEIS_POR_CRIADOR:
        raise RegraViolada(
            f"Você já tem {LIMITE_DISPONIVEIS_POR_CRIADOR} vales disponíveis. Cancele algum antes de criar outro.",
            "LIMITE_DE_VALES",
        )


def validar_resgate(status: StatusVale, criador_id: str, solicitante_id: str, tem_credito: bool) -> StatusVale:
    novo = transicionar(status, StatusVale.RESGATADO)
    if solicitante_id == criador_id:
        raise AcessoNegado("Você não pode resgatar um vale que você mesmo ofereceu.", "VALE_PROPRIO")
    if not tem_credito:
        raise RegraViolada(
            "Você precisa de um crédito de vale. Vença a semana, o mês ou um quiz de sintonia.",
            "SEM_CREDITO",
        )
    return novo


def validar_confirmacao_uso(status: StatusVale, beneficiario_id: str | None, solicitante_id: str) -> StatusVale:
    novo = transicionar(status, StatusVale.UTILIZADO)
    if solicitante_id != beneficiario_id:
        raise AcessoNegado("Só quem resgatou o vale confirma que ele foi cumprido.", "NAO_BENEFICIARIO")
    return novo


def validar_cancelamento(status: StatusVale, criador_id: str, solicitante_id: str) -> StatusVale:
    novo = transicionar(status, StatusVale.CANCELADO)
    if solicitante_id != criador_id:
        raise AcessoNegado("Só quem criou o vale pode cancelá-lo.", "NAO_CRIADOR")
    return novo
