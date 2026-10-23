from datetime import date, datetime, timezone

import pytest

from app.domain.enums import Papel
from app.domain.enums import ResultadoPeriodo as RP
from app.domain.erros import RegraViolada
from app.domain.periodos import (
    FUSO,
    fechamento_semana,
    intervalo_semana,
    mes_da_semana,
    semana_aberta_para_pontos,
    semana_do_instante,
    semanas_do_mes,
    semanas_fechaveis,
    ultima_semana_do_mes,
)
from app.domain.ranking import Placar, apurar, vencedores


def test_semana_usa_fuso_de_sao_paulo():
    """REQ-RNK-001: domingo 23:30 em SP ainda é a mesma semana, embora já seja segunda em UTC."""
    domingo_noite_sp = datetime(2026, 10, 26, 2, 30, tzinfo=timezone.utc)  # 25/10 23:30 em SP
    assert semana_do_instante(domingo_noite_sp) == "2026-W43"


def test_intervalo_e_fechamento_da_semana():
    """REQ-RNK-002"""
    assert intervalo_semana("2026-W43") == (date(2026, 10, 19), date(2026, 10, 25))
    assert fechamento_semana("2026-W43") == datetime(2026, 10, 26, 12, 0, tzinfo=FUSO)
    assert semana_aberta_para_pontos("2026-W43", datetime(2026, 10, 26, 11, 59, tzinfo=FUSO))
    assert not semana_aberta_para_pontos("2026-W43", datetime(2026, 10, 26, 12, 0, tzinfo=FUSO))


def test_semana_pertence_ao_mes_da_sua_quinta_feira():
    """REQ-RNK-006: a semana de 28/09 a 04/10/2026 tem a quinta em 01/10 -> outubro."""
    assert mes_da_semana("2026-W40") == "2026-10"
    assert semanas_do_mes("2026-10") == ["2026-W40", "2026-W41", "2026-W42", "2026-W43", "2026-W44"]
    assert ultima_semana_do_mes("2026-W44") and not ultima_semana_do_mes("2026-W43")


def test_semanas_fechaveis_param_na_semana_corrente():
    """REQ-RNK-003"""
    agora = datetime(2026, 10, 22, 14, 0, tzinfo=FUSO)  # quinta da W43
    assert semanas_fechaveis("2026-W41", agora) == ["2026-W41", "2026-W42"]


def test_referencia_invalida():
    with pytest.raises(RegraViolada):
        intervalo_semana("2026-43")
    with pytest.raises(RegraViolada):
        semanas_do_mes("2026-13")


def test_apuracao_e_vencedores():
    """REQ-RNK-004 / REQ-CRD-001"""
    assert apurar(30, 20) is RP.VITORIA_A and vencedores(RP.VITORIA_A) == (Papel.A,)
    assert apurar(10, 25) is RP.VITORIA_B
    assert apurar(15, 15) is RP.EMPATE and vencedores(RP.EMPATE) == (Papel.A, Papel.B)
    assert apurar(0, 0) is RP.SEM_DISPUTA and vencedores(RP.SEM_DISPUTA) == ()
    assert Placar(5, 3).lider() is Papel.A and Placar(4, 4).lider() is None
