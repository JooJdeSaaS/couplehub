import pytest

from app.domain.enums import StatusVale as V
from app.domain.erros import AcessoNegado, RegraViolada, TransicaoInvalida
from app.domain.vales import (
    LIMITE_DISPONIVEIS_POR_CRIADOR,
    validar_cancelamento,
    validar_confirmacao_uso,
    validar_criacao,
    validar_resgate,
)

BEATRIS, LUCAS = "u-beatris", "u-lucas"


def test_parceiro_com_credito_resgata_vale_disponivel():
    """REQ-VAL-004"""
    assert validar_resgate(V.DISPONIVEL, criador_id=BEATRIS, solicitante_id=LUCAS, tem_credito=True) is V.RESGATADO


def test_nao_resgata_o_proprio_vale():
    """REQ-VAL-001, REQ-VAL-005"""
    with pytest.raises(AcessoNegado):
        validar_resgate(V.DISPONIVEL, BEATRIS, BEATRIS, tem_credito=True)


def test_sem_credito_nao_resgata():
    """REQ-VAL-006"""
    with pytest.raises(RegraViolada) as erro:
        validar_resgate(V.DISPONIVEL, BEATRIS, LUCAS, tem_credito=False)
    assert erro.value.codigo == "SEM_CREDITO"


@pytest.mark.parametrize("status", [V.RESGATADO, V.UTILIZADO, V.CANCELADO])
def test_so_vale_disponivel_pode_ser_resgatado(status):
    """REQ-VAL-007"""
    with pytest.raises(TransicaoInvalida):
        validar_resgate(status, BEATRIS, LUCAS, tem_credito=True)


def test_so_quem_resgatou_confirma_uso():
    """REQ-VAL-009"""
    assert validar_confirmacao_uso(V.RESGATADO, beneficiario_id=LUCAS, solicitante_id=LUCAS) is V.UTILIZADO
    with pytest.raises(AcessoNegado):
        validar_confirmacao_uso(V.RESGATADO, beneficiario_id=LUCAS, solicitante_id=BEATRIS)
    with pytest.raises(TransicaoInvalida):
        validar_confirmacao_uso(V.DISPONIVEL, beneficiario_id=None, solicitante_id=LUCAS)


def test_cancelamento_so_pelo_criador_e_so_se_disponivel():
    """REQ-VAL-010"""
    assert validar_cancelamento(V.DISPONIVEL, BEATRIS, BEATRIS) is V.CANCELADO
    with pytest.raises(AcessoNegado):
        validar_cancelamento(V.DISPONIVEL, BEATRIS, LUCAS)
    with pytest.raises(TransicaoInvalida):
        validar_cancelamento(V.RESGATADO, BEATRIS, BEATRIS)


def test_estados_finais_nao_mudam():
    """REQ-VAL-003, REQ-VAL-011"""
    with pytest.raises(TransicaoInvalida):
        validar_confirmacao_uso(V.UTILIZADO, LUCAS, LUCAS)
    with pytest.raises(TransicaoInvalida):
        validar_cancelamento(V.CANCELADO, BEATRIS, BEATRIS)


def test_criacao_limita_titulo_e_quantidade():
    """REQ-VAL-002"""
    validar_criacao("Vale massagem de 20 min", disponiveis_do_criador=0)
    with pytest.raises(RegraViolada):
        validar_criacao("Oi", 0)
    with pytest.raises(RegraViolada):
        validar_criacao("Vale cinema", LIMITE_DISPONIVEIS_POR_CRIADOR)
