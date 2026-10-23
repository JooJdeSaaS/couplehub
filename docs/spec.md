# CoupleHUB — Especificação de Requisitos (EARS)

> **Status:** rascunho v0.1 · **Foco:** fluxo principal de **Quizzes → Pontos → Ranking → Créditos → Vales**
> **Fontes:** `00-contexto/visao.md`, `RB.md`, `RF.md`, `RNF.md`, personas Lucas e Beatris
> **Implementação de referência:** `backend/app/domain` (regras) e `backend/app/services` (orquestração)

---

## 1. Convenções

### 1.1 Padrões EARS usados

| Padrão | Gabarito em português | Quando usar |
| :--- | :--- | :--- |
| **Ubíquo** | O sistema deve `<resposta>`. | Regra sempre válida, sem gatilho. |
| **Evento** | **Quando** `<gatilho>`, o sistema deve `<resposta>`. | Reação a uma ação ou a um instante. |
| **Estado** | **Enquanto** `<estado>`, o sistema deve `<resposta>`. | Comportamento que vale durante um estado. |
| **Indesejado** | **Se** `<condição indesejada>`, **então** o sistema deve `<resposta>`. | Erros, abusos, entradas inválidas. |
| **Opcional** | **Onde** `<funcionalidade presente>`, o sistema deve `<resposta>`. | Variações configuráveis. |
| **Complexo** | **Enquanto** `<estado>`, **quando** `<gatilho>`, o sistema deve `<resposta>`. | Combinação dos anteriores. |

### 1.2 Identificadores

`REQ-<MÓDULO>-<nº>`. Módulos: **QZ** quiz · **RET** retrospectiva · **PTS** pontuação · **RNK** ranking · **CRD** créditos · **VAL** vales · **PRV** privacidade · **RT** tempo real · **PAR** pareamento · **DEC** minigame de decisão · **DATE** ideias de dates.

A coluna **Verificação** aponta o teste automatizado (`backend/tests/…`) ou `inspeção` quando a verificação é manual. Os códigos entre parênteses — p.ex. `(SEM_CREDITO)` — são os valores do campo `erro` que a API devolve.

### 1.3 Glossário

| Termo | Definição |
| :--- | :--- |
| **Parceiro A / B** | Os dois membros do casal. A criou o HUB; B entrou pelo convite. Permissões simétricas. |
| **Gabarito** | Respostas que um parceiro dá **sobre si** (`SOBRE_SI`). |
| **Palpite** | Tentativa de adivinhar o gabarito do outro (`PALPITE`). |
| **Dono do gabarito** | Quem respondeu sobre si; é quem corrige palpites de texto livre sobre ele. |
| **Quiz unilateral** | PERSONALIZADO ou RETROSPECTIVA: um gabarito (autor) e um palpiteiro (parceiro). |
| **Quiz mútuo** | SINTONIA: os dois respondem sobre si **e** palpitam sobre o outro. |
| **Semana de competição** | Semana ISO de segunda 00:00 a domingo 23:59, fuso `America/Sao_Paulo`. |
| **Fechamento** | Momento em que um período deixa de aceitar pontos e seu placar vira definitivo. |
| **Livro-razão** | Tabela `lancamento_pontos`: registro só de inserção de cada ganho de pontos. |
| **Crédito de vale** | Direito de resgatar **um** vale, conquistado ao vencer semana, mês ou quiz de sintonia. |
| **Benefício da dúvida** | Palpite não corrigido até o prazo vale PARCIAL (metade dos pontos). |

### 1.4 Parâmetros de negócio

Valores iniciais, centralizados como constantes em `backend/app/domain/*.py` para facilitar ajuste.

| Parâmetro | Valor | Constante |
| :--- | :--- | :--- |
| Perguntas por quiz | 1–15 (retrospectiva: 3–15) | `quiz.MIN_PERGUNTAS`, `MAX_PERGUNTAS` |
| Pontos por pergunta | 2–50 (padrão 10) | `pontuacao.PONTOS_*` |
| Opções em múltipla escolha | 2–6, distintas | `pontuacao.MIN_OPCOES`, `MAX_OPCOES` |
| Prazo de palpites (personalizado/sintonia) | 7 dias após a publicação | `quiz.PRAZO_PADRAO` |
| Bônus por quiz perfeito | +20 % dos pontos base | `pontuacao.FATOR_BONUS_PERFEITO` |
| Participação na retrospectiva | 5 pontos | `pontuacao.PONTOS_PARTICIPACAO_RETROSPECTIVA` |
| Fechamento da semana | segunda-feira seguinte, 12:00 (SP) | `periodos.HORA_FECHAMENTO` |
| Validade do crédito de vale | 30 dias | `periodos.VALIDADE_CREDITO` |
| Vales disponíveis por criador | até 20 | `vales.LIMITE_DISPONIVEIS_POR_CRIADOR` |
| Janela do índice de compatibilidade | últimos 10 quizzes | `pontuacao.JANELA_COMPATIBILIDADE` |

