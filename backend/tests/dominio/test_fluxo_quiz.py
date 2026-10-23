from datetime import datetime, timedelta, timezone

import pytest

from app.domain.enums import FormatoPergunta as F
from app.domain.enums import Papel
from app.domain.enums import StatusQuiz as S
from app.domain.enums import TipoQuiz as T
from app.domain.erros import AcessoNegado, RegraViolada, TransicaoInvalida
from app.domain.quiz import (
    proximo_status,
    quem_palpita,
    quem_responde_sobre_si,
    status_ao_vencer_prazo,
    status_inicial,
    validar_cobertura,
    validar_envio_palpites,
    validar_envio_sobre_si,
    validar_estrutura,
)

AGORA = datetime(2026, 10, 22, 17, 0, tzinfo=timezone.utc)
A, B = Papel.A, Papel.B


def test_papeis_por_tipo():
    """REQ-QZ-001, REQ-QZ-003"""
    assert quem_responde_sobre_si(T.PERSONALIZADO, A) == {A} and quem_palpita(T.PERSONALIZADO, A) == {B}
    assert quem_responde_sobre_si(T.SINTONIA, A) == {A, B} and quem_palpita(T.SINTONIA, A) == {A, B}
    assert status_inicial(T.PERSONALIZADO) is S.RASCUNHO and status_inicial(T.SINTONIA) is S.ABERTO


def test_retrospectiva_exige_tres_perguntas():
    """REQ-RET-003"""
    duas = [(F.TEXTO_LIVRE, None, 10)] * 2
    validar_estrutura(T.PERSONALIZADO, duas)
    with pytest.raises(RegraViolada):
        validar_estrutura(T.RETROSPECTIVA, duas)


def test_fluxo_unilateral_completo():
    """REQ-QZ-004, REQ-QZ-006, REQ-QZ-008, REQ-QZ-009"""
    st = S.RASCUNHO
    validar_envio_sobre_si(T.PERSONALIZADO, st, autor=A, solicitante=A, ja_enviou=False)
    st = proximo_status(T.PERSONALIZADO, st, A, {A}, set(), 0)
    assert st is S.ABERTO

    validar_envio_palpites(T.PERSONALIZADO, st, A, B, False, AGORA, AGORA + timedelta(days=1))
    assert proximo_status(T.PERSONALIZADO, st, A, {A}, {B}, palpites_pendentes=1) is S.EM_CORRECAO
    assert proximo_status(T.PERSONALIZADO, S.EM_CORRECAO, A, {A}, {B}, 0) is S.ENCERRADO


def test_autor_nao_palpita_no_proprio_quiz_unilateral():
    """REQ-QZ-007"""
    with pytest.raises(AcessoNegado):
        validar_envio_palpites(T.PERSONALIZADO, S.ABERTO, A, A, False, AGORA, None)


def test_parceiro_nao_escreve_gabarito_do_quiz_unilateral():
    """REQ-QZ-004"""
    with pytest.raises(AcessoNegado):
        validar_envio_sobre_si(T.PERSONALIZADO, S.RASCUNHO, A, B, False)


def test_palpite_fora_do_prazo_ou_duplicado():
    """REQ-QZ-010, REQ-QZ-008"""
    with pytest.raises(TransicaoInvalida):
        validar_envio_palpites(T.PERSONALIZADO, S.ABERTO, A, B, False, AGORA, prazo=AGORA)
    with pytest.raises(TransicaoInvalida):
        validar_envio_palpites(T.PERSONALIZADO, S.ABERTO, A, B, True, AGORA, None)
    with pytest.raises(TransicaoInvalida):
        validar_envio_palpites(T.PERSONALIZADO, S.RASCUNHO, A, B, False, AGORA, None)


def test_sintonia_so_encerra_com_os_quatro_envios():
    """REQ-QZ-001"""
    st = S.ABERTO
    assert proximo_status(T.SINTONIA, st, A, {A}, {A, B}, 0) is S.ABERTO
    assert proximo_status(T.SINTONIA, st, A, {A, B}, {A}, 0) is S.ABERTO
    assert proximo_status(T.SINTONIA, st, A, {A, B}, {A, B}, 0) is S.ENCERRADO


def test_cobertura_tudo_ou_nada():
    """REQ-QZ-005"""
    validar_cobertura({"p1", "p2"}, ["p2", "p1"])
    with pytest.raises(RegraViolada):
        validar_cobertura({"p1", "p2"}, ["p1"])
    with pytest.raises(RegraViolada):
        validar_cobertura({"p1", "p2"}, ["p1", "p1", "p2"])


def test_vencimento_de_prazo():
    """REQ-QZ-011"""
    assert status_ao_vencer_prazo(S.RASCUNHO) is S.EXPIRADO
    assert status_ao_vencer_prazo(S.ABERTO) is S.EXPIRADO
    assert status_ao_vencer_prazo(S.EM_CORRECAO) is S.ENCERRADO
    assert status_ao_vencer_prazo(S.ENCERRADO) is None
