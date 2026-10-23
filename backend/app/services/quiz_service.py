"""Quizzes personalizados, de sintonia e retrospectiva semanal (RF05, RF06).

As regras ficam em app/domain (quiz.py e pontuacao.py); aqui só orquestramos
carga, persistência, lançamento de pontos e emissão de créditos.
"""
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import relogio
from app.domain import quiz as regras
from app.domain.enums import (
    FormatoPergunta,
    NaturezaResposta,
    OrigemCredito,
    OrigemPontos,
    Papel,
    ResultadoPalpite,
    StatusQuiz,
    TipoQuiz,
)
from app.domain.erros import AcessoNegado, NaoEncontrado, RegraViolada, TransicaoInvalida
from app.domain.periodos import fechamento_semana, semana_do_instante
from app.domain.pontuacao import (
    PONTOS_PARTICIPACAO_RETROSPECTIVA,
    avaliar_palpite,
    canonizar_valor,
    consolidar,
    indice_compatibilidade,
    pontos_do_palpite,
    validar_correcao_manual,
)
from app.domain.ranking import apurar, vencedores
from app.models import Pergunta, Quiz, Resposta
from app.schemas.quiz import CorrecaoEntrada, QuizEntrada, RespostaEntrada

from . import pontos_service
from .contexto import Contexto, obter_do_casal

SOBRE_SI, PALPITE = NaturezaResposta.SOBRE_SI, NaturezaResposta.PALPITE
_STATUS_COM_PRAZO = (StatusQuiz.RASCUNHO, StatusQuiz.ABERTO, StatusQuiz.EM_CORRECAO)


# --- Consultas ---------------------------------------------------------------
def listar(db: Session, ctx: Contexto, tipo: TipoQuiz | None = None, status: StatusQuiz | None = None) -> list[Quiz]:
    if aplicar_prazos(db, ctx, relogio.agora()):
        db.commit()
    consulta = select(Quiz).where(Quiz.casal_id == ctx.casal.id).order_by(Quiz.criado_em.desc())
    if tipo:
        consulta = consulta.where(Quiz.tipo == tipo)
    if status:
        consulta = consulta.where(Quiz.status == status)
    return list(db.scalars(consulta))


def obter(db: Session, ctx: Contexto, quiz_id: str) -> Quiz:
    quiz = obter_do_casal(db, Quiz, quiz_id, ctx.casal.id, "Quiz")
    if _aplicar_prazo(db, ctx, quiz, relogio.agora()):
        db.commit()
    return quiz


def compatibilidade(db: Session, ctx: Contexto) -> dict:
    encerrados = list(db.scalars(
        select(Quiz)
        .where(Quiz.casal_id == ctx.casal.id, Quiz.status == StatusQuiz.ENCERRADO)
        .order_by(Quiz.encerrado_em)
    ))
    percentuais = [q.percentual_sintonia or 0.0 for q in encerrados]
    recentes = encerrados[-10:]
    return {
        "indice": indice_compatibilidade(percentuais),
        "quizzes_considerados": len(recentes),
        "historico": [
            {"quiz_id": q.id, "titulo": q.titulo, "tipo": q.tipo,
             "percentual": q.percentual_sintonia or 0.0, "encerrado_em": q.encerrado_em}
            for q in reversed(recentes)
        ],
    }


# --- Comandos ----------------------------------------------------------------
def criar(db: Session, ctx: Contexto, dados: QuizEntrada) -> Quiz:
    regras.validar_estrutura(dados.tipo, [(p.formato, p.opcoes, p.pontos) for p in dados.perguntas])
    agora = relogio.agora()
    quiz = Quiz(
        casal_id=ctx.casal.id, autor_id=ctx.usuario.id, tipo=dados.tipo,
        titulo=dados.titulo.strip(), status=regras.status_inicial(dados.tipo),
    )
    if dados.tipo is TipoQuiz.RETROSPECTIVA:
        semana = semana_do_instante(agora)
        ja_existe = db.scalar(select(Quiz.id).where(
            Quiz.autor_id == ctx.usuario.id, Quiz.tipo == TipoQuiz.RETROSPECTIVA, Quiz.semana_ref == semana,
        ))
        if ja_existe:
            raise RegraViolada("Você já criou a sua retrospectiva desta semana.", "RETROSPECTIVA_JA_EXISTE")
        quiz.semana_ref, quiz.prazo = semana, fechamento_semana(semana)
    if dados.tipo.mutuo:
        quiz.publicado_em, quiz.prazo = agora, agora + regras.PRAZO_PADRAO

    quiz.perguntas = [
        Pergunta(
            ordem=i, enunciado=p.enunciado.strip(), formato=p.formato, pontos=p.pontos,
            opcoes=[o.strip() for o in p.opcoes or []] if p.formato is FormatoPergunta.MULTIPLA_ESCOLHA else None,
        )
        for i, p in enumerate(dados.perguntas, start=1)
    ]
    db.add(quiz)
    db.commit()
    return quiz


