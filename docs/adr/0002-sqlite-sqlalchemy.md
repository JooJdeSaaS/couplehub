# ADR-0002 — SQLite com SQLAlchemy 2.0 (tipado)

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
Volume pequeno (um casal gera dezenas de registros por semana), necessidade de persistir estado entre sessões e de rodar em qualquer máquina de aluno sem instalar servidor de banco.

## Decisão
- SQLite em arquivo (`backend/data/couplehub.db`) com `PRAGMA foreign_keys = ON` e `journal_mode = WAL`.
- Modelos declarativos tipados (`Mapped[...]`) do SQLAlchemy 2.0; enums gravados como `VARCHAR + CHECK`.
- Regras críticas também como restrições no banco (UNIQUE, CHECK, índice parcial) — ver `modelo-dominio/README.md §4`.
- No MVP, o esquema é criado com `Base.metadata.create_all()` na subida da API. `schema.sql` documenta o DDL equivalente.

## Consequências
- (+) Zero infraestrutura; o banco é um arquivo que pode ir junto na entrega.
- (+) Trocar para PostgreSQL é mudar `COUPLEHUB_DATABASE_URL` (os modelos não usam nada exclusivo do SQLite além do `sqlite_where` do índice parcial, que tem equivalente `postgresql_where`).
- (–) SQLite serializa escritas: suficiente para o uso previsto, não para milhares de casais simultâneos.
- (–) `create_all` não altera tabelas existentes. **Próximo passo:** adotar Alembic antes da primeira mudança de esquema com dados reais.

## Alternativas consideradas
- **PostgreSQL desde o início:** mais robusto, mas exige Docker/serviço local para cada integrante.
- **SQLModel:** menos código, porém mistura modelo de banco e de API, o que atrapalha a ocultação de campos sensíveis (gabarito).
