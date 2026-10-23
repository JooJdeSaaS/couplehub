"""Regras de pontuação de quizzes e retrospectivas (REQ-PTS-*).

Funções puras: recebem valores, devolvem valores. Nada aqui toca banco ou HTTP,
o que permite testar todas as regras sem infraestrutura (ver ADR-0007).
"""
from dataclasses import dataclass
from statistics import mean

from .enums import FormatoPergunta, ResultadoPalpite
from .erros import RegraViolada
from .texto import normalizar

PONTOS_PADRAO_PERGUNTA = 10
PONTOS_MIN_PERGUNTA = 2
PONTOS_MAX_PERGUNTA = 50
FATOR_BONUS_PERFEITO = 0.20
PONTOS_PARTICIPACAO_RETROSPECTIVA = 5
ESCALA_MIN, ESCALA_MAX = 1, 5
MIN_OPCOES, MAX_OPCOES = 2, 6
MAX_TAMANHO_TEXTO = 280
JANELA_COMPATIBILIDADE = 10

_VERDADEIRO = {"verdadeiro", "v", "true", "sim", "s"}
_FALSO = {"falso", "f", "false", "nao", "n"}


# --- Validação ---------------------------------------------------------------
def validar_pergunta(formato: FormatoPergunta, opcoes: list[str] | None, pontos: int) -> None:
    if not PONTOS_MIN_PERGUNTA <= pontos <= PONTOS_MAX_PERGUNTA:
        raise RegraViolada(
            f"Cada pergunta vale entre {PONTOS_MIN_PERGUNTA} e {PONTOS_MAX_PERGUNTA} pontos.",
            "PONTOS_FORA_DO_INTERVALO",
        )
    if formato is FormatoPergunta.MULTIPLA_ESCOLHA:
        opcoes = opcoes or []
        distintas = {normalizar(o) for o in opcoes if o.strip()}
        if not MIN_OPCOES <= len(distintas) == len(opcoes) <= MAX_OPCOES:
            raise RegraViolada(
                f"Múltipla escolha exige de {MIN_OPCOES} a {MAX_OPCOES} opções distintas.",
                "OPCOES_INVALIDAS",
            )
    elif opcoes:
        raise RegraViolada("Só perguntas de múltipla escolha têm opções.", "OPCOES_INVALIDAS")


def canonizar_valor(formato: FormatoPergunta, valor: str, opcoes: list[str] | None = None) -> str:
    """Valida a resposta conforme o formato e devolve sua forma canônica."""
    bruto = (valor or "").strip()
    if not bruto:
        raise RegraViolada("Resposta vazia.", "RESPOSTA_VAZIA")

    if formato is FormatoPergunta.MULTIPLA_ESCOLHA:
        for opcao in opcoes or []:
            if normalizar(opcao) == normalizar(bruto):
                return opcao
        raise RegraViolada("A resposta precisa ser uma das opções.", "OPCAO_INEXISTENTE")

    if formato is FormatoPergunta.VERDADEIRO_FALSO:
        chave = normalizar(bruto)
        if chave in _VERDADEIRO:
            return "VERDADEIRO"
        if chave in _FALSO:
            return "FALSO"
        raise RegraViolada("Use verdadeiro ou falso.", "VALOR_INVALIDO")

    if formato is FormatoPergunta.ESCALA:
        try:
            numero = int(bruto)
        except ValueError:
            raise RegraViolada("Escala aceita apenas números inteiros.", "VALOR_INVALIDO") from None
        if not ESCALA_MIN <= numero <= ESCALA_MAX:
            raise RegraViolada(f"Escala vai de {ESCALA_MIN} a {ESCALA_MAX}.", "VALOR_INVALIDO")
        return str(numero)

    if len(bruto) > MAX_TAMANHO_TEXTO:
        raise RegraViolada(f"Máximo de {MAX_TAMANHO_TEXTO} caracteres.", "TEXTO_LONGO")
    return bruto


# --- Avaliação ---------------------------------------------------------------
def avaliar_palpite(formato: FormatoPergunta, gabarito: str, palpite: str) -> ResultadoPalpite:
    """Correção automática. Texto livre diferente do gabarito fica PENDENTE
    para o dono do gabarito corrigir (REQ-PTS-004)."""
    if formato is FormatoPergunta.ESCALA:
        distancia = abs(int(gabarito) - int(palpite))
        if distancia == 0:
            return ResultadoPalpite.ACERTO
        return ResultadoPalpite.PARCIAL if distancia == 1 else ResultadoPalpite.ERRO

    if normalizar(gabarito) == normalizar(palpite):
        return ResultadoPalpite.ACERTO
    if formato is FormatoPergunta.TEXTO_LIVRE:
        return ResultadoPalpite.PENDENTE
    return ResultadoPalpite.ERRO


def validar_correcao_manual(resultado: ResultadoPalpite) -> None:
    if resultado is ResultadoPalpite.PENDENTE:
        raise RegraViolada("Correção precisa ser ACERTO, PARCIAL ou ERRO.", "CORRECAO_INVALIDA")


def pontos_do_palpite(resultado: ResultadoPalpite, pontos_pergunta: int) -> int:
    if resultado is ResultadoPalpite.ACERTO:
        return pontos_pergunta
    if resultado is ResultadoPalpite.PARCIAL:
        return pontos_pergunta // 2
    if resultado is ResultadoPalpite.ERRO:
        return 0
    raise RegraViolada("Palpite ainda não corrigido.", "PALPITE_PENDENTE")


# --- Consolidação ------------------------------------------------------------
@dataclass(frozen=True)
class ResumoPontuacao:
    pontos_base: int
    pontos_possiveis: int
    bonus: int
    acertos: int
    total_perguntas: int

    @property
    def total(self) -> int:
        return self.pontos_base + self.bonus

    @property
    def percentual(self) -> float:
        if not self.pontos_possiveis:
            return 0.0
        return round(100 * self.pontos_base / self.pontos_possiveis, 1)

    @property
    def perfeito(self) -> bool:
        return self.total_perguntas > 0 and self.acertos == self.total_perguntas


def consolidar(itens: list[tuple[ResultadoPalpite, int]]) -> ResumoPontuacao:
    """`itens` = [(resultado, pontos_da_pergunta), ...] de UM palpiteiro em UM quiz."""
    base = sum(pontos_do_palpite(r, p) for r, p in itens)
    possiveis = sum(p for _, p in itens)
    acertos = sum(1 for r, _ in itens if r is ResultadoPalpite.ACERTO)
    perfeito = bool(itens) and acertos == len(itens)
    bonus = round(base * FATOR_BONUS_PERFEITO) if perfeito else 0
    return ResumoPontuacao(base, possiveis, bonus, acertos, len(itens))


def indice_compatibilidade(percentuais: list[float], janela: int = JANELA_COMPATIBILIDADE) -> float | None:
    """Média dos últimos `janela` percentuais (lista em ordem cronológica)."""
    recentes = percentuais[-janela:]
    return round(mean(recentes), 1) if recentes else None
