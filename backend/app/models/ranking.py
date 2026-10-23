from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import OrigemPontos, ResultadoPeriodo, TipoPeriodo

from .base import Base, EnumStr, coluna_timestamp, pk


class LancamentoPontos(Base):
    """Livro-razão de pontos, só de inserção (ADR-0004). É a fonte da verdade
    do ranking; a tabela `ranking` guarda apenas o placar FECHADO de cada período."""
    __tablename__ = "lancamento_pontos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "origem", "referencia_id", name="uq_lancamento_idempotente"),
        CheckConstraint("pontos >= 0", name="ck_lancamento_pontos_positivos"),
        Index("ix_lancamento_casal_semana", "casal_id", "semana_ref"),
        Index("ix_lancamento_casal_mes", "casal_id", "mes_ref"),
    )

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    pontos: Mapped[int] = mapped_column(Integer)
    origem: Mapped[OrigemPontos] = mapped_column(EnumStr(OrigemPontos))
    referencia_id: Mapped[str] = mapped_column(String(36))  # id do quiz (ou de futuro minigame)
    semana_ref: Mapped[str] = mapped_column(String(8))      # "2026-W43"
    mes_ref: Mapped[str] = mapped_column(String(7))         # "2026-10" (mês da quinta-feira da semana)
    descricao: Mapped[str] = mapped_column(String(120))
    criado_em: Mapped[datetime] = coluna_timestamp()


class Ranking(Base):
    """Placar consolidado de um período já fechado."""
    __tablename__ = "ranking"
    __table_args__ = (UniqueConstraint("casal_id", "tipo_periodo", "referencia", name="uq_ranking_periodo"),)

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    tipo_periodo: Mapped[TipoPeriodo] = mapped_column(EnumStr(TipoPeriodo))
    referencia: Mapped[str] = mapped_column(String(8))
    data_inicio: Mapped[date] = mapped_column(Date)
    data_fim: Mapped[date] = mapped_column(Date)
    pontos_a: Mapped[int] = mapped_column(Integer)
    pontos_b: Mapped[int] = mapped_column(Integer)
    resultado: Mapped[ResultadoPeriodo] = mapped_column(EnumStr(ResultadoPeriodo))
    fechado_em: Mapped[datetime] = coluna_timestamp()
