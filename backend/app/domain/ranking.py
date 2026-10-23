"""Apuração de vencedores e emissão de créditos de vale (REQ-RNK-*, REQ-CRD-*)."""
from dataclasses import dataclass
from datetime import datetime

from .enums import Papel, ResultadoPeriodo
from .periodos import VALIDADE_CREDITO


def apurar(pontos_a: int, pontos_b: int) -> ResultadoPeriodo:
    if pontos_a == 0 and pontos_b == 0:
        return ResultadoPeriodo.SEM_DISPUTA
    if pontos_a > pontos_b:
        return ResultadoPeriodo.VITORIA_A
    if pontos_b > pontos_a:
        return ResultadoPeriodo.VITORIA_B
    return ResultadoPeriodo.EMPATE


def vencedores(resultado: ResultadoPeriodo) -> tuple[Papel, ...]:
    """Quem recebe crédito de vale. Empate com pontos: os dois recebem."""
    return {
        ResultadoPeriodo.VITORIA_A: (Papel.A,),
        ResultadoPeriodo.VITORIA_B: (Papel.B,),
        ResultadoPeriodo.EMPATE: (Papel.A, Papel.B),
        ResultadoPeriodo.SEM_DISPUTA: (),
    }[resultado]


@dataclass(frozen=True)
class Placar:
    pontos_a: int
    pontos_b: int

    @property
    def resultado(self) -> ResultadoPeriodo:
        return apurar(self.pontos_a, self.pontos_b)

    def lider(self) -> Papel | None:
        r = self.resultado
        return Papel.A if r is ResultadoPeriodo.VITORIA_A else Papel.B if r is ResultadoPeriodo.VITORIA_B else None


def validade_credito(emitido_em: datetime) -> datetime:
    return emitido_em + VALIDADE_CREDITO


def credito_vencido(expira_em: datetime, agora: datetime) -> bool:
    return agora >= expira_em
