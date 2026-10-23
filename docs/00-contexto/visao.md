# HUB de Interação e Gamificação para Casais

---

## 1. Introdução e Propósito

### 1.1 Visão Geral
O projeto consiste no desenvolvimento de uma aplicação (HUB) privada voltada exclusivamente para casais. O objetivo principal é enriquecer a rotina do casal por meio de minijogos de tomada de decisão, *quizzes* semanais de memória e conhecimento mútuo, banco de ideias para encontros (*dates*) e um sistema gamificado de recompensas baseado em "vales".

### 1.2 Problema
Muitos casais enfrentam desafios do cotidiano como:
- **Indecisão recorrente:** Dificuldade e atrito no momento de escolher restaurantes, passeios ou atividades no tempo livre.
- **Perda de atenção aos detalhes:** Desconexão sobre como foi a semana do parceiro devido à correria da rotina.
- **Monotonia na rotina:** Falta de ideias criativas para encontros (seja em casa ou fora).

### 1.3 Solução Proposta
Uma plataforma centralizada que combina **decisão divertida + gamificação do relacionamento + catálogo de ideias**, permitindo que o casal fortaleça sua conexão de maneira leve e descontraída.

---

## 2. Personas e Público-Alvo

### Persona 1: O Parceiro Organizado
* **Nome:** Lucas Mendes (23 anos)
* **Ocupação:** Analista de Dados Junior / Estudante
* **Perfil:** Atencioso, gosta de planejar o tempo livre com antecedência e tem afinidade com tecnologia.
* **Dores:** Demora para decidir passeios; sente que a rotina de trabalho faz perder detalhes da semana da parceira.
* **Objetivos:** Ter um catálogo de ideias de *dates* e acompanhar a rotina da parceira através dos *quizzes* semanais.

### Persona 2: A Parceira Competitiva
* **Nome:** Beatris Oliveira (22 anos)
* **Ocupação:** Estagiária de Comunicação Social
* **Perfil:** Expressiva, adora brincadeiras, dinâmicas de competição e demonstrações afetivas.
* **Dores:** Conversas repetitivas durante a semana; indecisões cotidianas com respostas do tipo "tanto faz".
* **Objetivos:** Ganhar pontos e resgatar "vales" carinhosos/divertidos, mantendo um ranking ativo entre o casal.

---

## 3. Requisitos de Negócio (RB)

| Código | Descrição |
| :--- | :--- |
| **RB01** | **Fortalecimento da Conexão:** Estimular a comunicação contínua e a empatia no dia a dia do casal. |
| **RB02** | **Redução de Atritos:** Agilizar a escolha de locais e passeios através de dinâmicas gamificadas de decisão. |
| **RB03** | **Gamificação e Engajamento:** Aumentar a retenção dos usuários com *quizzes*, rankings e prêmios ("vales"). |
| **RB04** | **Privacidade e Exclusividade:** Garantir que o ambiente de interações seja estritamente restrito e seguro para o par. |

---

## 4. Requisitos Não Funcionais (RNF)

| Código | Descrição | Categoria |
| :--- | :--- | :--- |
| **RNF01** | O sistema deve refletir interações entre os dois parceiros em até 2 segundos. | Desempenho / Sincronia |
| **RNF02** | As respostas dos *quizzes* e dados pessoais devem ser criptografados (HTTPS/TLS e repouso). | Segurança e Privacidade |
| **RNF03** | O sistema deve manter alta disponibilidade (mínimo de 99% de *uptime*). | Disponibilidade |
| **RNF04** | A interface deve ser simples e permitir ações principais com até 3 toques. | Usabilidade |
| **RNF05** | O aplicativo deve ser compatível com sistemas Android e iOS (ou web responsivo). | Portabilidade |

---

## 5. Requisitos Funcionais (RF)

### 5.1 Módulo de Conta e Sincronização
- **RF01 - Autenticação:** Cadastro e login via e-mail/senha ou conta social.
- **RF02 - Pareamento:** Vínculo entre os dois usuários via código único ou link de convite.

### 5.2 Módulo de Tomada de Decisão e Dates
- **RF03 - Sorteador/Minijogo:** Ferramentas dinâmicas (roleta, sorteio, pedra-papel-tesoura) para definir decisões do casal.
- **RF04 - Banco de Dates:** Catálogo de ideias para encontros (divididos em *em casa* e *fora de casa*) com opção de adicionar favoritos e ideias personalizadas.

### 5.3 Módulo de Quizzes e Ranking
- **RF05 - Quiz do Relacionamento:** Criação e resposta a perguntas personalizadas sobre o histórico e gostos do casal.
- **RF06 - Quiz Semanal:** Perguntas sobre acontecimentos e rotina dos últimos 7 dias.
- **RF07 - Ranking Semanal/Mensal:** Placar pontuado automaticamente com base nos acertos dos *quizzes*.

### 5.4 Módulo de Prêmios e Vales
- **RF08 - Gestão de Vales:** Criação e personalização de cartões de "vales" (ex: *Vale massagem*, *Vale 1 dia sem celular*).
- **RF09 - Resgate de Vales:** Solicitação de resgate do prêmio pelo vencedor, atualizando o status do vale e notificando o parceiro.