# ADR-0003 — Quiz unificado: personalizado, sintonia e retrospectiva no mesmo modelo

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
O enunciado descreve três dinâmicas parecidas: quiz personalizado (RF05), quiz de sintonia em que "ambos respondem sobre si ou sobre o parceiro" e a retrospectiva semanal (RF06), em que um conta a semana e o outro adivinha. Modelar cada uma separadamente triplicaria correção, pontuação, prazos e regras de visibilidade.

## Decisão
1. Uma única hierarquia `quiz → pergunta → resposta`, com `quiz.tipo ∈ {PERSONALIZADO, SINTONIA, RETROSPECTIVA}`.
2. **O gabarito é uma resposta** de natureza `SOBRE_SI`; o palpite é uma resposta `PALPITE`. O palpite de X é comparado ao `SOBRE_SI` do parceiro de X.
3. Quiz unilateral: autor dá `SOBRE_SI`, parceiro dá `PALPITE`. Quiz mútuo (SINTONIA): os dois dão as duas.
4. Retrospectiva = quiz unilateral com `semana_ref` obrigatória, prazo no fechamento da semana e unicidade por autor/semana (índice parcial).

## Consequências
- (+) Uma só implementação de correção automática, correção manual, benefício da dúvida, prazos e visibilidade.
- (+) O modo SINTONIA não precisou de tabela nova.
- (+) A retrospectiva ganha de graça o histórico de compatibilidade.
- (–) Regras que dependem do tipo ficam em condicionais (`tipo.mutuo`, `tipo is RETROSPECTIVA`) — concentradas em `domain/quiz.py` para não se espalharem.

## Alternativas consideradas
- **Tabela `retrospectiva` + `marco_semana`:** mais explícita, mas duplicaria toda a mecânica de palpite/correção.
- **Coluna `gabarito` em `pergunta`:** simples para o modo unilateral, mas impossível para o modo SINTONIA (dois gabaritos por pergunta).