def enviar_sobre_si(db: Session, ctx: Contexto, quiz_id: str, respostas: list[RespostaEntrada]) -> Quiz:
    quiz = obter(db, ctx, quiz_id)
    agora = relogio.agora()
    regras.validar_envio_sobre_si(
        quiz.tipo, quiz.status, ctx.papel_de(quiz.autor_id), ctx.papel,
        ja_enviou=ctx.papel in _quem_enviou(ctx, quiz, SOBRE_SI),
    )
    _registrar(ctx, quiz, respostas, SOBRE_SI)

    if not quiz.tipo.mutuo:
        quiz.publicado_em = agora
        if quiz.tipo is TipoQuiz.PERSONALIZADO:
            quiz.prazo = agora + regras.PRAZO_PADRAO
        else:  # RETROSPECTIVA: preencher a própria semana também pontua (REQ-RET-005)
            pontos_service.lancar(
                db, ctx.casal.id, ctx.usuario.id, PONTOS_PARTICIPACAO_RETROSPECTIVA,
                OrigemPontos.RETROSPECTIVA_PARTICIPACAO, quiz.id, quiz.semana_ref,
                "Contou como foi a semana",
            )
    _avaliar_automaticamente(ctx, quiz)
    _atualizar_status(db, ctx, quiz, agora)
    db.commit()
    return quiz


def enviar_palpites(db: Session, ctx: Contexto, quiz_id: str, respostas: list[RespostaEntrada]) -> Quiz:
    quiz = obter(db, ctx, quiz_id)
    agora = relogio.agora()
    regras.validar_envio_palpites(
        quiz.tipo, quiz.status, ctx.papel_de(quiz.autor_id), ctx.papel,
        ja_enviou=ctx.papel in _quem_enviou(ctx, quiz, PALPITE), agora=agora, prazo=quiz.prazo,
    )
    _registrar(ctx, quiz, respostas, PALPITE)
    _avaliar_automaticamente(ctx, quiz)
    _atualizar_status(db, ctx, quiz, agora)
    db.commit()
    return quiz


def corrigir(db: Session, ctx: Contexto, quiz_id: str, correcoes: list[CorrecaoEntrada]) -> Quiz:
    quiz = obter(db, ctx, quiz_id)
    agora = relogio.agora()
    if quiz.status not in (StatusQuiz.ABERTO, StatusQuiz.EM_CORRECAO):
        raise TransicaoInvalida("Este quiz não aceita mais correções.", "QUIZ_FECHADO")

    por_id = {r.id: (r, p) for p in quiz.perguntas for r in p.respostas if r.natureza is PALPITE}
    for correcao in correcoes:
        validar_correcao_manual(correcao.resultado)
        if correcao.resposta_id not in por_id:
            raise NaoEncontrado("Palpite não encontrado neste quiz.")
        resposta, pergunta = por_id[correcao.resposta_id]
        if resposta.usuario_id == ctx.usuario.id:
            raise AcessoNegado("Quem corrige é o dono do gabarito, não quem palpitou.", "AUTOCORRECAO")
        if resposta.resultado is not ResultadoPalpite.PENDENTE:
            raise TransicaoInvalida("Este palpite não está aguardando correção.", "NAO_PENDENTE")
        resposta.resultado = correcao.resultado
        resposta.pontos_obtidos = pontos_do_palpite(correcao.resultado, pergunta.pontos)
        resposta.corrigida_por_id, resposta.corrigida_em = ctx.usuario.id, agora

    _atualizar_status(db, ctx, quiz, agora)
    db.commit()
    return quiz


# --- Prazos ------------------------------------------------------------------
def aplicar_prazos(db: Session, ctx: Contexto, agora: datetime) -> bool:
    """Expira/encerra todos os quizzes vencidos do casal. Chamado antes de
    listar e antes de fechar o ranking (fechamento preguiçoso — ADR-0004)."""
    vencidos = list(db.scalars(select(Quiz).where(
        Quiz.casal_id == ctx.casal.id, Quiz.status.in_(_STATUS_COM_PRAZO),
        Quiz.prazo.is_not(None), Quiz.prazo <= agora,
    )))
    alterados = [_aplicar_prazo(db, ctx, q, agora) for q in vencidos]
    return any(alterados)


