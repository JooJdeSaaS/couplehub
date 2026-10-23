"""Calendário de competição: semanas ISO e meses (REQ-RNK-*).

Regras:
- A semana vai de segunda 00:00 a domingo 23:59 no fuso America/Sao_Paulo.
- A semana W é FECHADA na segunda-feira seguinte às 12:00 (janela de carência
  para palpites e correções de última hora da retrospectiva).
- Uma semana pertence ao mês que contém a sua quinta-feira (convenção ISO-8601).
  Assim cada semana cai em exatamente um mês e o total mensal é sempre a soma
  exata dos totais semanais.
"""
import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .erros import RegraViolada

FUSO = ZoneInfo("America/Sao_Paulo")
HORA_FECHAMENTO = time(12, 0)
VALIDADE_CREDITO = timedelta(days=30)

_RE_SEMANA = re.compile(r"^(\d{4})-W(\d{2})$")
_RE_MES = re.compile(r"^(\d{4})-(\d{2})$")


def _exigir_fuso(instante: datetime) -> None:
    if instante.tzinfo is None:
        raise ValueError("datetime sem fuso horário")


def data_local(instante: datetime) -> date:
    _exigir_fuso(instante)
    return instante.astimezone(FUSO).date()


# --- Semanas -----------------------------------------------------------------
def semana_ref(dia: date) -> str:
    ano, semana, _ = dia.isocalendar()
    return f"{ano}-W{semana:02d}"


def semana_do_instante(instante: datetime) -> str:
    return semana_ref(data_local(instante))


def _partes_semana(ref: str) -> tuple[int, int]:
    m = _RE_SEMANA.match(ref or "")
    if not m:
        raise RegraViolada(f"Semana inválida: {ref!r} (use AAAA-Www).", "PERIODO_INVALIDO")
    ano, semana = int(m[1]), int(m[2])
    try:
        date.fromisocalendar(ano, semana, 1)
    except ValueError:
        raise RegraViolada(f"Semana inexistente: {ref!r}.", "PERIODO_INVALIDO") from None
    return ano, semana


def intervalo_semana(ref: str) -> tuple[date, date]:
    ano, semana = _partes_semana(ref)
    inicio = date.fromisocalendar(ano, semana, 1)
    return inicio, inicio + timedelta(days=6)


def semana_seguinte(ref: str) -> str:
    inicio, _ = intervalo_semana(ref)
    return semana_ref(inicio + timedelta(days=7))


def fechamento_semana(ref: str) -> datetime:
    """Instante (com fuso) em que a semana `ref` deixa de aceitar pontos."""
    _, fim = intervalo_semana(ref)
    return datetime.combine(fim + timedelta(days=1), HORA_FECHAMENTO, tzinfo=FUSO)


def semana_aberta_para_pontos(ref: str, agora: datetime) -> bool:
    _exigir_fuso(agora)
    return agora < fechamento_semana(ref)


def semanas_fechaveis(desde_ref: str, agora: datetime) -> list[str]:
    """Semanas a partir de `desde_ref` (inclusive) cujo fechamento já passou."""
    _exigir_fuso(agora)
    resultado, ref = [], desde_ref
    while fechamento_semana(ref) <= agora:
        resultado.append(ref)
        ref = semana_seguinte(ref)
    return resultado


# --- Meses -------------------------------------------------------------------
def mes_ref(dia: date) -> str:
    return f"{dia.year:04d}-{dia.month:02d}"


def mes_da_semana(ref: str) -> str:
    ano, semana = _partes_semana(ref)
    return mes_ref(date.fromisocalendar(ano, semana, 4))


def semanas_do_mes(ref_mes: str) -> list[str]:
    m = _RE_MES.match(ref_mes or "")
    if not m or not 1 <= int(m[2]) <= 12:
        raise RegraViolada(f"Mês inválido: {ref_mes!r} (use AAAA-MM).", "PERIODO_INVALIDO")
    ano, mes = int(m[1]), int(m[2])
    dia = date(ano, mes, 1)
    while dia.weekday() != 3:  # primeira quinta-feira
        dia += timedelta(days=1)
    semanas = []
    while dia.month == mes:
        semanas.append(semana_ref(dia))
        dia += timedelta(days=7)
    return semanas


def intervalo_mes(ref_mes: str) -> tuple[date, date]:
    semanas = semanas_do_mes(ref_mes)
    return intervalo_semana(semanas[0])[0], intervalo_semana(semanas[-1])[1]


def ultima_semana_do_mes(ref: str) -> bool:
    """True se fechar a semana `ref` também fecha o mês dela."""
    return mes_da_semana(ref) != mes_da_semana(semana_seguinte(ref))
