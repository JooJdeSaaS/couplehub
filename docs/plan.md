# CoupleHUB — Plano técnico (plan.md)

> Como a [spec](spec.md) será implementada. Decisões detalhadas nos [ADRs](adr/).

## 1. Arquitetura

```
┌──────────── mobile (Expo Go) ────────────┐        ┌──────────────── backend (FastAPI) ─────────────────┐
│ Telas (React Navigation, abas)           │  REST  │ api/routers  → valida (Pydantic), chama serviço    │
│ AuthContext (token no SecureStore)       │ ─────▶ │ services     → orquestra, commit, pontos/créditos  │
│ api/cliente.js (fetch + erros de domínio)│        │ domain       → REGRAS PURAS (testadas sem banco)   │
│ useEventosDoCasal (WebSocket + refresh)  │ ◀───── │ models       → SQLAlchemy + CHECK/UNIQUE           │
└──────────────────────────────────────────┘   WS   │ realtime/hub → sala por casal (RNF01)              │
                                                    └──────────────────────┬─────────────────────────────┘
                                                                           │ SQLite (WAL) · respostas cifradas
```

Fluxo de uma ação: **tela** → `PUT /quizzes/{id}/palpites` → `quiz_service.enviar_palpites` → `domain.quiz.validar_envio_palpites` + `domain.pontuacao.avaliar_palpite` → commit → evento `quiz.atualizado` no WebSocket → **aparelho do parceiro** recarrega o quiz.

## 2. Mapa da API (MVP)

| Módulo | Endpoints | Requisitos |
| :--- | :--- | :--- |
| Conta | `POST /auth/cadastro`, `POST /auth/login`, `GET /auth/eu` | RF01 |
| Casal | `POST /casais`, `POST /casais/entrar`, `POST /casais/meu/novo-codigo`, `GET /casais/meu` | RF02, REQ-PAR-* |
| Quizzes | `GET/POST /quizzes`, `GET /quizzes/{id}`, `PUT …/sobre-mim`, `PUT …/palpites`, `POST …/correcoes`, `GET /quizzes/compatibilidade`, `GET /quizzes/templates/retrospectiva` | RF05, RF06, REQ-QZ/RET/PTS |
| Ranking | `GET /ranking/semanal`, `GET /ranking/mensal`, `GET /ranking/historico` | RF07, REQ-RNK |
| Vales | `GET/POST /vales`, `GET /vales/creditos`, `POST …/resgatar`, `POST …/confirmar-uso`, `DELETE /vales/{id}` | RF08, RF09, REQ-VAL/CRD |
| Decisão | `GET/POST /decisoes`, `GET /decisoes/{id}`, `PUT …/opcoes`, `POST …/cancelar` | RF03, REQ-DEC |
| Dates | `GET/POST /dates`, `GET /dates/sortear`, `PUT/DELETE …/favorito`, `PUT …/realizado` | RF04, REQ-DATE |
| Tempo real | `WS /ws?token=` | RNF01, REQ-RT |

Erros seguem um formato único: `{"erro": "SEM_CREDITO", "mensagem": "…"}` com HTTP 401/403/404/409/422.

## 3. Iterações

| Sprint | Entrega | Saída verificável |
| :--- | :--- | :--- |
| **S0 — Fundação** (esta entrega) | Estrutura do repo, modelo de domínio, spec EARS, ADRs, backend com todas as rotas do MVP, app com navegação e telas base | 51 testes de domínio verdes; Swagger abre; app conecta e pareia |
| **S1 — Quizzes ponta a ponta** | Telas de criar quiz, responder, palpitar e corrigir; retrospectiva com template | Testes de API `test_fluxos.py` verdes; demo Lucas × Beatris |
| **S2 — Gamificação** | Ranking com histórico, créditos, vales (criar/resgatar/usar) com feedback em tempo real | REQ-RNK, CRD, VAL verificados em 2 aparelhos |
| **S3 — Decisão e Dates** | Minigame com animação de roleta, catálogo com filtros, "sortear date" | REQ-DEC, REQ-DATE |
| **S4 — Qualidade** | Alembic, rate limit no login e no código de convite, acessibilidade (rótulos, contraste), testes de usabilidade com as personas (RNF04: ≤ 3 toques) | Checklist de RNF |

## 4. Estratégia de testes

- **Domínio** (`tests/dominio`): unidade, sem banco, um teste por regra; cada teste cita o `REQ-*` na docstring.
- **API** (`tests/api`): fluxos completos com `TestClient`, banco SQLite em memória e **relógio congelado** (`monkeypatch` em `app.core.relogio.agora`) para atravessar o fechamento da semana.
- **Rastreabilidade:** a matriz REQ → teste está na própria spec (coluna *Verificação*).
- **Manual:** RNF01 (2 aparelhos), RNF04 (contagem de toques), RNF05 (Android + iOS no Expo Go).

## 5. Riscos

| Risco | Mitigação |
| :--- | :--- |
| Versão do Expo SDK diferente da do Expo Go instalado no celular | Projeto no SDK 58; `npx expo install expo@^<SDK>.0.0 --fix` migra (ver `mobile/README.md`) |
| Celular não alcança a API em `localhost` | O app descobre o IP do computador pelo `hostUri` do Expo; firewall liberado na porta 8000 |
| Perder a chave de criptografia em dev | Arquivo `backend/data/.chave_dev` documentado; em produção, variável de ambiente obrigatória |
| Esquema mudar com dados reais | Adotar Alembic na S4 (ADR-0002) |
| Regras de pontuação gerarem disputa no casal | Parâmetros centralizados (spec §1.4) e "questões em aberto" (spec §11) levadas à validação com usuários |
