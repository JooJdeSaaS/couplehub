from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ContextoDecisao, StatusDecisao, TipoResultadoDecisao

from .base import Base, EnumStr, UTCDateTime, coluna_timestamp, pk


class SessaoDecisao(Base):
    """Uma rodada do minigame "Onde vamos?"."""
    __tablename__ = "sessao_decisao"
    __table_args__ = (Index("ix_decisao_casal_status", "casal_id", "status"),)

    id: Mapped[str] = pk()
    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"))
    criado_por_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    titulo: Mapped[str] = mapped_column(String(80))
    contexto: Mapped[ContextoDecisao] = mapped_column(EnumStr(ContextoDecisao))
    status: Mapped[StatusDecisao] = mapped_column(EnumStr(StatusDecisao), default=StatusDecisao.COLETANDO)
    tipo_resultado: Mapped[TipoResultadoDecisao | None] = mapped_column(EnumStr(TipoResultadoDecisao))
    resultado_rotulo: Mapped[str | None] = mapped_column(String(60))
    favorecido_id: Mapped[str | None] = mapped_column(ForeignKey("usuario.id"))
    escolhedor_id: Mapped[str | None] = mapped_column(ForeignKey("usuario.id"))
    justificativa: Mapped[str | None] = mapped_column(String(280))
    semente: Mapped[int | None] = mapped_column(Integer)  # reproduz o sorteio (auditoria)
    criado_em: Mapped[datetime] = coluna_timestamp()
    resolvida_em: Mapped[datetime | None] = mapped_column(UTCDateTime)

    entradas: Mapped[list["EntradaDecisao"]] = relationship(back_populates="sessao", cascade="all, delete-orphan")


class EntradaDecisao(Base):
    """Preferência (com peso) ou veto, mantida em segredo até a resolução."""
    __tablename__ = "entrada_decisao"
    __table_args__ = (
        CheckConstraint("(veto = 1 AND peso IS NULL) OR (veto = 0 AND peso BETWEEN 1 AND 5)", name="ck_entrada_peso"),
        Index("ix_entrada_sessao_usuario", "sessao_id", "usuario_id"),
    )

    id: Mapped[str] = pk()
    sessao_id: Mapped[str] = mapped_column(ForeignKey("sessao_decisao.id", ondelete="CASCADE"))
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"))
    rotulo: Mapped[str] = mapped_column(String(60))
    peso: Mapped[int | None] = mapped_column(Integer)
    veto: Mapped[bool] = mapped_column(Boolean, default=False)

    sessao: Mapped[SessaoDecisao] = relationship(back_populates="entradas")
