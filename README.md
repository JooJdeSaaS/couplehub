# CoupleHUB 💞

HUB privado de interação e gamificação para casais — projeto da disciplina de **Modelagem de Sistemas**.
Quizzes de sintonia, retrospectiva semanal, ranking, vales-recompensa, minigame "Onde vamos?" e banco de ideias de dates.

| Camada | Tecnologia |
| :--- | :--- |
| App | React Native + Expo (Expo Go), React Navigation |
| API | Python 3.11+, FastAPI, Pydantic 2, WebSocket |
| Dados | SQLite + SQLAlchemy 2.0 (respostas cifradas com Fernet) |

## Começar

```bash
# 1) API
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000     # Swagger em /docs

# 2) App (outro terminal, mesma rede Wi-Fi do celular)
cd mobile && npm install && npx expo install --fix
npx expo start                                               # leia o QR code no Expo Go
```

Detalhes em [`backend/README.md`](backend/README.md) e [`mobile/README.md`](mobile/README.md).

## Estrutura

```
couplehub/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI: rotas, CORS, tradução de erros de domínio → HTTP
│   │   ├── core/                # config, banco (SQLite/WAL), scrypt+JWT, Fernet, relógio
│   │   ├── domain/              # ★ regras puras: quiz, pontuação, períodos, ranking, vales, decisão
│   │   ├── models/              # SQLAlchemy: casal, quiz, vale, ranking, decisão, date
│   │   ├── schemas/             # contratos Pydantic de entrada/saída
│   │   ├── services/            # orquestração + transação (pontos, créditos, fechamento)
│   │   ├── api/                 # deps (auth/escopo do casal) e routers
│   │   ├── realtime/hub.py      # WebSocket por casal
│   │   └── seed/catalogo.py     # 20 ideias de date + template da retrospectiva
│   ├── tests/
│   │   ├── dominio/             # 51 testes de regra (sem banco)
│   │   └── api/                 # fluxos ponta a ponta com relógio congelado
│   └── requirements.txt
├── mobile/
│   ├── App.js                   # Login → Parear → abas (Início, Quizzes, Decidir, Dates, Vales)
│   └── src/{api,context,hooks,components,screens,theme}/
└── docs/
    ├── 00-contexto/             # visão, RB, RF, RNF e personas (originais da equipe)
    ├── spec.md                  # ★ requisitos em EARS (Quizzes → Ranking → Vales)
    ├── plan.md                  # arquitetura, mapa da API, sprints, riscos
    ├── tasks.md                 # backlog rastreado por REQ-*
    ├── modelo-dominio/          # ★ entidades, ER, invariantes, máquinas de estado, schema.sql
    ├── img/                     # diagrama ER renderizado
    └── adr/                     # 7 decisões de arquitetura
```

## Por onde ler

1. [`docs/modelo-dominio/README.md`](docs/modelo-dominio/README.md) — as tabelas e por que existem.
2. [`docs/spec.md`](docs/spec.md) — o que o sistema deve fazer, em EARS, com o teste que verifica cada requisito.
3. [`backend/app/domain/`](backend/app/domain/) — as mesmas regras, em código executável.