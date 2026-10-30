# CoupleHUB — Tarefas (tasks.md)

Legenda: `[x]` feito nesta entrega · `[ ]` a fazer. Cada tarefa cita os requisitos que atende.

## S0 — Fundação
- [x] T01 Estrutura do monorepo `backend/ mobile/ docs/` — ADR-0001
- [x] T02 Modelo de domínio (13 tabelas), DDL de referência e diagrama ER — `docs/modelo-dominio/`
- [x] T03 Spec EARS do fluxo Quizzes → Pontos → Ranking → Créditos → Vales — `docs/spec.md`
- [x] T04 Camada de domínio pura + 51 testes — ADR-0007
- [x] T05 Modelos SQLAlchemy com restrições de integridade — REQ-PRV-004, REQ-PTS-007, REQ-CRD-003
- [x] T06 Autenticação (cadastro, login, JWT) e pareamento por código — RF01, RF02, REQ-PAR-001..003
- [x] T07 Criptografia de respostas em repouso — REQ-PRV-003, ADR-0005
- [x] T08 Serviços e rotas de quiz/retrospectiva/correção — REQ-QZ-*, REQ-RET-*, REQ-PTS-*
- [x] T09 Ranking com fechamento preguiçoso e créditos — REQ-RNK-*, REQ-CRD-*
- [x] T10 Vales com resgate concorrente seguro — REQ-VAL-*
- [x] T11 Minigame de decisão e catálogo de dates (backend) — REQ-DEC-*, REQ-DATE-*
- [x] T12 Canal WebSocket por casal — REQ-RT-001
- [x] T13 App Expo: navegação, login/cadastro, pareamento, Início, Quizzes, Vales, Ranking, Decisão, Dates — RNF04, RNF05
- [ ] T14 Rodar `pytest` completo (domínio + API) na máquina da equipe e registrar o resultado
- [x] T14b Script do casal de demonstração e relógio de dev (`COUPLEHUB_AVANCAR_DIAS`) para testes manuais

## S1 — Quizzes ponta a ponta
- [x] T15 Tela "Criar quiz" — versão básica (formatos, opções, pontos) — REQ-QZ-002
- [ ] T15b Editar/reordenar perguntas e pré-visualizar antes de publicar
- [x] T16 Tela única de quiz: responder sobre mim / palpitar, entrada por formato — REQ-QZ-004..006
- [x] T17 Correção de palpites (Acertou / Quase / Errou) dentro da tela do quiz — REQ-PTS-005
- [x] T18 Retrospectiva a partir do template (botão "Contar como foi minha semana") — REQ-RET-001..005
- [ ] T18b Permitir editar as perguntas do template antes de publicar — REQ-RET-004
- [ ] T19 Tela de compatibilidade (índice + histórico) — REQ-QZ-012
- [ ] T20 Lembrete de prazo (sexta à noite: "faltam X horas para fechar a semana")

## S2 — Gamificação
- [ ] T21 Histórico de ranking semanal/mensal com gráfico — REQ-RNK-005
- [ ] T22 Animação/feedback de vitória e de crédito recebido — RB03
- [ ] T23 Notificação push quando o app está fechado (Expo Push) — spec §11.4
- [ ] T24 Vale reutilizável (modelo que gera cópias) — spec §11.3

## S3 — Decisão e Dates
- [ ] T25 Animação de roleta/moeda ao resolver a rodada — REQ-DEC-005..007
- [ ] T26 Filtros combinados e busca no catálogo — REQ-DATE-002
- [ ] T27 Integração "date → decisão": abrir rodada a partir de ideias favoritas

## S4 — Qualidade e produção
- [ ] T28 Migrações Alembic — ADR-0002
- [ ] T29 Rate limit em `/auth/login` e `/casais/entrar` (força bruta do código)
- [ ] T30 Login social Google/Apple — REQ-PAR-004
- [ ] T31 Testes de usabilidade com as personas (≤ 3 toques) — RNF04
- [ ] T32 Deploy com HTTPS e monitoramento de uptime ≥ 99 % — RNF02, RNF03
