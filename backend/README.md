# CoupleHUB — Backend (FastAPI)

## Rodar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: <http://localhost:8000/docs> · ReDoc: <http://localhost:8000/redoc>
- `--host 0.0.0.0` é necessário para o celular (Expo Go) alcançar a API pela rede local.
- Na primeira subida são criados `data/couplehub.db`, a chave de dev `data/.chave_dev` e o catálogo de 20 ideias de date.

### Testar no Swagger
1. `POST /auth/cadastro` duas vezes (Lucas e Beatris) e copie os tokens.
2. Clique em **Authorize**, cole o token do Lucas → `POST /casais` → anote `codigo_convite`.
3. Troque para o token da Beatris → `POST /casais/entrar` com o código.
4. Siga o fluxo: `POST /quizzes` → `PUT /quizzes/{id}/sobre-mim` (Lucas) → `PUT /quizzes/{id}/palpites` (Beatris) → `GET /ranking/semanal`.

## Testes

```bash
pytest                    # tudo
pytest tests/dominio      # só regras de negócio (sem banco, ~0,2 s)
```

`tests/api` usa SQLite em memória e congela o relógio (`app.core.relogio.agora`) para atravessar o fechamento da semana.

## Camadas

| Pasta | Papel |
| :--- | :--- |
| `app/domain/` | Regras puras (match com vetos, pontuação, prazos, máquinas de estado, calendário). Só biblioteca padrão. |
| `app/services/` | Orquestra: carrega, chama o domínio, grava, lança pontos, emite créditos, faz commit. |
| `app/models/` | SQLAlchemy 2.0 + restrições de integridade (ver `docs/modelo-dominio`). |
| `app/schemas/` | Contratos Pydantic de entrada/saída. |
| `app/api/` | Rotas, autenticação (`deps.py`) e notificação em tempo real. |
| `app/realtime/` | Hub WebSocket por casal. |
| `app/core/` | Configuração, banco, segurança (scrypt + JWT), criptografia (Fernet), relógio. |

Erros de regra viram JSON `{"erro": "<CODIGO>", "mensagem": "..."}`: 401 não autenticado · 403 sem permissão · 404 inexistente/de outro casal · 409 transição inválida · 422 regra violada.
