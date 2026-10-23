"""Quizzes personalizados, de sintonia e retrospectiva semanal (RF05, RF06)."""
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.domain.enums import StatusQuiz, TipoQuiz
from app.schemas.quiz import (
    CompatibilidadeSaida,
    EnvioCorrecoes,
    EnvioRespostas,
    QuizDetalhe,
    QuizEntrada,
    QuizResumo,
    TemplatePergunta,
)
from app.seed.catalogo import TEMPLATE_RETROSPECTIVA
from app.services import quiz_service

from ..deps import DB, Ctx, Notificar

router = APIRouter(prefix="/quizzes", tags=["Quizzes e retrospectiva"])


@router.get("", response_model=list[QuizResumo])
def listar(
    ctx: Ctx, db: DB, tipo: TipoQuiz | None = None,
    status_: Annotated[StatusQuiz | None, Query(alias="status")] = None,
):
    return quiz_service.listar(db, ctx, tipo, status_)


@router.get("/templates/retrospectiva", response_model=list[TemplatePergunta],
            summary="Perguntas sugeridas para o 'Como foi sua semana?'")
def template_retrospectiva(ctx: Ctx):
    return TEMPLATE_RETROSPECTIVA


@router.get("/compatibilidade", response_model=CompatibilidadeSaida)
def compatibilidade(ctx: Ctx, db: DB):
    return quiz_service.compatibilidade(db, ctx)


@router.post("", response_model=QuizDetalhe, status_code=status.HTTP_201_CREATED)
def criar(dados: QuizEntrada, ctx: Ctx, db: DB, notificar: Notificar):
    quiz = quiz_service.criar(db, ctx, dados)
    notificar(ctx, "quiz.criado", quiz_id=quiz.id)
    return quiz_service.montar_visao(ctx, quiz)


@router.get("/{quiz_id}", response_model=QuizDetalhe)
def detalhe(quiz_id: str, ctx: Ctx, db: DB):
    return quiz_service.montar_visao(ctx, quiz_service.obter(db, ctx, quiz_id))


@router.put("/{quiz_id}/sobre-mim", response_model=QuizDetalhe,
            summary="Registra minhas respostas sobre mim (viram gabarito para o parceiro)")
def enviar_sobre_si(quiz_id: str, envio: EnvioRespostas, ctx: Ctx, db: DB, notificar: Notificar):
    quiz = quiz_service.enviar_sobre_si(db, ctx, quiz_id, envio.respostas)
    notificar(ctx, "quiz.atualizado", quiz_id=quiz.id, status=quiz.status)
    return quiz_service.montar_visao(ctx, quiz)


@router.put("/{quiz_id}/palpites", response_model=QuizDetalhe, summary="Envia meus palpites sobre o parceiro")
def enviar_palpites(quiz_id: str, envio: EnvioRespostas, ctx: Ctx, db: DB, notificar: Notificar):
    quiz = quiz_service.enviar_palpites(db, ctx, quiz_id, envio.respostas)
    notificar(ctx, "quiz.atualizado", quiz_id=quiz.id, status=quiz.status)
    return quiz_service.montar_visao(ctx, quiz)


@router.post("/{quiz_id}/correcoes", response_model=QuizDetalhe,
             summary="Dono do gabarito corrige palpites de texto livre")
def corrigir(quiz_id: str, envio: EnvioCorrecoes, ctx: Ctx, db: DB, notificar: Notificar):
    quiz = quiz_service.corrigir(db, ctx, quiz_id, envio.correcoes)
    notificar(ctx, "quiz.atualizado", quiz_id=quiz.id, status=quiz.status)
    return quiz_service.montar_visao(ctx, quiz)
