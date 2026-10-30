# ADR-0004 — Livro-razão de pontos e fechamento "preguiçoso" do ranking

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
O ranking semanal/mensal (RF07) define quem ganha créditos de vale (RF09). Precisamos de: placar parcial ao vivo, placar definitivo imutável, auditoria de cada ponto e nenhuma duplicação de pontos ou créditos. O backend roda num único processo e pode ficar desligado (máquina do aluno), então um agendador (cron) poderia simplesmente não disparar.

## Decisão
1. **Livro-razão** `lancamento_pontos`, só de inserção, com `UNIQUE (usuario_id, origem, referencia_id)`. Cada lançamento já carrega `semana_ref` e `mes_ref`.
2. **Placar aberto** = `SUM(pontos)` agrupado por usuário. **Placar fechado** = linha imutável em `ranking` com `UNIQUE (casal_id, tipo_periodo, referencia)`.
3. **Fechamento preguiçoso:** toda consulta de ranking ou de créditos chama `fechar_periodos_pendentes()`, que (a) aplica prazos vencidos dos quizzes, (b) fecha cada semana cujo fechamento (segunda 12:00) já passou, (c) fecha o mês quando fecha sua última semana, (d) emite créditos e (e) expira créditos vencidos. Tudo idempotente; corrida entre duas requisições é resolvida pelo UNIQUE + rollback.

## Consequências
- (+) Não depende de cron nem de o servidor estar ligado no horário exato.
- (+) "De onde vieram meus pontos?" é uma consulta simples; o ranking pode ser reconstruído do zero.
- (–) Um GET pode escrever no banco (fechamento). Aceitável e documentado.
- (–) Se ninguém abrir o app, o crédito só aparece na próxima abertura — o que é exatamente quando ele seria visto.

## Alternativas consideradas
- **Contador de pontos em `usuario`:** simples, mas sem histórico, sujeito a corrida e impossível de separar por semana.
- **APScheduler/cron:** fechamento pontual, mas frágil em ambiente acadêmico e duplicaria lógica em caso de falha.