def _aplicar_prazo(db: Session, ctx: Contexto, quiz: Quiz, agora: datetime) -> bool:
    if quiz.prazo is None or agora < quiz.prazo:
        return False
    novo = regras.status_ao_vencer_prazo(quiz.status)
    if novo is None:
        return False
    if novo is StatusQuiz.EXPIRADO:
        quiz.status = regras.transicionar(quiz.status, novo)
        return True
    # EM_CORRECAO vencido: palpites não corrigidos recebem o benefício da dúvida (REQ-QZ-011)
    for pergunta in quiz.perguntas:
        for r in pergunta.respostas:
            if r.natureza is PALPITE and r.resultado is ResultadoPalpite.PENDENTE:
                r.resultado = ResultadoPalpite.PARCIAL
                r.pontos_obtidos = pontos_do_palpite(ResultadoPalpite.PARCIAL, pergunta.pontos)
                r.corrigida_em = agora
    quiz.status = regras.transicionar(quiz.status, StatusQuiz.ENCERRADO)
    _encerrar(db, ctx, quiz, agora, momento_pontos=quiz.prazo)
    return True


# --- Internos ----------------------------------------------------------------
def _respostas(quiz: Quiz) -> list[Resposta]:
    return [r for p in quiz.perguntas for r in p.respostas]


def _quem_enviou(ctx: Contexto, quiz: Quiz, natureza: NaturezaResposta) -> set[Papel]:
    return {ctx.papel_de(r.usuario_id) for r in _respostas(quiz) if r.natureza is natureza}


def _registrar(ctx: Contexto, quiz: Quiz, respostas: list[RespostaEntrada], natureza: NaturezaResposta) -> None:
    perguntas = {p.id: p for p in quiz.perguntas}
    regras.validar_cobertura(set(perguntas), [r.pergunta_id for r in respostas])
    for entrada in respostas:
        pergunta = perguntas[entrada.pergunta_id]
        valor = canonizar_valor(pergunta.formato, entrada.valor, pergunta.opcoes)
        pergunta.respostas.append(Resposta(usuario_id=ctx.usuario.id, natureza=natureza, valor=valor))


def _avaliar_automaticamente(ctx: Contexto, quiz: Quiz) -> None:
    """Corrige os palpite cujo gabarito já existe. No modo SINTONIA o gabarito
    do parceiro pode chegar depois do palpite; por isso a avaliação é retomada
    a cada envio."""
    for pergunta in quiz.perguntas:
        gabaritos = {r.usuario_id: r.valor for r in pergunta.respostas if r.natureza is SOBRE_SI}
        for r in pergunta.respostas:
            dono = ctx.outro_id(r.usuario_id)
            if r.natureza is PALPITE and r.resultado is None and dono in gabaritos:
                r.resultado = avaliar_palpite(pergunta.formato, gabaritos[dono], r.valor)
                if r.resultado is not ResultadoPalpite.PENDENTE:
                    r.pontos_obtidos = pontos_do_palpite(r.resultado, pergunta.pontos)


def _pendentes(quiz: Quiz) -> int:
    return sum(
        1 for r in _respostas(quiz)
        if r.natureza is PALPITE and r.resultado in (None, ResultadoPalpite.PENDENTE)
    )


def _atualizar_status(db: Session, ctx: Contexto, quiz: Quiz, agora: datetime) -> None:
    novo = regras.proximo_status(
        quiz.tipo, quiz.status, ctx.papel_de(quiz.autor_id),
        _quem_enviou(ctx, quiz, SOBRE_SI), _quem_enviou(ctx, quiz, PALPITE), _pendentes(quiz),
    )
    if novo is not quiz.status:
        quiz.status = novo
        if novo is StatusQuiz.ENCERRADO:
            _encerrar(db, ctx, quiz, agora, momento_pontos=agora)


