import pytest

from app.domain.enums import FormatoPergunta as F
from app.domain.enums import ResultadoPalpite as R
from app.domain.erros import RegraViolada
from app.domain.pontuacao import (
    avaliar_palpite,
    canonizar_valor,
    consolidar,
    indice_compatibilidade,
    pontos_do_palpite,
    validar_correcao_manual,
    validar_pergunta,
)


def test_multipla_escolha_acerto_ignora_acento_e_caixa():
    """REQ-PTS-001"""
    assert avaliar_palpite(F.MULTIPLA_ESCOLHA, "Pão de queijo", "pao de QUEIJO") is R.ACERTO
    assert avaliar_palpite(F.MULTIPLA_ESCOLHA, "Pizza", "Sushi") is R.ERRO


def test_escala_vizinha_vale_parcial():
    """REQ-PTS-002"""
    assert avaliar_palpite(F.ESCALA, "4", "4") is R.ACERTO
    assert avaliar_palpite(F.ESCALA, "4", "5") is R.PARCIAL
    assert avaliar_palpite(F.ESCALA, "4", "2") is R.ERRO


def test_texto_livre_diferente_fica_pendente_para_o_dono_do_gabarito():
    """REQ-PTS-004"""
    assert avaliar_palpite(F.TEXTO_LIVRE, "Apresentei o TCC", "apresentei o tcc!") is R.ACERTO
    assert avaliar_palpite(F.TEXTO_LIVRE, "Apresentei o TCC", "Teve prova") is R.PENDENTE


def test_correcao_manual_nao_aceita_pendente():
    """REQ-PTS-005"""
    with pytest.raises(RegraViolada):
        validar_correcao_manual(R.PENDENTE)


def test_pontos_por_resultado():
    """REQ-PTS-003"""
    assert pontos_do_palpite(R.ACERTO, 10) == 10
    assert pontos_do_palpite(R.PARCIAL, 10) == 5
    assert pontos_do_palpite(R.ERRO, 10) == 0
    with pytest.raises(RegraViolada):
        pontos_do_palpite(R.PENDENTE, 10)


def test_bonus_de_20_por_cento_so_com_quiz_perfeito():
    """REQ-PTS-006"""
    perfeito = consolidar([(R.ACERTO, 10), (R.ACERTO, 20)])
    assert (perfeito.pontos_base, perfeito.bonus, perfeito.total, perfeito.percentual) == (30, 6, 36, 100.0)

    quase = consolidar([(R.ACERTO, 10), (R.PARCIAL, 10)])
    assert (quase.pontos_base, quase.bonus, quase.percentual) == (15, 0, 75.0)


def test_canonizacao_por_formato():
    """REQ-QZ-005"""
    assert canonizar_valor(F.VERDADEIRO_FALSO, "Sim") == "VERDADEIRO"
    assert canonizar_valor(F.ESCALA, " 3 ") == "3"
    assert canonizar_valor(F.MULTIPLA_ESCOLHA, "japonesa", ["Italiana", "Japonesa"]) == "Japonesa"
    with pytest.raises(RegraViolada):
        canonizar_valor(F.MULTIPLA_ESCOLHA, "Árabe", ["Italiana", "Japonesa"])
    with pytest.raises(RegraViolada):
        canonizar_valor(F.ESCALA, "6")
    with pytest.raises(RegraViolada):
        canonizar_valor(F.TEXTO_LIVRE, "   ")


def test_validacao_da_pergunta():
    """REQ-QZ-002"""
    validar_pergunta(F.MULTIPLA_ESCOLHA, ["A", "B"], 10)
    with pytest.raises(RegraViolada):
        validar_pergunta(F.MULTIPLA_ESCOLHA, ["A", "a"], 10)   # duplicada após normalizar
    with pytest.raises(RegraViolada):
        validar_pergunta(F.ESCALA, ["1", "2"], 10)            # escala não tem opções
    with pytest.raises(RegraViolada):
        validar_pergunta(F.TEXTO_LIVRE, None, 100)            # pontos fora do intervalo


def test_indice_de_compatibilidade_usa_os_ultimos_dez():
    """REQ-QZ-012"""
    assert indice_compatibilidade([]) is None
    assert indice_compatibilidade([0.0] * 5 + [100.0] * 10) == 100.0
    assert indice_compatibilidade([50.0, 100.0]) == 75.0
