#!/usr/bin/env python3
"""Cria o casal de demonstração Lucas + Beatris, com dados em todos os módulos.

O CoupleHUB não tem conta de administrador (RB04: só o casal vê os próprios
dados). Para testar tudo, use estas duas contas: entre como uma, saia e entre
como a outra (ou use dois celulares).

Uso, com a API rodando em outro terminal:
    cd backend
    python scripts/criar_demo.py                      # API em http://localhost:8000
    python scripts/criar_demo.py --api http://192.168.0.10:8000

Só usa a biblioteca padrão e a API pública (os mesmos endpoints do app), então
também funciona como teste de fumaça do backend.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

SENHA = "couplehub123"
LUCAS = {"nome": "Lucas", "email": "lucas@couplehub.dev", "senha": SENHA, "avatar_emoji": "🦊"}
BEATRIS = {"nome": "Beatris", "email": "beatris@couplehub.dev", "senha": SENHA, "avatar_emoji": "🌻"}

# urllib sem proxy: a API de desenvolvimento roda na rede local
_abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class ErroApi(Exception):
    def __init__(self, metodo: str, caminho: str, status: int, corpo):
        self.status, self.corpo = status, corpo
        super().__init__(f"{metodo} {caminho} -> HTTP {status}: {corpo}")

    @property
    def codigo(self) -> str | None:
        return self.corpo.get("erro") if isinstance(self.corpo, dict) else None


class Cliente:
    def __init__(self, base: str, token: str | None = None):
        self.base, self.token = base.rstrip("/"), token

    def _req(self, metodo: str, caminho: str, corpo=None):
        dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
        req = urllib.request.Request(self.base + caminho, data=dados, method=metodo)
        req.add_header("Content-Type", "application/json")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with _abridor.open(req, timeout=20) as resp:
                texto = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", "replace")
            try:
                conteudo = json.loads(texto)
            except ValueError:
                conteudo = texto
            raise ErroApi(metodo, caminho, e.code, conteudo) from None
        return json.loads(texto) if texto else None

    def get(self, caminho):
        return self._req("GET", caminho)

    def post(self, caminho, corpo=None):
        return self._req("POST", caminho, corpo)

    def put(self, caminho, corpo=None):
        return self._req("PUT", caminho, corpo)


def passo(texto: str) -> None:
    print(f"  • {texto}")


def aviso(texto: str) -> None:
    print(f"  ⚠ {texto}")


def entrar(api: str, pessoa: dict) -> Cliente:
    anonimo = Cliente(api)
    try:
        sessao = anonimo.post("/auth/cadastro", pessoa)
        passo(f"conta criada: {pessoa['email']}")
    except ErroApi as e:
        if e.codigo != "EMAIL_EM_USO":
            raise
        sessao = anonimo.post("/auth/login", {"email": pessoa["email"], "senha": pessoa["senha"]})
        passo(f"conta já existia, login feito: {pessoa['email']}")
    return Cliente(api, sessao["access_token"])


def responder(cli: Cliente, quiz: dict, rota: str, *valores: str) -> dict:
    """rota = 'sobre-mim' (gabarito) ou 'palpites'."""
    respostas = [{"pergunta_id": p["id"], "valor": v} for p, v in zip(quiz["perguntas"], valores, strict=True)]
    return cli.put(f"/quizzes/{quiz['id']}/{rota}", {"respostas": respostas})


def conferir(quiz: dict, esperado: str, nome: str) -> None:
    if quiz["status"] == esperado:
        passo(f"{nome}: {esperado}")
    else:
        aviso(f"{nome}: esperava {esperado}, ficou {quiz['status']}")


def parear(lucas: Cliente, beatris: Cliente) -> bool:
    """Devolve False se o casal já existia (dados de demo já criados)."""
    casal_l = lucas.get("/casais/meu")
    if casal_l and casal_l["status"] == "ATIVO":
        return False
    casal_b = beatris.get("/casais/meu")
    if casal_b and (casal_l is None or casal_b["id"] != casal_l["id"]):
        raise SystemExit("A conta da Beatris já pertence a outro casal. Apague backend/data/couplehub.db e rode de novo.")

    casal = lucas.post("/casais") if casal_l is None else lucas.post("/casais/meu/novo-codigo")
    beatris.post("/casais/entrar", {"codigo": casal["codigo_convite"]})
    passo(f"casal pareado (código {casal['codigo_convite']})")
    return True


def criar_quizzes(lucas: Cliente, beatris: Cliente) -> None:
    # 1) Sintonia que a Beatris vence -> crédito de vale para ela
    q = lucas.post("/quizzes", {
        "tipo": "SINTONIA", "titulo": "Sintonia relâmpago",
        "perguntas": [
            {"enunciado": "Praia ou montanha?", "formato": "MULTIPLA_ESCOLHA", "opcoes": ["Praia", "Montanha"]},
            {"enunciado": "Comida para pedir no domingo", "formato": "MULTIPLA_ESCOLHA",
             "opcoes": ["Pizza", "Japonesa", "Hambúrguer"]},
            {"enunciado": "Eu prefiro dormir cedo", "formato": "VERDADEIRO_FALSO"},
        ],
    })
    responder(lucas, q, "sobre-mim", "Praia", "Pizza", "FALSO")
    responder(lucas, q, "palpites", "Praia", "Japonesa", "VERDADEIRO")        # 2 de 3
    responder(beatris, q, "sobre-mim", "Montanha", "Japonesa", "VERDADEIRO")
    q = responder(beatris, q, "palpites", "Praia", "Pizza", "FALSO")           # 3 de 3 + bônus
    conferir(q, "ENCERRADO", "Sintonia relâmpago (Beatris vence e ganha crédito)")

    # 2) Sintonia que o Lucas vence -> crédito de vale para ele
    q = beatris.post("/quizzes", {
        "tipo": "SINTONIA", "titulo": "Nós dois em números",
        "perguntas": [
            {"enunciado": "De 1 a 5, quanto eu gosto de acordar cedo?", "formato": "ESCALA"},
            {"enunciado": "Meu lugar favorito para um date", "formato": "MULTIPLA_ESCOLHA",
             "opcoes": ["Cinema", "Parque", "Restaurante", "Em casa"]},
        ],
    })
    responder(beatris, q, "sobre-mim", "4", "Parque")
    responder(lucas, q, "sobre-mim", "2", "Cinema")
    responder(lucas, q, "palpites", "4", "Parque")                             # 2 de 2 + bônus
    q = responder(beatris, q, "palpites", "3", "Em casa")                      # quase + erro
    conferir(q, "ENCERRADO", "Nós dois em números (Lucas vence e ganha crédito)")

    # 3) Quiz do Lucas esperando os palpites da Beatris
    q = lucas.post("/quizzes", {
        "tipo": "PERSONALIZADO", "titulo": "Você me conhece?",
        "perguntas": [
            {"enunciado": "Qual foi nossa primeira viagem juntos?", "formato": "MULTIPLA_ESCOLHA",
             "opcoes": ["Ilhabela", "Campos do Jordão", "Paraty"]},
            {"enunciado": "Eu já chorei vendo desenho animado", "formato": "VERDADEIRO_FALSO"},
            {"enunciado": "De 1 a 5, quanto eu gosto de karaokê?", "formato": "ESCALA"},
            {"enunciado": "Qual comida eu nunca dispenso?", "formato": "TEXTO_LIVRE", "pontos": 15},
        ],
    })
    q = responder(lucas, q, "sobre-mim", "Paraty", "VERDADEIRO", "2", "Pão de queijo")
    conferir(q, "ABERTO", "Você me conhece? (Beatris precisa palpitar)")

    # 4) Quiz da Beatris com palpite de texto esperando a correção dela
    q = beatris.post("/quizzes", {
        "tipo": "PERSONALIZADO", "titulo": "Detalhes que importam",
        "perguntas": [
            {"enunciado": "Qual é a minha série de conforto?", "formato": "TEXTO_LIVRE", "pontos": 15},
            {"enunciado": "Onde foi nosso primeiro beijo?", "formato": "TEXTO_LIVRE", "pontos": 15},
            {"enunciado": "Meu doce favorito", "formato": "MULTIPLA_ESCOLHA",
             "opcoes": ["Brigadeiro", "Pudim", "Sorvete"]},
        ],
    })
    responder(beatris, q, "sobre-mim", "Gilmore Girls", "Na festa junina da faculdade", "Brigadeiro")
    q = responder(lucas, q, "palpites", "gilmore girls", "Na festa da faculdade", "Pudim")
    conferir(q, "EM_CORRECAO", "Detalhes que importam (Beatris precisa corrigir 1 palpite)")

    # 5) Retrospectiva da Beatris esperando os palpites do Lucas
    template = beatris.get("/quizzes/templates/retrospectiva")
    q = beatris.post("/quizzes", {"tipo": "RETROSPECTIVA", "titulo": "Como foi minha semana", "perguntas": template})
    valores = {
        "TEXTO_LIVRE": iter(["Apresentei o projeto de Modelagem", "Trânsito na volta do estágio", "A viagem de fim de ano"]),
        "ESCALA": iter(["4"]),
        "VERDADEIRO_FALSO": iter(["VERDADEIRO"]),
        "MULTIPLA_ESCOLHA": iter([]),
    }
    q = responder(beatris, q, "sobre-mim", *[next(valores[p["formato"]], "Sim") for p in q["perguntas"]])
    conferir(q, "ABERTO", "Retrospectiva da Beatris (Lucas precisa palpitar)")


def criar_vales(lucas: Cliente, beatris: Cliente) -> None:
    for titulo, icone in [("Vale massagem de 20 minutos", "💆"), ("Vale jantar escolhido por você", "🍝"),
                          ("Vale um dia sem celular", "📵")]:
        lucas.post("/vales", {"titulo": titulo, "icone": icone})
    for titulo, icone in [("Vale café da manhã na cama", "☕"), ("Vale escolher o filme", "🎬"),
                          ("Vale um passeio de bike", "🚲")]:
        beatris.post("/vales", {"titulo": titulo, "icone": icone})
    passo("3 vales oferecidos por cada um")


def criar_decisoes(lucas: Cliente, beatris: Cliente) -> None:
    r = lucas.post("/decisoes", {"titulo": "Jantar de sábado", "contexto": "RESTAURANTE"})
    lucas.put(f"/decisoes/{r['id']}/opcoes", {
        "preferencias": [{"rotulo": "Japonês", "peso": 5}, {"rotulo": "Pizza", "peso": 3}, {"rotulo": "Árabe", "peso": 2}],
        "vetos": ["Hambúrguer"],
    })
    passo("rodada 'Jantar de sábado': Lucas já enviou, falta a Beatris")

    r = beatris.post("/decisoes", {"titulo": "Filme de domingo", "contexto": "ROLE"})
    beatris.put(f"/decisoes/{r['id']}/opcoes", {
        "preferencias": [{"rotulo": "Comédia romântica", "peso": 5}, {"rotulo": "Suspense", "peso": 2}],
        "vetos": [],
    })
    r = lucas.put(f"/decisoes/{r['id']}/opcoes", {
        "preferencias": [{"rotulo": "Suspense", "peso": 4}, {"rotulo": "Ficção científica", "peso": 5}],
        "vetos": ["Terror"],
    })
    resultado = (r.get("resultado") or {}).get("rotulo")
    passo(f"rodada 'Filme de domingo': resolvida -> {resultado}")


def criar_dates(lucas: Cliente) -> None:
    ideias = lucas.get("/dates?ambiente=EM_CASA")
    for ideia in ideias[:2]:
        lucas.put(f"/dates/{ideia['id']}/favorito")
    if ideias:
        lucas.put(f"/dates/{ideias[0]['id']}/realizado")
    passo("2 ideias de date favoritadas, 1 marcada como feita")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api", default="http://localhost:8000", help="URL da API (padrão: %(default)s)")
    api = parser.parse_args().api.rstrip("/")

    print(f"CoupleHUB — criando dados de demonstração em {api}")
    try:
        Cliente(api).get("/saude")
    except (urllib.error.URLError, ConnectionError, TimeoutError):
        raise SystemExit(f"Não encontrei a API em {api}. Ela está rodando (uvicorn app.main:app ...)?") from None

    lucas, beatris = entrar(api, LUCAS), entrar(api, BEATRIS)
    if parear(lucas, beatris):
        criar_quizzes(lucas, beatris)
        criar_vales(lucas, beatris)
        criar_decisoes(lucas, beatris)
        criar_dates(lucas)
    else:
        passo("o casal de demonstração já existia; nada foi duplicado")
        print("    (para recriar do zero: pare a API, apague backend/data/couplehub.db, suba a API e rode de novo)")

    placar = lucas.get("/ranking/semanal")
    pontos = ", ".join(f"{p['nome']} {p['pontos']}" for p in placar["participantes"])
    creditos_l, creditos_b = len(lucas.get("/vales/creditos")), len(beatris.get("/vales/creditos"))

    print(f"""
Pronto! Entre no app com uma destas contas (senha das duas: {SENHA})
  Lucas    {LUCAS['email']}
  Beatris  {BEATRIS['email']}

Placar da semana {placar['referencia']}: {pontos}
Créditos de vale: Lucas {creditos_l} · Beatris {creditos_b}

O que dá para testar:
  como Beatris  palpitar em "Você me conhece?" · corrigir 1 palpite em "Detalhes que importam"
                enviar opções no "Jantar de sábado" · resgatar um vale do Lucas
  como Lucas    palpitar na retrospectiva da Beatris · contar a própria semana
                resgatar um vale da Beatris · ver o resultado do "Filme de domingo"
Para ver a semana fechar: reinicie a API com COUPLEHUB_AVANCAR_DIAS=7 (veja backend/README.md).""")


if __name__ == "__main__":
    try:
        main()
    except ErroApi as erro:
        sys.exit(f"\nErro da API: {erro}")
