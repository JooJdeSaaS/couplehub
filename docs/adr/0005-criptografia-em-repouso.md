# ADR-0005 — Criptografia em repouso de respostas (Fernet por coluna)

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
RNF02 exige que respostas de quizzes e histórico do casal sejam cifrados em trânsito e em repouso. O SQLite não oferece criptografia nativa (SQLCipher exigiria build especial).

## Decisão
- Tipo de coluna `TextoCifrado` (TypeDecorator) que cifra ao gravar e decifra ao ler, usando **Fernet** (AES-128-CBC + HMAC-SHA256) da biblioteca `cryptography`.
- Aplicado a `resposta.valor` (gabaritos e palpites). Senhas usam hash **scrypt** (não reversível).
- Chave em `COUPLEHUB_CHAVE_DADOS`. Em dev, se ausente, é gerada em `backend/data/.chave_dev` (fora do git). Fora de dev, a API não sobe sem a chave.
- Em trânsito: HTTPS/TLS terminado no proxy/hospedagem de produção (no Expo Go local usa-se HTTP na rede de casa).

## Consequências
- (+) Um dump do arquivo `.db` não revela o que o casal respondeu.
- (–) Campos cifrados não podem ser filtrados/comparados em SQL; a correção é feita em Python (já era assim).
- (–) Perder a chave = perder as respostas. Rotação de chave exigirá `MultiFernet`.

## Alternativas consideradas
- **SQLCipher:** cifra o arquivo inteiro, mas complica a instalação em Windows/macOS de cada integrante.
- **Cifrar no app (E2E):** maior privacidade, porém impede a correção automática no servidor.
