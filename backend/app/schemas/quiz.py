from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import FormatoPergunta, ResultadoPalpite, StatusQuiz, TipoQuiz
from app.domain.pontuacao import PONTOS_PADRAO_PERGUNTA


class PerguntaEntrada(BaseModel):
    enunciado: str = Field(min_length=3, max_length=280)
    formato: FormatoPergunta
    opcoes: list[str] | None = None
    pontos: int = PONTOS_PADRAO_PERGUNTA


class QuizEntrada(BaseModel):
    tipo: TipoQuiz
    titulo: str = Field(min_length=3, max_length=120)
    perguntas: list[PerguntaEntrada]


class RespostaEntrada(BaseModel):
    pergunta_id: str
    valor: str = Field(max_length=280)


class EnvioRespostas(BaseModel):
    respostas: list[RespostaEntrada]


class CorrecaoEntrada(BaseModel):
    resposta_id: str
    resultado: ResultadoPalpite


class EnvioCorrecoes(BaseModel):
    correcoes: list[CorrecaoEntrada] = Field(min_length=1)


class QuizResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tipo: TipoQuiz
    titulo: str
    status: StatusQuiz
    autor_id: str
    semana_ref: str | None
    prazo: datetime | None
    percentual_sintonia: float | None
    criado_em: datetime
    encerrado_em: datetime | None


class PalpiteVisao(BaseModel):
    resposta_id: str
    valor: str
    resultado: ResultadoPalpite | None
    pontos_obtidos: int | None


class PerguntaVisao(BaseModel):
    id: str
    ordem: int
    enunciado: str
    formato: FormatoPergunta
    opcoes: list[str] | None
    pontos: int
    minha_resposta: str | None
    meu_palpite: PalpiteVisao | None
    gabarito_do_parceiro: str | None   # só após ENCERRADO
    palpite_do_parceiro: PalpiteVisao | None  # após ENCERRADO ou quando eu preciso corrigir


class EnvioStatus(BaseModel):
    sobre_si: bool
    palpites: bool


class QuizDetalhe(QuizResumo):
    perguntas: list[PerguntaVisao]
    eu: EnvioStatus
    parceiro: EnvioStatus
    acoes_disponiveis: list[str]       # dica para a UI: RESPONDER_SOBRE_SI, PALPITAR, CORRIGIR


class ItemCompatibilidade(BaseModel):
    quiz_id: str
    titulo: str
    tipo: TipoQuiz
    percentual: float
    encerrado_em: datetime


class CompatibilidadeSaida(BaseModel):
    indice: float | None
    quizzes_considerados: int
    historico: list[ItemCompatibilidade]


class TemplatePergunta(BaseModel):
    enunciado: str
    formato: FormatoPergunta
    opcoes: list[str] | None = None
    pontos: int = PONTOS_PADRAO_PERGUNTA