def _encerrar(db: Session, ctx: Contexto, quiz: Quiz, agora: datetime, momento_pontos: datetime) -> None:
    """Consolida a pontuação de cada palpiteiro, lança no ranking e, no modo
    SINTONIA, dá crédito de vale ao vencedor (REQ-PTS-006, REQ-CRD-002)."""
    quiz.encerrado_em = agora
    semana = quiz.semana_ref or semana_do_instante(momento_pontos)

    itens: dict[str, list[tuple[ResultadoPalpite, int]]] = defaultdict(list)
    for pergunta in quiz.perguntas:
        for r in pergunta.respostas:
            if r.natureza is PALPITE:
                itens[r.usuario_id].append((r.resultado, pergunta.pontos))

    totais: dict[str, int] = {}
    base_total = possiveis_total = 0
    for usuario_id, lista in itens.items():
        resumo = consolidar(lista)
        totais[usuario_id] = resumo.total
        base_total += resumo.pontos_base
        possiveis_total += resumo.pontos_possiveis
        pontos_service.lancar(db, ctx.casal.id, usuario_id, resumo.pontos_base, OrigemPontos.QUIZ_PALPITE,
                              quiz.id, semana, f"Palpites em '{quiz.titulo}'")
        pontos_service.lancar(db, ctx.casal.id, usuario_id, resumo.bonus, OrigemPontos.QUIZ_BONUS_PERFEITO,
                              quiz.id, semana, f"Gabaritou '{quiz.titulo}'")

    quiz.percentual_sintonia = round(100 * base_total / possiveis_total, 1) if possiveis_total else 0.0

    if quiz.tipo.mutuo:
        resultado = apurar(totais.get(ctx.id_do_papel(Papel.A), 0), totais.get(ctx.id_do_papel(Papel.B), 0))
        for papel in vencedores(resultado):
            pontos_service.emitir_credito(db, ctx.casal.id, ctx.id_do_papel(papel),
                                          OrigemCredito.VENCEDOR_QUIZ_SINTONIA, quiz.id, agora)


# --- Visão para a API (o que cada parceiro pode ver) -------------------------
def _palpite(r: Resposta | None) -> dict | None:
    if r is None:
        return None
    return {"resposta_id": r.id, "valor": r.valor, "resultado": r.resultado, "pontos_obtidos": r.pontos_obtidos}


def montar_visao(ctx: Contexto, quiz: Quiz) -> dict:
    """Aplica REQ-QZ-013: antes de ENCERRADO ninguém vê o gabarito do outro, e
    só vê palpites do outro que estejam aguardando a SUA correção."""
    eu, parceiro = ctx.usuario.id, ctx.parceiro.id
    encerrado = quiz.status is StatusQuiz.ENCERRADO
    perguntas, precisa_corrigir = [], False

    for p in quiz.perguntas:
        por = {(r.usuario_id, r.natureza): r for r in p.respostas}
        minha, meu_palpite = por.get((eu, SOBRE_SI)), por.get((eu, PALPITE))
        gabarito_parceiro, palpite_parceiro = por.get((parceiro, SOBRE_SI)), por.get((parceiro, PALPITE))
        aguardando_minha_correcao = bool(palpite_parceiro and palpite_parceiro.resultado is ResultadoPalpite.PENDENTE)
        precisa_corrigir |= aguardando_minha_correcao
        perguntas.append({
            "id": p.id, "ordem": p.ordem, "enunciado": p.enunciado, "formato": p.formato,
            "opcoes": p.opcoes, "pontos": p.pontos,
            "minha_resposta": minha.valor if minha else None,
            "meu_palpite": _palpite(meu_palpite),
            "gabarito_do_parceiro": gabarito_parceiro.valor if (encerrado and gabarito_parceiro) else None,
            "palpite_do_parceiro": _palpite(palpite_parceiro) if (encerrado or aguardando_minha_correcao) else None,
        })

    enviou_sobre_si, enviou_palpite = _quem_enviou(ctx, quiz, SOBRE_SI), _quem_enviou(ctx, quiz, PALPITE)
    autor = ctx.papel_de(quiz.autor_id)
    acoes = []
    if ctx.papel in regras.quem_responde_sobre_si(quiz.tipo, autor) and ctx.papel not in enviou_sobre_si \
            and quiz.status is (StatusQuiz.ABERTO if quiz.tipo.mutuo else StatusQuiz.RASCUNHO):
        acoes.append("RESPONDER_SOBRE_SI")
    if ctx.papel in regras.quem_palpita(quiz.tipo, autor) and ctx.papel not in enviou_palpite \
            and quiz.status is StatusQuiz.ABERTO:
        acoes.append("PALPITAR")
    if precisa_corrigir:
        acoes.append("CORRIGIR")

    return {
        "id": quiz.id, "tipo": quiz.tipo, "titulo": quiz.titulo, "status": quiz.status,
        "autor_id": quiz.autor_id, "semana_ref": quiz.semana_ref, "prazo": quiz.prazo,
        "percentual_sintonia": quiz.percentual_sintonia, "criado_em": quiz.criado_em,
        "encerrado_em": quiz.encerrado_em, "perguntas": perguntas,
        "eu": {"sobre_si": ctx.papel in enviou_sobre_si, "palpites": ctx.papel in enviou_palpite},
        "parceiro": {"sobre_si": ctx.papel.outro in enviou_sobre_si, "palpites": ctx.papel.outro in enviou_palpite},
        "acoes_disponiveis": acoes,
    }
