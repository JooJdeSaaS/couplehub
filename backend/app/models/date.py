from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import AmbienteDate, CategoriaDate, CustoDate

from .base import Base, EnumStr, UTCDateTime, coluna_timestamp, pk


class IdeiaDate(Base):
    """Entidade "Date". casal_id NULL = item do catálogo global (seed);
    preenchido = ideia privada do casal."""
    __tablename__ = "ideia_date"
    __table_args__ = (Index("ix_date_filtros", "ambiente", "categoria"),)

    id: Mapped[str] = pk()
    casal_id: Mapped[str | None] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"), index=True)
    criado_por_id: Mapped[str | None] = mapped_column(ForeignKey("usuario.id", ondelete="SET NULL"))
    titulo: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(500))
    ambiente: Mapped[AmbienteDate] = mapped_column(EnumStr(AmbienteDate))
    categoria: Mapped[CategoriaDate] = mapped_column(EnumStr(CategoriaDate))
    custo: Mapped[CustoDate] = mapped_column(EnumStr(CustoDate), default=CustoDate.BAIXO)
    duracao_min: Mapped[int | None] = mapped_column(Integer)
    criado_em: Mapped[datetime] = coluna_timestamp()


class DateFavorito(Base):
    """Associação N:N casal x ideia (favoritos e "já fizemos")."""
    __tablename__ = "date_favorito"

    casal_id: Mapped[str] = mapped_column(ForeignKey("casal.id", ondelete="CASCADE"), primary_key=True)
    ideia_id: Mapped[str] = mapped_column(ForeignKey("ideia_date.id", ondelete="CASCADE"), primary_key=True)
    favoritado_em: Mapped[datetime] = coluna_timestamp()
    realizado_em: Mapped[datetime | None] = mapped_column(UTCDateTime)
