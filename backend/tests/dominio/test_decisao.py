import random
from collections import Counter

import pytest

from app.domain.decisao import Preferencia as P
from app.domain.decisao import Submissao as S
from app.domain.decisao import decidir, validar_submissao
from app.domain.enums import Papel
from app.domain.enums import TipoResultadoDecisao as T
from app.domain.erros import RegraViolada


def rng(semente=42):
    return random.Random(semente)


def test_match_quando_ha_opcao_em_comum_mesmo_com_grafia_diferente():
    """REQ-DEC-004"""
    a = S((P("Japonês", 5), P("Pizza", 2)))
    b = S((P("japones ", 3), P("Hambúrguer", 5)))
    r = decidir(a, b, rng())
    assert r.tipo is T.MATCH and r.rotulo == "Japonês"


def test_veto_de_um_elimina_a_opcao_do_outro():
    """REQ-DEC-003"""
    a = S((P("Pizza", 5), P("Sushi", 1)), vetos=("Hambúrguer",))
    b = S((P("Hambúrguer", 5), P("Sushi", 1)), vetos=("Pizza",))
    r = decidir(a, b, rng())
    assert r.tipo is T.MATCH and r.rotulo == "Sushi"
    assert set(r.vetadas) == {"Pizza", "Hambúrguer"}


def test_desempate_do_match_prefere_soma_maior_e_depois_equilibrio():
    """REQ-DEC-004"""
    a = S((P("Cinema", 5), P("Boliche", 4), P("Parque", 1)))
    b = S((P("Cinema", 1), P("Boliche", 2), P("Parque", 5)))
    # somas: Cinema 6 (dif 4), Boliche 6 (dif 2), Parque 6 (dif 4) -> Boliche é o mais equilibrado
    for semente in range(20):
        assert decidir(a, b, rng(semente)).rotulo == "Boliche"


def test_sem_match_faz_sorteio_ponderado_e_informa_quem_foi_favorecido():
    """REQ-DEC-005"""
    a = S((P("Italiana", 5),))
    b = S((P("Árabe", 1),))
    contagem = Counter(decidir(a, b, rng(s)).rotulo for s in range(600))
    assert contagem["Italiana"] > contagem["Árabe"] * 3          # 5:1 esperado
    r = decidir(a, b, rng())
    assert r.tipo is T.PONDERADO and r.favorecido in (Papel.A, Papel.B)


def test_regra_de_equilibrio_reduz_chance_de_quem_venceu_o_ultimo_sorteio():
    """REQ-DEC-006"""
    a = S((P("Italiana", 3),))
    b = S((P("Árabe", 3),))
    neutro = Counter(decidir(a, b, rng(s)).favorecido for s in range(1000))
    equilibrado = Counter(decidir(a, b, rng(s), ultimo_favorecido=Papel.A).favorecido for s in range(1000))
    assert equilibrado[Papel.A] < neutro[Papel.A]
    assert 250 < equilibrado[Papel.A] < 420                       # ~1/3 esperado


def test_tudo_vetado_cai_no_cara_ou_coroa():
    """REQ-DEC-007"""
    a = S((P("Pizza", 3),), vetos=("Sushi",))
    b = S((P("Sushi", 3),), vetos=("Pizza",))
    r = decidir(a, b, rng())
    assert r.tipo is T.CARA_OU_COROA and r.rotulo is None and r.escolhedor in (Papel.A, Papel.B)


def test_mesma_semente_mesmo_resultado():
    """REQ-DEC-008"""
    a = S((P("Italiana", 2), P("Mexicana", 4)))
    b = S((P("Árabe", 3), P("Tailandesa", 1)))
    assert decidir(a, b, rng(7)) == decidir(a, b, rng(7))


@pytest.mark.parametrize("sub", [
    S(()),                                                         # nenhuma preferência
    S(tuple(P(f"Opção {i}") for i in range(6))),                   # preferências demais
    S((P("Pizza"),), vetos=("A1", "B2", "C3")),                    # vetos demais
    S((P("Pizza", 9),)),                                           # peso fora de 1..5
    S((P("Pizza"),), vetos=("pizza",)),                            # veta o que sugeriu
])
def test_submissoes_invalidas(sub):
    """REQ-DEC-002"""
    with pytest.raises(RegraViolada):
        validar_submissao(sub)
