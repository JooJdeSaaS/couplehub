"""Contexto do usuário autenticado dentro do seu casal + helpers de escopo."""
from dataclasses import dataclass
from typing import TypeVar

from sqlalchemy.orm import Session

from app.domain.enums import Papel
from app.domain.erros import NaoEncontrado
from app.models import Casal, Usuario

T = TypeVar("T")


@dataclass(frozen=True)
class Contexto:
    usuario: Usuario
    casal: Casal

    @property
    def papel(self) -> Papel:
        return Papel(self.usuario.papel)

    @property
    def parceiro(self) -> Usuario:
        parceiro = self.casal.parceiro_de(self.usuario.id)
        assert parceiro is not None, "contexto só existe para casal ATIVO"
        return parceiro

    def papel_de(self, usuario_id: str) -> Papel:
        return self.papel if usuario_id == self.usuario.id else self.papel.outro

    def id_do_papel(self, papel: Papel) -> str:
        return self.usuario.id if papel == self.papel else self.parceiro.id

    def outro_id(self, usuario_id: str) -> str:
        return self.parceiro.id if usuario_id == self.usuario.id else self.usuario.id


def obter_do_casal(db: Session, modelo: type[T], id_: str, casal_id: str, nome: str = "Recurso") -> T:
    """Busca por id garantindo o escopo do casal. Recurso de OUTRO casal
    responde exatamente como inexistente (REQ-PRV-002)."""
    obj = db.get(modelo, id_)
    if obj is None or getattr(obj, "casal_id", None) != casal_id:
        raise NaoEncontrado(f"{nome} não encontrado.")
    return obj