---

## 2. Quizzes (RF05) — fluxo principal

### 2.1 Visão do fluxo

```
            autor registra gabarito          todos palpitaram
 RASCUNHO ─────────────────────────▶ ABERTO ─────────────────────▶ ENCERRADO ──▶ pontos no ranking
    │                                  │  │                            ▲
    │ prazo vencido                    │  └─ há texto livre pendente ─▶ EM_CORRECAO
    ▼                                  ▼                                 │ dono corrige / prazo vence
 EXPIRADO ◀──────── prazo vencido sem todos os envios                    └──────────────────────┘
```

SINTONIA nasce em ABERTO (não há rascunho: cada um registra o próprio gabarito enquanto o quiz está aberto).

### 2.2 Requisitos

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-QZ-001 | Ubíquo | O sistema deve suportar três tipos de quiz: **PERSONALIZADO** e **RETROSPECTIVA**, nos quais o autor responde sobre si e o parceiro palpita, e **SINTONIA**, no qual cada parceiro responde sobre si e palpita sobre o outro. | RF05, RF06 | `dominio/test_fluxo_quiz::test_papeis_por_tipo`, `api/test_fluxos::test_sintonia_da_credito_ao_vencedor` |
| REQ-QZ-002 | Evento | **Quando** um parceiro criar um quiz, o sistema deve exigir de 1 a 15 perguntas, cada uma com formato (múltipla escolha, verdadeiro/falso, escala 1–5 ou texto livre) e valor de 2 a 50 pontos, e, para múltipla escolha, de 2 a 6 opções distintas. | RF05 | `dominio/test_pontuacao::test_validacao_da_pergunta` |
| REQ-QZ-003 | Evento | **Quando** um quiz PERSONALIZADO ou RETROSPECTIVA for criado, o sistema deve colocá-lo em RASCUNHO; **quando** um quiz SINTONIA for criado, o sistema deve colocá-lo em ABERTO com prazo de 7 dias. | RF05 | `dominio/test_fluxo_quiz::test_papeis_por_tipo` |
| REQ-QZ-004 | Estado | **Enquanto** um quiz unilateral estiver em RASCUNHO, o sistema deve permitir que apenas o autor registre o gabarito. | RF05 | `dominio/test_fluxo_quiz::test_parceiro_nao_escreve_gabarito_do_quiz_unilateral` |
| REQ-QZ-005 | Evento | **Quando** um parceiro enviar gabarito ou palpites, o sistema deve exigir exatamente uma resposta por pergunta, validá-la conforme o formato e armazená-la em forma canônica (p.ex. "sim" → `VERDADEIRO`). | RF05 | `dominio/test_fluxo_quiz::test_cobertura_tudo_ou_nada`, `dominio/test_pontuacao::test_canonizacao_por_formato` |
| REQ-QZ-006 | Evento | **Quando** o autor registrar o gabarito de um quiz unilateral, o sistema deve mudar o quiz para ABERTO e, se for PERSONALIZADO, fixar o prazo de palpites em 7 dias a partir desse momento. | RF05 | `dominio/test_fluxo_quiz::test_fluxo_unilateral_completo` |
| REQ-QZ-007 | Indesejado | **Se** um parceiro tentar palpitar sobre o próprio gabarito, **então** o sistema deve recusar o envio (`PALPITE_PROPRIO`). | RB01 | `dominio/test_fluxo_quiz::test_autor_nao_palpita_no_proprio_quiz_unilateral` |
| REQ-QZ-008 | Indesejado | **Se** um parceiro tentar reenviar um gabarito ou palpites já enviados, **então** o sistema deve recusar o envio (`ENVIO_DUPLICADO`), pois envios são definitivos. | RB03 | `dominio/test_fluxo_quiz::test_palpite_fora_do_prazo_ou_duplicado` |
| REQ-QZ-009 | Evento | **Quando** todos os envios esperados existirem, o sistema deve encerrar o quiz (ENCERRADO) se não houver palpite pendente de correção, ou movê-lo para EM_CORRECAO se houver. | RF05, RF07 | `dominio/test_fluxo_quiz::test_fluxo_unilateral_completo`, `api/test_fluxos::test_fluxo_quiz_ranking_credito_vale` |
| REQ-QZ-010 | Indesejado | **Se** um palpite chegar com o quiz fora de ABERTO ou após o prazo, **então** o sistema deve recusá-lo (`QUIZ_FECHADO` / `PRAZO_ENCERRADO`). | RF06 | `dominio/test_fluxo_quiz::test_palpite_fora_do_prazo_ou_duplicado`, `api/test_fluxos::test_retrospectiva_…` |
| REQ-QZ-011 | Evento | **Quando** o prazo de um quiz vencer, o sistema deve marcar como EXPIRADO, sem pontos, o quiz que estiver em RASCUNHO ou ABERTO, e deve converter em PARCIAL os palpites ainda pendentes de um quiz EM_CORRECAO e encerrá-lo. | RF06 | `dominio/test_fluxo_quiz::test_vencimento_de_prazo`, `api/test_fluxos::test_retrospectiva_…` |
| REQ-QZ-012 | Ubíquo | O sistema deve manter o histórico de compatibilidade do casal, com o percentual de acerto de cada quiz encerrado e um índice igual à média dos últimos 10 quizzes. | RB01 | `dominio/test_pontuacao::test_indice_de_compatibilidade_usa_os_ultimos_dez` |
| REQ-QZ-013 | Estado | **Enquanto** um quiz não estiver ENCERRADO, o sistema deve ocultar de cada parceiro o gabarito e os palpites do outro, exceto os palpites que aguardam a correção do próprio usuário. | RB04 | `api/test_fluxos::test_fluxo_quiz_ranking_credito_vale` |

