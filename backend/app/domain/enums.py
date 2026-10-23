"""Enumerações do domínio CoupleHUB.

Todas são StrEnum: o valor gravado no banco é igual ao nome, o que deixa o
SQLite legível em consultas manuais e simplifica a serialização JSON.
"""
from enum import StrEnum


# --- Conta e casal -----------------------------------------------------------
class Papel(StrEnum):
    """Posição do usuário dentro do casal (relação 1:1 simétrica)."""
    A = "A"
    B = "B"

    @property
    def outro(self) -> "Papel":
        return Papel.B if self is Papel.A else Papel.A


class StatusCasal(StrEnum):
    AGUARDANDO_PARCEIRO = "AGUARDANDO_PARCEIRO"
    ATIVO = "ATIVO"
    ENCERRADO = "ENCERRADO"


class ProvedorAuth(StrEnum):
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"
    APPLE = "APPLE"


# --- Quizzes e retrospectiva -------------------------------------------------
class TipoQuiz(StrEnum):
    """PERSONALIZADO e RETROSPECTIVA são unilaterais (um gabarito, um palpiteiro);
    SINTONIA é mútuo (os dois respondem sobre si e palpitam sobre o outro)."""
    PERSONALIZADO = "PERSONALIZADO"
    SINTONIA = "SINTONIA"
    RETROSPECTIVA = "RETROSPECTIVA"

    @property
    def mutuo(self) -> bool:
        return self is TipoQuiz.SINTONIA


class StatusQuiz(StrEnum):
    RASCUNHO = "RASCUNHO"          # autor ainda não registrou o gabarito
    ABERTO = "ABERTO"              # aceitando palpites
    EM_CORRECAO = "EM_CORRECAO"    # há palpites de texto livre aguardando correção
    ENCERRADO = "ENCERRADO"        # pontuado e lançado no ranking
    EXPIRADO = "EXPIRADO"          # prazo vencido sem palpites


class FormatoPergunta(StrEnum):
    MULTIPLA_ESCOLHA = "MULTIPLA_ESCOLHA"
    VERDADEIRO_FALSO = "VERDADEIRO_FALSO"
    ESCALA = "ESCALA"              # inteiro de 1 a 5
    TEXTO_LIVRE = "TEXTO_LIVRE"


class NaturezaResposta(StrEnum):
    SOBRE_SI = "SOBRE_SI"          # vira gabarito para o parceiro
    PALPITE = "PALPITE"            # tentativa de adivinhar o gabarito do parceiro


class ResultadoPalpite(StrEnum):
    PENDENTE = "PENDENTE"
    ACERTO = "ACERTO"
    PARCIAL = "PARCIAL"
    ERRO = "ERRO"


# --- Pontos, ranking e créditos ----------------------------------------------
class OrigemPontos(StrEnum):
    QUIZ_PALPITE = "QUIZ_PALPITE"
    QUIZ_BONUS_PERFEITO = "QUIZ_BONUS_PERFEITO"
    RETROSPECTIVA_PARTICIPACAO = "RETROSPECTIVA_PARTICIPACAO"


class TipoPeriodo(StrEnum):
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"


class ResultadoPeriodo(StrEnum):
    VITORIA_A = "VITORIA_A"
    VITORIA_B = "VITORIA_B"
    EMPATE = "EMPATE"
    SEM_DISPUTA = "SEM_DISPUTA"    # ninguém pontuou


class OrigemCredito(StrEnum):
    VENCEDOR_SEMANA = "VENCEDOR_SEMANA"
    VENCEDOR_MES = "VENCEDOR_MES"
    VENCEDOR_QUIZ_SINTONIA = "VENCEDOR_QUIZ_SINTONIA"


class StatusCredito(StrEnum):
    PENDENTE = "PENDENTE"
    CONSUMIDO = "CONSUMIDO"
    EXPIRADO = "EXPIRADO"


# --- Vales -------------------------------------------------------------------
class StatusVale(StrEnum):
    DISPONIVEL = "DISPONIVEL"
    RESGATADO = "RESGATADO"
    UTILIZADO = "UTILIZADO"
    CANCELADO = "CANCELADO"


# --- Minigame de decisão -----------------------------------------------------
class ContextoDecisao(StrEnum):
    RESTAURANTE = "RESTAURANTE"
    ROLE = "ROLE"
    OUTRO = "OUTRO"


class StatusDecisao(StrEnum):
    COLETANDO = "COLETANDO"
    RESOLVIDA = "RESOLVIDA"
    CANCELADA = "CANCELADA"


class TipoResultadoDecisao(StrEnum):
    MATCH = "MATCH"                # opção em comum, não vetada
    PONDERADO = "PONDERADO"        # sorteio ponderado pelos pesos
    CARA_OU_COROA = "CARA_OU_COROA"  # tudo vetado: sorteia quem escolhe


# --- Ideias de dates ---------------------------------------------------------
class AmbienteDate(StrEnum):
    EM_CASA = "EM_CASA"
    FORA_DE_CASA = "FORA_DE_CASA"


class CategoriaDate(StrEnum):
    GASTRONOMIA = "GASTRONOMIA"
    CULTURA = "CULTURA"
    AVENTURA = "AVENTURA"
    RELAXAMENTO = "RELAXAMENTO"
    CRIATIVO = "CRIATIVO"
    ESPORTE = "ESPORTE"
    ROMANTICO = "ROMANTICO"


class CustoDate(StrEnum):
    GRATIS = "GRATIS"
    BAIXO = "BAIXO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"
