"""Fluxos ponta a ponta pela API (Quizzes -> Ranking -> Crédito -> Vale).

Cada teste cita os requisitos EARS que verifica (docs/spec.md)."""
from datetime import datetime, timezone

from app.core.database import engine

from .conftest import cadastrar, parear

FECHAMENTO_W43 = datetime(2026, 10, 26, 15, 0, 1, tzinfo=timezone.utc)  # seg 26/10 12:00:01 em SP


def _quiz_personalizado(cliente, headers):
    corpo = {
        "tipo": "PERSONALIZADO",
        "titulo": "Você me conhece?",
        "perguntas": [
            {"enunciado": "Minha culinária favorita?", "formato": "MULTIPLA_ESCOLHA",
             "opcoes": ["Japonesa", "Italiana", "Árabe"], "pontos": 10},
            {"enunciado": "Onde foi nosso primeiro encontro?", "formato": "TEXTO_LIVRE", "pontos": 10},
        ],
    }
    r = cliente.post("/quizzes", json=corpo, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def _respostas(quiz, *valores):
    return {"respostas": [{"pergunta_id": p["id"], "valor": v} for p, v in zip(quiz["perguntas"], valores, strict=True)]}


def test_fluxo_quiz_ranking_credito_vale(cliente, casal, tempo):
    """REQ-QZ-004/006/009/013, REQ-PTS-004/006, REQ-RNK-003/004/005, REQ-CRD-001, REQ-VAL-004/006/009"""
    quiz = _quiz_personalizado(cliente, casal.a)
    assert quiz["status"] == "RASCUNHO"

    quiz = cliente.put(f"/quizzes/{quiz['id']}/sobre-mim", json=_respostas(quiz, "japonesa", "Parque Ibirapuera"),
                       headers=casal.a).json()
    assert quiz["status"] == "ABERTO"

    visao_b = cliente.get(f"/quizzes/{quiz['id']}", headers=casal.b).json()
    assert "PALPITAR" in visao_b["acoes_disponiveis"]
    assert all(p["gabarito_do_parceiro"] is None for p in visao_b["perguntas"])          # REQ-QZ-013

    r = cliente.put(f"/quizzes/{quiz['id']}/palpites", json=_respostas(quiz, "Japonesa", "No Ibira"), headers=casal.b)
    assert r.json()["status"] == "EM_CORRECAO"
    palpite_texto = r.json()["perguntas"][1]["meu_palpite"]
    assert palpite_texto["resultado"] == "PENDENTE"

    r = cliente.post(f"/quizzes/{quiz['id']}/correcoes", headers=casal.b,
                     json={"correcoes": [{"resposta_id": palpite_texto["resposta_id"], "resultado": "ACERTO"}]})
    assert r.status_code == 403 and r.json()["erro"] == "AUTOCORRECAO"

    visao_a = cliente.get(f"/quizzes/{quiz['id']}", headers=casal.a).json()
    assert "CORRIGIR" in visao_a["acoes_disponiveis"]
    assert visao_a["perguntas"][1]["palpite_do_parceiro"]["valor"] == "No Ibira"

    r = cliente.post(f"/quizzes/{quiz['id']}/correcoes", headers=casal.a,
                     json={"correcoes": [{"resposta_id": palpite_texto["resposta_id"], "resultado": "ACERTO"}]})
    assert r.json()["status"] == "ENCERRADO" and r.json()["percentual_sintonia"] == 100.0

    placar = cliente.get("/ranking/semanal", headers=casal.a).json()
    pontos = {p["papel"]: p["pontos"] for p in placar["participantes"]}
    assert pontos == {"A": 0, "B": 24}                       # 20 + bônus de 20% (REQ-PTS-006)
    assert placar["fechado"] is False and placar["lider_id"] == casal.id_b

    vale = cliente.post("/vales", json={"titulo": "Vale massagem de 20 minutos", "icone": "💆"}, headers=casal.a).json()
    r = cliente.post(f"/vales/{vale['id']}/resgatar", headers=casal.b)
    assert r.status_code == 422 and r.json()["erro"] == "SEM_CREDITO"                     # REQ-VAL-006

    tempo.ir_para(FECHAMENTO_W43)
    creditos = cliente.get("/vales/creditos", headers=casal.b).json()
    assert [(c["origem"], c["referencia"]) for c in creditos] == [("VENCEDOR_SEMANA", "2026-W43")]

    r = cliente.post(f"/vales/{vale['id']}/resgatar", headers=casal.b)
    assert r.status_code == 200 and r.json()["status"] == "RESGATADO"
    assert cliente.get("/vales/creditos", headers=casal.b).json() == []                   # crédito consumido

    r = cliente.post(f"/vales/{vale['id']}/confirmar-uso", headers=casal.a)
    assert r.status_code == 403                                                          # REQ-VAL-009
    r = cliente.post(f"/vales/{vale['id']}/confirmar-uso", headers=casal.b)
    assert r.json()["status"] == "UTILIZADO"

    fechado = cliente.get("/ranking/semanal", params={"referencia": "2026-W43"}, headers=casal.a).json()
    assert fechado["fechado"] is True and fechado["resultado"] == "VITORIA_B"


def test_retrospectiva_com_correcao_pendente_vira_parcial_no_fechamento(cliente, casal, tempo):
    """REQ-RET-001/002/005, REQ-QZ-011, REQ-RNK-003/007"""
    template = cliente.get("/quizzes/templates/retrospectiva", headers=casal.b).json()
    retro = cliente.post("/quizzes", headers=casal.b,
                         json={"tipo": "RETROSPECTIVA", "titulo": "Minha semana", "perguntas": template}).json()
    assert retro["semana_ref"] == "2026-W43"

    r = cliente.post("/quizzes", headers=casal.b,
                     json={"tipo": "RETROSPECTIVA", "titulo": "De novo", "perguntas": template})
    assert r.status_code == 422 and r.json()["erro"] == "RETROSPECTIVA_JA_EXISTE"           # REQ-RET-002

    cliente.put(f"/quizzes/{retro['id']}/sobre-mim", headers=casal.b,
                json=_respostas(retro, "Apresentei meu TCC", "Trânsito", "4", "Sim", "Viagem"))
    cliente.put(f"/quizzes/{retro['id']}/palpites", headers=casal.a,
                json=_respostas(retro, "apresentei meu tcc", "O chefe", "5", "Não", "viagem!"))

    tempo.ir_para(FECHAMENTO_W43)
    placar = cliente.get("/ranking/semanal", params={"referencia": "2026-W43"}, headers=casal.a).json()
    pontos = {p["papel"]: p["pontos"] for p in placar["participantes"]}
    # Lucas: 15 (acerto) + 7 (pendente -> parcial) + 5 (escala vizinha) + 0 + 10 = 37; Beatris: 5 de participação
    assert pontos == {"A": 37, "B": 5}
    assert placar["resultado"] == "VITORIA_A"
    assert cliente.get(f"/quizzes/{retro['id']}", headers=casal.a).json()["status"] == "ENCERRADO"

    r = cliente.put(f"/quizzes/{retro['id']}/palpites", headers=casal.a, json=_respostas(retro, *["x"] * 5))
    assert r.status_code == 409                                                          # REQ-QZ-010


def test_sintonia_da_credito_ao_vencedor(cliente, casal):
    """REQ-QZ-001, REQ-CRD-002"""
    quiz = cliente.post("/quizzes", headers=casal.a, json={
        "tipo": "SINTONIA", "titulo": "Sintonia relâmpago",
        "perguntas": [{"enunciado": "Praia ou montanha?", "formato": "MULTIPLA_ESCOLHA", "opcoes": ["Praia", "Montanha"]}],
    }).json()
    assert quiz["status"] == "ABERTO"
    cliente.put(f"/quizzes/{quiz['id']}/palpites", headers=casal.a, json=_respostas(quiz, "Praia"))   # palpite antes do gabarito
    cliente.put(f"/quizzes/{quiz['id']}/sobre-mim", headers=casal.a, json=_respostas(quiz, "Montanha"))
    cliente.put(f"/quizzes/{quiz['id']}/sobre-mim", headers=casal.b, json=_respostas(quiz, "Praia"))
    final = cliente.put(f"/quizzes/{quiz['id']}/palpites", headers=casal.b, json=_respostas(quiz, "Praia")).json()

    assert final["status"] == "ENCERRADO" and final["percentual_sintonia"] == 50.0
    creditos_a = cliente.get("/vales/creditos", headers=casal.a).json()
    assert [c["origem"] for c in creditos_a] == ["VENCEDOR_QUIZ_SINTONIA"]
    assert cliente.get("/vales/creditos", headers=casal.b).json() == []


def test_privacidade_entre_casais_e_criptografia_em_repouso(cliente, casal):
    """REQ-PRV-001/002/003, REQ-PAR-001/002"""
    quiz = _quiz_personalizado(cliente, casal.a)
    cliente.put(f"/quizzes/{quiz['id']}/sobre-mim", json=_respostas(quiz, "Japonesa", "Parque Ibirapuera"),
                headers=casal.a)

    intruso = parear(cliente, "Carla", "Diego")
    assert cliente.get(f"/quizzes/{quiz['id']}", headers=intruso.a).status_code == 404
    assert cliente.get("/quizzes", headers=intruso.a).json() == []

    solteiro, _ = cadastrar(cliente, "Sozinho")
    r = cliente.get("/quizzes", headers=solteiro)
    assert r.status_code == 403 and r.json()["erro"] == "CASAL_NAO_PAREADO"

    with engine.connect() as conexao:
        valores = [linha[0] for linha in conexao.exec_driver_sql("SELECT valor FROM resposta")]
    assert valores and not any("Ibirapuera" in v for v in valores)


def test_minigame_mantem_segredo_ate_resolver(cliente, casal):
    """REQ-DEC-001/003/004"""
    rodada = cliente.post("/decisoes", headers=casal.a, json={"titulo": "Jantar de sábado"}).json()
    cliente.put(f"/decisoes/{rodada['id']}/opcoes", headers=casal.a,
                json={"preferencias": [{"rotulo": "Japonês", "peso": 5}, {"rotulo": "Pizza", "peso": 2}],
                      "vetos": ["Hambúrguer"]})
    visao_b = cliente.get(f"/decisoes/{rodada['id']}", headers=casal.b).json()
    assert visao_b["parceiro_enviou"] is True and visao_b["entradas_do_parceiro"] is None

    final = cliente.put(f"/decisoes/{rodada['id']}/opcoes", headers=casal.b,
                        json={"preferencias": [{"rotulo": "japones", "peso": 3}, {"rotulo": "Hambúrguer", "peso": 5}]}).json()
    assert final["status"] == "RESOLVIDA"
    assert final["resultado"]["tipo"] == "MATCH" and final["resultado"]["rotulo"] == "Japonês"
