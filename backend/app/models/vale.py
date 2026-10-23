from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import OrigemCredito, StatusCredito, StatusVale

from .base import Base, EnumStr, UTCDateTime, coluna_timestamp, pk


class CreditoVale(Base):
    """Direito de resgatar UM vale, conquistado ao vencer semana, mês ou quiz de sintonia."""
    __tablename__ = "credito_vale"
    __table_args__ = (
        # idempotência: fechar a mesma semana duas vezes não gera crédito em dobro
        UniqueConstraint("usuario_id", "origem", "referencia", name="uq_credito_origem"),
        Index("ix_credito_usuario_status", "usuario_id", "status"),
    )

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    origem: Mapped[OrigemCredito] = mapped_column(EnumStr(OrigemCredito))
    referencia: Mapped[str] = mapped_column(String(40))  # "2026-W43", "2026-10" ou id do quiz
    status: Mapped[StatusCredito] = mapped_column(EnumStr(StatusCredito), default=StatusCredito.PENDENTE)
    expira_em: Mapped[datetime] = mapped_column(UTCDateTime)
    criado_em: Mapped[datetime] = coluna_timestamp()
    consumido_em: Mapped[datetime | None] = mapped_column(UTCDateTime)


class Vale(Base):
    """Oferta do criador ao parceiro. Ver máquina de estados em app/domain/vales.py."""
    __tablename__ = "vale"
    __table_args__ = (
        CheckConstraint(
            "(status IN ('DISPONIVEL', 'CANCELADO')) = (resgatado_por_id IS NULL)",
            name="ck_vale_resgate_coerente",
        ),
        CheckConstraint("resgatado_por_id IS NULL OR resgatado_por_id <> criador_id", name="ck_vale_nao_proprio"),
        Index("ix_vale_casal_status", "casal_id", "status"),
    )

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    criador_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    titulo: Mapped[str] = mapped_column(String(80))
    descricao: Mapped[str | None] = mapped_column(String(280))
    icone: Mapped[str | None] = mapped_column(String(8))
    status: Mapped[StatusVale] = mapped_column(EnumStr(StatusVale), default=StatusVale.DISPONIVEL)
    resgatado_por_id: Mapped[str | None] = mapped_column(ForeignKey("usuario.id"))
    credito_id: Mapped[str | None] = mapped_column(ForeignKey("credito_vale.id"), unique=True)
    criado_em: Mapped[datetime] = coluna_timestamp()
    resgatado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
    utilizado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
    cancelado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