---

## 3. Retrospectiva semanal — "Como foi sua semana?" (RF06)

Cada parceiro conta a própria semana (gabarito) e o outro tenta adivinhar. É um quiz do tipo RETROSPECTIVA, então herda todos os REQ-QZ.

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-RET-001 | Evento | **Quando** um parceiro criar sua retrospectiva, o sistema deve vinculá-la à semana de competição corrente e definir como prazo o fechamento dessa semana. | RF06 | `api/test_fluxos::test_retrospectiva_…` |
| REQ-RET-002 | Indesejado | **Se** o parceiro já tiver criado a retrospectiva da semana corrente, **então** o sistema deve recusar a nova criação (`RETROSPECTIVA_JA_EXISTE`). | RF06 | `api/test_fluxos::test_retrospectiva_…` + índice único `uq_retrospectiva_autor_semana` |
| REQ-RET-003 | Ubíquo | A retrospectiva deve ter no mínimo 3 perguntas. | RF06 | `dominio/test_fluxo_quiz::test_retrospectiva_exige_tres_perguntas` |
| REQ-RET-004 | Opcional | **Onde** o template de retrospectiva estiver habilitado, o sistema deve oferecer perguntas sugeridas e editáveis (melhor momento, maior estresse, nota da semana…). | RNF04 | inspeção (`GET /quizzes/templates/retrospectiva`) |
| REQ-RET-005 | Evento | **Quando** o autor publicar sua retrospectiva, o sistema deve lançar 5 pontos de participação para ele na semana da retrospectiva. | RB03 | `api/test_fluxos::test_retrospectiva_…` |

---

