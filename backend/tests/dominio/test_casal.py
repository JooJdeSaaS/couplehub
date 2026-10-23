from datetime import datetime, timedelta, timezone

import pytest

from app.domain.casal import (
    ALFABETO_CODIGO,
    TAMANHO_CODIGO,
    VALIDADE_CONVITE,
    gerar_codigo,
    normalizar_codigo,
    validar_criacao_casal,
    validar_entrada,
)
from app.domain.enums import StatusCasal as S
from app.domain.erros import RegraViolada, TransicaoInvalida

AGORA = datetime(2026, 10, 22, 17, 0, tzinfo=timezone.utc)


def test_codigo_de_convite():
    """REQ-PAR-001: 6 caracteres sem símbolos ambíguos; quem já tem casal não cria outro."""
    for _ in range(200):
        codigo = gerar_codigo()
        assert len(codigo) == TAMANHO_CODIGO and set(codigo) <= set(ALFABETO_CODIGO)
    assert not set("0O1IL") & set(ALFABETO_CODIGO)
    assert VALIDADE_CONVITE == timedelta(hours=48)
    with pytest.raises(RegraViolada):
        validar_criacao_casal(ja_tem_casal=True)


def test_entrada_valida():
    """REQ-PAR-002"""
    assert normalizar_codigo(" k7q-2mx ") == "K7Q2MX"
    validar_entrada(S.AGUARDANDO_PARCEIRO, AGORA + timedelta(hours=1), AGORA, solicitante_ja_tem_casal=False)


@pytest.mark.parametrize("status, expira_em, ja_tem_casal, erro", [
    (S.AGUARDANDO_PARCEIRO, AGORA, False, RegraViolada),            # expirado (limite exato)
    (S.ATIVO, AGORA + timedelta(hours=1), False, TransicaoInvalida),  # já usado
    (S.AGUARDANDO_PARCEIRO, AGORA + timedelta(hours=1), True, RegraViolada),  # já pareado
])
def test_entradas_recusadas(status, expira_em, ja_tem_casal, erro):
    """REQ-PAR-003"""
    with pytest.raises(erro):
        validar_entrada(status, expira_em, AGORA, ja_tem_casal)
