from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, Float, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import FormatoPergunta, NaturezaResposta, ResultadoPalpite, StatusQuiz, TipoQuiz

from .base import Base, EnumStr, TextoCifrado, UTCDateTime, coluna_timestamp, pk
from .casal import Usuario


class Quiz(Base):
    """Quiz personalizado, de sintonia ou retrospectiva semanal (ADR-0003)."""
    __tablename__ = "quiz"
    __table_args__ = (
        CheckConstraint("(tipo = 'RETROSPECTIVA') = (semana_ref IS NOT NULL)", name="ck_quiz_semana_so_retrospectiva"),
        Index("uq_retrospectiva_autor_semana", "autor_id", "semana_ref", unique=True,
              sqlite_where=text("tipo = 'RETROSPECTIVA'")),
        Index("ix_quiz_casal_status", "casal_id", "status"),
    )

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    autor_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    tipo: Mapped[TipoQuiz] = mapped_column(EnumStr(TipoQuiz))
    titulo: Mapped[str] = mapped_column(String(120))
    status: Mapped[StatusQuiz] = mapped_column(EnumStr(StatusQuiz))
    semana_ref: Mapped[str | None] = mapped_column(String(8))          # "2026-W43", só retrospectiva
    prazo: Mapped[datetime | None] = mapped_column(UTCDateTime)
    percentual_sintonia: Mapped[float | None] = mapped_column(Float)   # snapshot ao encerrar
    criado_em: Mapped[datetime] = coluna_timestamp()
    publicado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
    encerrado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)

    autor: Mapped[Usuario] = relationship()
    perguntas: Mapped[list["Pergunta"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan", order_by="Pergunta.ordem"
    )


class Pergunta(Base):
    __tablename__ = "pergunta"
    __table_args__ = (
        UniqueConstraint("quiz_id", "ordem", name="uq_pergunta_ordem"),
        CheckConstraint("pontos BETWEEN 2 AND 50", name="ck_pergunta_pontos"),
    )

    id: Mapped[str] = pk()
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quiz.id", ondelete="CASCADE"))
    ordem: Mapped[int] = mapped_column(Integer)
    enunciado: Mapped[str] = mapped_column(String(280))
    formato: Mapped[FormatoPergunta] = mapped_column(EnumStr(FormatoPergunta))
    opcoes: Mapped[list[str] | None] = mapped_column(JSON)
    pontos: Mapped[int] = mapped_column(Integer, default=10)

    quiz: Mapped[Quiz] = relationship(back_populates="perguntas")
    respostas: Mapped[list["Resposta"]] = relationship(back_populates="pergunta", cascade="all, delete-orphan")


class Resposta(Base):
    """SOBRE_SI = gabarito de quem respondeu; PALPITE = tentativa sobre o parceiro."""
    __tablename__ = "resposta"
    __table_args__ = (
        UniqueConstraint("pergunta_id", "usuario_id", "natureza", name="uq_resposta_unica"),
        CheckConstraint(
            "natureza = 'PALPITE' OR (resultado IS NULL AND pontos_obtidos IS NULL)",
            name="ck_resposta_sobre_si_sem_nota",
        ),
    )

    id: Mapped[str] = pk()
    pergunta_id: Mapped[str] = mapped_column(ForeignKey("pergunta.id", ondelete="CASCADE"), index=True)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    natureza: Mapped[NaturezaResposta] = mapped_column(EnumStr(NaturezaResposta))
    valor: Mapped[str] = mapped_column(TextoCifrado)                    # cifrado em repouso (RNF02)
    resultado: Mapped[ResultadoPalpite | None] = mapped_column(EnumStr(ResultadoPalpite))
    pontos_obtidos: Mapped[int | None] = mapped_column(Integer)
    corrigida_por_id: Mapped[str | None] = mapped_column(ForeignKey("usuario.id"))
    respondida_em: Mapped[datetime] = coluna_timestamp()
    corrigida_em: Mapped[datetime | None] = mapped_column(UTCDateTime)

    pergunta: Mapped[Pergunta] = relationship(back_populates="respostas")