## 4. Pontuação

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-PTS-001 | Evento | **Quando** um palpite de múltipla escolha ou verdadeiro/falso for registrado e o gabarito existir, o sistema deve corrigi-lo automaticamente, ignorando maiúsculas, acentos e pontuação. | RF07 | `dominio/test_pontuacao::test_multipla_escolha_…` |
| REQ-PTS-002 | Evento | **Quando** um palpite de escala for registrado, o sistema deve classificá-lo como ACERTO se igual ao gabarito, PARCIAL se a diferença for 1 e ERRO nos demais casos. | RF07 | `dominio/test_pontuacao::test_escala_vizinha_vale_parcial` |
| REQ-PTS-003 | Ubíquo | O sistema deve atribuir 100 % dos pontos da pergunta ao ACERTO, 50 % (arredondado para baixo) ao PARCIAL e 0 ao ERRO. | RF07 | `dominio/test_pontuacao::test_pontos_por_resultado` |
| REQ-PTS-004 | Evento | **Quando** um palpite de texto livre for registrado, o sistema deve marcá-lo como ACERTO se for igual ao gabarito após normalização, ou como PENDENTE para correção do dono do gabarito. | RB01 | `dominio/test_pontuacao::test_texto_livre_…`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-PTS-005 | Evento | **Quando** o dono do gabarito corrigir um palpite PENDENTE, o sistema deve aceitar apenas ACERTO, PARCIAL ou ERRO e registrar quem corrigiu e quando. **Se** quem palpitou tentar corrigir o próprio palpite, **então** o sistema deve recusar (`AUTOCORRECAO`). | RB01 | `dominio/test_pontuacao::test_correcao_manual_nao_aceita_pendente`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-PTS-006 | Evento | **Quando** um quiz for encerrado, o sistema deve lançar os pontos de cada palpiteiro no livro-razão e, se ele tiver acertado todas as perguntas, um bônus de 20 % sobre os pontos base. | RF07, RB03 | `dominio/test_pontuacao::test_bonus_…`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-PTS-007 | Ubíquo | O lançamento de pontos deve ser idempotente por (usuário, origem, quiz): reprocessar um encerramento não deve duplicar pontos. | RF07 | inspeção + `uq_lancamento_idempotente` |

---

## 5. Ranking semanal e mensal (RF07)

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-RNK-001 | Ubíquo | O sistema deve calcular a semana de competição pelo calendário ISO no fuso `America/Sao_Paulo`. | RF07 | `dominio/test_periodos_e_ranking::test_semana_usa_fuso_de_sao_paulo` |
| REQ-RNK-002 | Estado | **Enquanto** não chegar segunda-feira 12:00 seguinte ao fim da semana, o sistema deve manter a semana aberta para pontos (janela de carência para palpites e correções de domingo à noite). | RF06, RF07 | `dominio/test_periodos_e_ranking::test_intervalo_e_fechamento_da_semana` |
| REQ-RNK-003 | Evento | **Quando** ocorrer uma consulta de ranking ou de créditos após o fechamento de uma ou mais semanas, o sistema deve, uma única vez por semana: aplicar os prazos vencidos dos quizzes, totalizar os pontos e gravar o placar definitivo. | RF07 | `dominio/test_periodos_e_ranking::test_semanas_fechaveis_…`, `api/test_fluxos::*` |
| REQ-RNK-004 | Ubíquo | O sistema deve declarar vencedor quem tiver mais pontos no período, EMPATE quando os dois tiverem a mesma pontuação maior que zero e SEM_DISPUTA quando ninguém pontuar. | RF07 | `dominio/test_periodos_e_ranking::test_apuracao_e_vencedores` |
| REQ-RNK-005 | Estado | **Enquanto** um período estiver aberto, o sistema deve exibir o placar parcial atualizado, o líder e o horário de fechamento. | RB03 | `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-RNK-006 | Ubíquo | O sistema deve compor o ranking mensal com as semanas cuja quinta-feira cai no mês e fechá-lo junto com a última dessas semanas. | RF07 | `dominio/test_periodos_e_ranking::test_semana_pertence_ao_mes_…` |
| REQ-RNK-007 | Ubíquo | O sistema deve atribuir os pontos de uma retrospectiva à semana dela, e os pontos dos demais quizzes à semana em que foram encerrados (ou do prazo, quando encerrados por vencimento). | RF07 | `api/test_fluxos::test_retrospectiva_…` |

---

## 6. Créditos de vale

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-CRD-001 | Evento | **Quando** uma semana ou um mês for fechado, o sistema deve emitir um crédito de vale para cada vencedor do período (os dois em EMPATE, nenhum em SEM_DISPUTA). | RF09 | `dominio/test_periodos_e_ranking::test_apuracao_e_vencedores`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-CRD-002 | Evento | **Quando** um quiz SINTONIA for encerrado, o sistema deve emitir um crédito de vale para o parceiro com mais pontos no quiz (os dois em caso de empate com pontos). | RF09 | `api/test_fluxos::test_sintonia_da_credito_ao_vencedor` |
| REQ-CRD-003 | Ubíquo | Cada crédito deve valer 30 dias e ser emitido no máximo uma vez por (usuário, origem, referência). | RB03 | inspeção + `uq_credito_origem` |
| REQ-CRD-004 | Evento | **Quando** um crédito atingir a validade sem ter sido usado, o sistema deve marcá-lo como EXPIRADO. | RB03 | inspeção (`pontos_service.expirar_creditos`) |

---

## 7. Vales (RF08, RF09) — fluxo principal

### 7.1 Ciclo de vida

```
              resgatar (parceiro do criador, consome 1 crédito)            confirmar uso (quem resgatou)
 DISPONIVEL ───────────────────────────────────────────────▶ RESGATADO ─────────────────────────────▶ UTILIZADO
     │
     └── cancelar (criador) ──▶ CANCELADO                         UTILIZADO e CANCELADO são finais
