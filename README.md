# 👩‍❤️‍👨 CoupleHub - HUB de Interação e Gamificação para Casais

> Projeto desenvolvido para a disciplina de **Modelagem de Sistemas**.

O **CoupleHub** é uma plataforma pensada para aproximar casais por meio da gamificação, auxílio na tomada de decisões cotidianas, quizzes de sintonia e um sistema dinâmico de recompensas afetivas ("vales").

## 🚀 Visão Geral

Escolher onde comer ou o que fazer no final de semana muitas vezes se torna um impasse silencioso no relacionamento. Além disso, a correria do dia a dia dificulta manter dinâmicas divertidas e acompanhar os detalhes da semana do parceiro.

O **CoupleHub** resolve esses problemas unindo:
1. **Decisões Rápidas:** Minijogos e sorteios visuais para acabar com o *"tanto faz"*.
2. **Quizzes de Sintonia:** Perguntas sobre o relacionamento e acompanhamento da semana.
3. **Sistema de Vales:** Recompensas afetivas (ex: *Vale Massagem*, *Vale Ficar sem Celular*) resgatadas com a pontuação dos jogos.
4. **Catálogo de Dates:** Ideias criativas para momentos dentro e fora de casa.

---

## 🎮 Funcionalidades Principais

* **Conexão Exclusiva do Casal:** Vinculação segura entre 2 usuários via código de pareamento.
* **Minijogos de Decisão:** Roleta, pedra-papel-tesoura e sorteios interativos para definir escolhas cotidianas.
* **Quiz Semanal & Perfil:** Perguntas sobre fatos da semana do outro e curiosidades do casal.
* **Ranking & Placar:** Pontuação atualizada semanalmente e mensalmente.
* **Loja de Vales:** Criação, conquista e resgate de recompensas personalizadas.
* **Ideias de Encontros:** Guia interativo de dates categorizados por local e estilo.

---

## 📄 Requisitos do Sistema

### Requisitos de Negócio (RB)
* **RB01:** Fortalecer a comunicação, empatia e cumplicidade no dia a dia do casal.
* **RB02:** Reduzir atritos cotidianos na tomada de decisões de lazer e alimentação.
* **RB03:** Engajar o casal por meio de mecânicas de gamificação, pontuação e conquistas.
* **RB04:** Garantir um ambiente estritamente privado e seguro para a dupla.

### Requisitos Não Funcionais (RNF)
* **RNF01 (Sincronização):** Atualização das ações dos parceiros em tempo real com latência $< 2$ segundos.
* **RNF02 (Segurança):** Criptografia de dados ponta a ponta para preservar as informações e respostas do casal.
* **RNF03 (Disponibilidade):** Disponibilidade mínima de 99% (*uptime*).
* **RNF04 (Usabilidade):** Interface intuitiva com acesso a qualquer funcionalidade principal em até 3 toques/cliques.
* **RNF05 (Compatibilidade):** Suporte multiplataforma (Web Responsivo e Mobile).

### Requisitos Funcionais (RF)
* **RF01 - Cadastro e Autenticação:** Permite criar conta e realizar login individual.
* **RF02 - Pareamento de Casal:** Permite vincular dois usuários através de um código único.
* **RF03 - Sorteador de Decisões:** Disponibiliza dinâmicas visuais para tomada de decisão rápida.
* **RF04 - Cadastro e Filtro de Dates:** Permite visualizar e favoritar sugestões de encontros em/fora de casa.
* **RF05 - Quiz Personalizado do Casal:** Permite cadastrar e responder quizzes sobre o relacionamento.
* **RF06 - Quiz Semanal do Relacionamento:** Libera questionários periódicos sobre os últimos 7 dias da rotina do parceiro.
* **RF07 - Ranking e Placar:** Calcula pontuações e gera histórico do vencedor da semana/mês.
* **RF08 - Gerenciamento de Vales:** Permite a criação e concessão de "vales" customizados.
* **RF09 - Resgate de Vales:** Permite o resgate de recompensas conquistadas com notificação ao parceiro.

---

## 👤 Personas

### 💙 Lucas Mendes, 23 anos (O Organizado e Detalhista)
* **Perfil:** Analista de dados junior, gosta de planejar roteiros e busca formas de não deixar o relacionamento cair na rotina.
* **Dor:** Fica indeciso na hora de escolher lugares para ir e quer lembrar mais dos detalhes do dia a dia da parceira.
* **Objetivo no App:** Salvar ideias de dates, tomar decisões rápidas em jogos e acompanhar a rotina da parceira através dos quizzes.

### 💖 Beatris Oliveira, 22 anos (A Competitiva e Espontânea)
* **Perfil:** Estagiária de comunicação, competitiva, adora brincadeiras carinhosas e registrar memórias do casal.
* **Dor:** Acha entediante passar horas conversando sobre *"o que vamos comer hoje?"*.
* **Objetivo no App:** Ganhar os quizzes da semana, liderar o ranking e resgatar vales carinhosos (ex: *Vale Massagem*).

---

## 🛠️ Arquitetura e Modelagem

Como parte da disciplina de **Modelagem de Sistemas**, este repositório contempla os artefatos de engenharia de software:

* Documento de Visão
* Especificação de Requisitos (RF, RNF, RB)
* Diagrama de Casos de Uso
* Diagrama de Classes
* Diagrama de Sequência (Fluxo do Quiz Semanal e Resgate de Vales)

---

## 💻 Como Executar o Projeto

*(Ajuste de acordo com a stack técnica escolhida no seu projeto)*

```bash
# 1. Clonar o repositório
git clone https://github.com/JooJdeSaaS/couplehub.git

# 2. Entrar na pasta do projeto
cd couplehub

# 3. Instalar as dependências
npm install

# 4. Executar em modo de desenvolvimento
npm run dev
```

---

## 📝 Licença

Este projeto foi desenvolvido estritamente para fins acadêmicos.