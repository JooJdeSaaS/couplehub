# ADR-0001 — Monorepo com backend FastAPI e app Expo

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
Projeto acadêmico de Modelagem de Sistemas, equipe pequena, entrega iterativa. O app precisa rodar em Android e iOS (RNF05) e ser demonstrável sem publicar nas lojas.

## Decisão
Um único repositório com três pastas: `backend/` (Python 3.12+, FastAPI, SQLAlchemy 2), `mobile/` (React Native + Expo, executado pelo Expo Go) e `docs/` (spec, plan, tasks, ADRs, modelo de domínio). A API é REST/JSON, com documentação automática em `/docs` (Swagger), e um canal WebSocket para eventos (ADR-0006).

## Consequências
- (+) Um único lugar para requisitos, código e testes; rastreabilidade simples (IDs `REQ-*` citados nos testes).
- (+) Expo Go dispensa build nativo: basta ler o QR code.
- (–) Dois ecossistemas (pip e npm) para manter.
- (–) Expo Go aceita só as bibliotecas do SDK; módulos nativos extras exigiriam *development build*.

## Alternativas consideradas
- **Flutter + Firebase:** menos código de backend, mas esconde a modelagem relacional que a disciplina avalia.
- **Django REST:** mais "baterias inclusas", porém mais pesado e sem validação por tipos tão direta quanto Pydantic.
