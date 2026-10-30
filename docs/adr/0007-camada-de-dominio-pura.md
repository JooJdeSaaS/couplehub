# ADR-0007 — Regras de negócio numa camada de domínio pura

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
As regras não triviais (match com vetos, pontuação, prazos, máquinas de estado, calendário de competição) são o que a disciplina avalia e o que mais muda durante o semestre. Se ficarem misturadas a rotas e consultas SQL, só dá para testá-las subindo banco e API.

## Decisão
Arquitetura em camadas:

```
api/routers   →  HTTP: valida entrada (Pydantic), chama serviço, publica evento
services      →  orquestra: carrega do banco, chama o domínio, grava, faz commit
domain        →  regras puras (só biblioteca padrão): recebem valores, devolvem valores ou lançam ErroDominio
models        →  mapeamento SQLAlchemy + restrições de integridade
```

`domain/` não importa FastAPI nem SQLAlchemy. Erros de domínio têm `codigo` estável e são traduzidos para HTTP num único lugar (`main.py`: 401/403/404/409/422).

## Consequências
- (+) 51 testes de regra rodam em ~0,2 s, sem banco.
- (+) Cada requisito EARS aponta para uma função pequena e para o teste que a verifica.
- (–) Um pouco mais de "cola" nos serviços (converter ORM ↔ valores).
