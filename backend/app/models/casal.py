from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import Papel, ProvedorAuth, StatusCasal

from .base import Base, EnumStr, UTCDateTime, coluna_timestamp, pk


class Casal(Base):
    """Raiz de agregação: tudo no app pertence a um casal (RB04)."""
    __tablename__ = "casal"

    id: Mapped[str] = pk()
    status: Mapped[StatusCasal] = mapped_column(EnumStr(StatusCasal), default=StatusCasal.AGUARDANDO_PARCEIRO)
    codigo_convite: Mapped[str | None] = mapped_column(String(8), unique=True)
    convite_expira_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
    data_inicio_relacionamento: Mapped[date | None] = mapped_column(Date)
    pareado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
    criado_em: Mapped[datetime] = coluna_timestamp()

    membros: Mapped[list["Usuario"]] = relationship(back_populates="casal", order_by="Usuario.papel")

    def membro(self, papel: Papel) -> "Usuario | None":
        return next((u for u in self.membros if u.papel == papel), None)

    def parceiro_de(self, usuario_id: str) -> "Usuario | None":
        return next((u for u in self.membros if u.id != usuario_id), None)


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("casal_id", "papel", name="uq_usuario_casal_papel"),  # no máx. 1 A e 1 B
        CheckConstraint("(casal_id IS NULL) = (papel IS NULL)", name="ck_usuario_papel_com_casal"),
    )

    id: Mapped[str] = pk()
    casal_id: Mapped[str | None] = mapped_column(ForeignKey("casal.id", ondelete="SET NULL"), index=True)
    papel: Mapped[Papel | None] = mapped_column(EnumStr(Papel))
    nome: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255))  # nulo em login social
    provedor_auth: Mapped[ProvedorAuth] = mapped_column(EnumStr(ProvedorAuth), default=ProvedorAuth.EMAIL)
    avatar_emoji: Mapped[str | None] = mapped_column(String(8))
    criado_em: Mapped[datetime] = coluna_timestamp()

    casal: Mapped[Casal | None] = relationship(back_populates="membros")
