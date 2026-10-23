"""Pareamento do casal por código de convite (REQ-PAR-*)."""
import secrets
from datetime import datetime, timedelta

from .enums import StatusCasal
from .erros import RegraViolada, TransicaoInvalida

ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # sem 0/O, 1/I/L
TAMANHO_CODIGO = 6
VALIDADE_CONVITE = timedelta(hours=48)


def gerar_codigo() -> str:
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(TAMANHO_CODIGO))


def normalizar_codigo(codigo: str) -> str:
    return (codigo or "").strip().upper().replace("-", "").replace(" ", "")


def validar_criacao_casal(ja_tem_casal: bool) -> None:
    if ja_tem_casal:
        raise RegraViolada("Você já faz parte de um casal.", "JA_PAREADO")


def validar_entrada(
    status: StatusCasal, expira_em: datetime | None, agora: datetime,
    solicitante_ja_tem_casal: bool,
) -> None:
    if solicitante_ja_tem_casal:
        raise RegraViolada("Você já faz parte de um casal.", "JA_PAREADO")
    if status is not StatusCasal.AGUARDANDO_PARCEIRO:
        raise TransicaoInvalida("Este convite já foi usado.", "CONVITE_USADO")
    if expira_em is None or agora >= expira_em:
        raise RegraViolada("Convite expirado. Peça um novo código.", "CONVITE_EXPIRADO")