```

Um vale é uma **oferta**: o "Vale massagem de 20 min" criado pela Beatris só pode ser resgatado pelo Lucas, e quem cumpre é a Beatris. Assim cada parceiro monta o seu "cardápio" de mimos e o vencedor escolhe do cardápio do outro.

### 7.2 Requisitos

| ID | Tipo | Requisito | Origem | Verificação |
| :--- | :--- | :--- | :--- | :--- |
| REQ-VAL-001 | Ubíquo | O sistema deve tratar cada vale como uma oferta do criador ao parceiro: só o parceiro pode resgatá-lo e cabe ao criador cumpri-lo. | RF08 | `dominio/test_vales::test_nao_resgata_o_proprio_vale` |
| REQ-VAL-002 | Evento | **Quando** um parceiro criar um vale, o sistema deve exigir título de 3 a 80 caracteres e limitar a 20 os vales DISPONIVEIS de cada criador. | RF08 | `dominio/test_vales::test_criacao_limita_titulo_e_quantidade` |
| REQ-VAL-003 | Ubíquo | O sistema deve permitir apenas as transições DISPONIVEL→RESGATADO, RESGATADO→UTILIZADO e DISPONIVEL→CANCELADO. | RF09 | `dominio/test_vales::*` + `ck_vale_resgate_coerente` |
| REQ-VAL-004 | Evento | **Quando** o parceiro com crédito pendente resgatar um vale DISPONIVEL, o sistema deve mudar o vale para RESGATADO, consumir o crédito que vence primeiro e vinculá-lo ao vale. | RF09 | `dominio/test_vales::test_parceiro_com_credito_…`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-VAL-005 | Indesejado | **Se** o criador tentar resgatar o próprio vale, **então** o sistema deve recusar (`VALE_PROPRIO`). | RF09 | `dominio/test_vales::test_nao_resgata_o_proprio_vale` + `ck_vale_nao_proprio` |
| REQ-VAL-006 | Indesejado | **Se** o parceiro tentar resgatar sem crédito pendente, **então** o sistema deve recusar (`SEM_CREDITO`) e informar como conquistar um crédito. | RF09 | `dominio/test_vales::test_sem_credito_nao_resgata`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-VAL-007 | Indesejado | **Se** o vale não estiver DISPONIVEL no momento do resgate, **então** o sistema deve recusar (`TRANSICAO_INVALIDA`). | RF09 | `dominio/test_vales::test_so_vale_disponivel_pode_ser_resgatado` |
| REQ-VAL-008 | Complexo | **Quando** um vale for resgatado, o sistema deve notificar o criador em até 2 s e, **se** dois resgates do mesmo vale chegarem ao mesmo tempo, **então** deve aceitar apenas um (`CONCORRENCIA`). | RF09, RNF01 | inspeção (evento `vale.resgatado`; `UPDATE … WHERE status='DISPONIVEL'`) |
| REQ-VAL-009 | Evento | **Quando** quem resgatou confirmar que o vale foi cumprido, o sistema deve marcá-lo como UTILIZADO. **Se** outra pessoa tentar confirmar, **então** o sistema deve recusar (`NAO_BENEFICIARIO`). | RF09 | `dominio/test_vales::test_so_quem_resgatou_confirma_uso`, `api/test_fluxos::test_fluxo_quiz_…` |
| REQ-VAL-010 | Evento | **Quando** o criador cancelar um vale DISPONIVEL, o sistema deve marcá-lo como CANCELADO. **Se** outra pessoa tentar cancelar, ou o vale não estiver DISPONIVEL, **então** o sistema deve recusar. | RF08 | `dominio/test_vales::test_cancelamento_…` |
| REQ-VAL-011 | Ubíquo | O sistema deve tratar UTILIZADO e CANCELADO como estados finais. | RF09 | `dominio/test_vales::test_estados_finais_nao_mudam` |

---

## 8. Requisitos transversais

### 8.1 Privacidade (RB04, RNF02)

| ID | Tipo | Requisito | Verificação |
| :--- | :--- | :--- | :--- |
| REQ-PRV-001 | Estado | **Enquanto** o usuário não pertencer a um casal ATIVO, o sistema deve bloquear quizzes, vales, ranking, decisões e dates (`CASAL_NAO_PAREADO`). | `api/test_fluxos::test_privacidade_…` |
| REQ-PRV-002 | Indesejado | **Se** um usuário pedir um recurso de outro casal, **então** o sistema deve responder exatamente como se o recurso não existisse (HTTP 404). | `api/test_fluxos::test_privacidade_…` |
| REQ-PRV-003 | Ubíquo | O sistema deve cifrar em repouso o conteúdo das respostas de quiz e, em produção, trafegar apenas por HTTPS/TLS. | `api/test_fluxos::test_privacidade_…` (cifra) · inspeção (TLS) |
| REQ-PRV-004 | Ubíquo | O sistema deve usar identificadores não sequenciais (UUID v4) para todos os recursos. | inspeção |

### 8.2 Tempo real (RNF01)

| ID | Tipo | Requisito | Verificação |
| :--- | :--- | :--- | :--- |
| REQ-RT-001 | Evento | **Quando** um quiz, vale ou rodada de decisão mudar de estado, o sistema deve publicar o evento no canal WebSocket do casal em até 2 s. | inspeção / teste manual com 2 aparelhos |
| REQ-RT-002 | Indesejado | **Se** o canal WebSocket estiver indisponível, **então** o app deve recarregar os dados ao voltar ao primeiro plano e no gesto "puxar para atualizar". | inspeção |

---

## 9. Demais módulos (esboço)

### 9.1 Conta e pareamento (RF01, RF02)

| ID | Tipo | Requisito | Verificação |
| :--- | :--- | :--- | :--- |
| REQ-PAR-001 | Evento | **Quando** um usuário sem casal criar o HUB, o sistema deve torná-lo Parceiro A e gerar um código de convite de 6 caracteres (sem 0/O/1/I/L) válido por 48 h. | `dominio/test_casal::test_codigo_de_convite`, `api/test_fluxos` (fixture `casal`) |
| REQ-PAR-002 | Evento | **Quando** outro usuário informar um código válido, o sistema deve torná-lo Parceiro B, ativar o casal e invalidar o código (uso único). | `dominio/test_casal::test_entrada_valida`, `api/test_fluxos` (fixture `casal`) |
| REQ-PAR-003 | Indesejado | **Se** o código estiver expirado, já tiver sido usado ou o usuário já pertencer a um casal, **então** o sistema deve recusar (`CONVITE_EXPIRADO` / `CONVITE_USADO` / `JA_PAREADO`). | `dominio/test_casal::test_entradas_recusadas` |
| REQ-PAR-004 | Opcional | **Onde** a autenticação social estiver habilitada, o sistema deve permitir cadastro via Google ou Apple (campo `provedor_auth`; fora do MVP). | — (fora do MVP) |

### 9.2 Minigame "Onde vamos?" (RF03, RB02)

| ID | Tipo | Requisito | Verificação |
| :--- | :--- | :--- | :--- |
| REQ-DEC-001 | Estado | **Enquanto** a rodada estiver COLETANDO, o sistema deve manter em segredo as opções de cada parceiro, informando ao outro apenas se ele já enviou. | `api/test_fluxos::test_minigame_…` |
| REQ-DEC-002 | Indesejado | **Se** um envio tiver menos de 1 ou mais de 5 preferências, mais de 2 vetos, peso fora de 1–5 ou vetar algo que o próprio parceiro sugeriu, **então** o sistema deve recusá-lo. | `dominio/test_decisao::test_submissoes_invalidas` |
| REQ-DEC-003 | Evento | **Quando** os dois enviarem, o sistema deve remover de ambas as listas as opções vetadas por qualquer um. | `dominio/test_decisao::test_veto_…` |
| REQ-DEC-004 | Evento | **Quando** houver opção em comum, o sistema deve escolhê-la (MATCH), desempatando pela maior soma de pesos, depois pela menor diferença de pesos e, por fim, por sorteio. | `dominio/test_decisao::test_match_…`, `test_desempate_…` |
| REQ-DEC-005 | Evento | **Quando** não houver opção em comum, o sistema deve sortear uma das opções restantes com probabilidade proporcional ao peso (PONDERADO). | `dominio/test_decisao::test_sem_match_…` |
| REQ-DEC-006 | Complexo | **Enquanto** o último sorteio ponderado do casal tiver favorecido um parceiro, **quando** houver novo sorteio ponderado, o sistema deve reduzir à metade o peso das opções desse parceiro. | `dominio/test_decisao::test_regra_de_equilibrio_…` |
| REQ-DEC-007 | Indesejado | **Se** todas as opções forem vetadas, **então** o sistema deve sortear, por cara ou coroa, qual parceiro escolhe. | `dominio/test_decisao::test_tudo_vetado_…` |
| REQ-DEC-008 | Ubíquo | O sistema deve gravar a semente de cada sorteio, permitindo reproduzir o resultado. | `dominio/test_decisao::test_mesma_semente_…` |

### 9.3 Ideias de dates (RF04)

| ID | Tipo | Requisito |
| :--- | :--- | :--- |
| REQ-DATE-001 | Ubíquo | O sistema deve exibir ao casal o catálogo global de ideias mais as ideias privadas do próprio casal, nunca as de outro casal. |
| REQ-DATE-002 | Evento | **Quando** o casal filtrar ideias, o sistema deve aceitar ambiente (em casa / fora), categoria, custo, favoritos e busca por título. |
| REQ-DATE-003 | Evento | **Quando** o casal favoritar uma ideia ou marcá-la como realizada, o sistema deve registrar a data no espaço do casal. |
| REQ-DATE-004 | Evento | **Quando** um parceiro pedir uma sugestão aleatória com filtro de ambiente, o sistema deve sortear uma ideia visível que atenda ao filtro. |

---

## 10. Cenários de aceitação (Dado / Quando / Então)

**C1 — Semana ganha vira massagem** (REQ-QZ-009, PTS-006, RNK-003, CRD-001, VAL-004, VAL-009)
- **Dado** que Lucas publicou o quiz "Você me conhece?" (2 perguntas × 10 pts) e Beatris acertou as duas, uma delas após correção manual do Lucas
- **E** que Lucas ofereceu o "Vale massagem de 20 minutos"
- **Quando** chegar segunda-feira 12:00 e Beatris abrir a tela de vales
- **Então** a semana fecha com Beatris 24 × 0 Lucas (20 + bônus de 20 %), ela recebe 1 crédito `VENCEDOR_SEMANA`
- **E** ao resgatar, o vale fica RESGATADO, o crédito é consumido e Lucas é notificado
- **E** só Beatris pode confirmar o uso, que leva o vale a UTILIZADO.

**C2 — Correção esquecida** (REQ-QZ-011, RET-005, RNK-007)
- **Dado** a retrospectiva da Beatris com uma resposta de texto livre que Lucas errou de grafia e ela não corrigiu
- **Quando** a semana fecha
- **Então** o palpite vale PARCIAL, o quiz encerra e os pontos entram na semana da retrospectiva.

**C3 — "Tanto faz"** (REQ-DEC-001, DEC-003, DEC-004)
- **Dado** que Lucas sugeriu Japonês (peso 5) e Pizza e vetou Hambúrguer, e Beatris sugeriu "japones" (peso 3) e Hambúrguer
- **Quando** Beatris enviar
- **Então** Hambúrguer é eliminado e o resultado é MATCH em "Japonês".

---

## 11. Questões em aberto

1. **Empate** dá crédito aos dois (decisão atual) ou a ninguém? Dar aos dois reforça a cooperação (RB01); a outra opção reforça a competição (persona Beatris).
2. **Benefício da dúvida**: palpite não corrigido vale PARCIAL. Alternativa: ACERTO (mais generoso) ou ERRO (pune o palpiteiro pela omissão de quem deveria corrigir — parece injusto).
3. **Vale reutilizável**: hoje cada vale é de uso único; um "modelo" que gera cópias seria útil para mimos recorrentes.
4. **Notificação push** (Expo Push) quando o app está fechado — o RNF01 hoje é atendido só com o app aberto (WebSocket).
5. **Desfazer casal**: o status `ENCERRADO` existe no modelo, mas o fluxo (o que acontece com o histórico) não foi especificado.
