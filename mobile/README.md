# CoupleHUB — App (React Native + Expo)

## Rodar no celular com Expo Go

> **Pré-requisito:** Node.js **22.13 ou mais novo** (`node -v`), exigência do Expo SDK 58.

1. Suba o backend com `--host 0.0.0.0` (ver `backend/README.md`). Computador e celular precisam estar **na mesma rede Wi-Fi**.
2. Instale as dependências e alinhe as versões com o SDK do Expo:

   ```bash
   cd mobile
   npm install
   npm run modulos-expo        # expo-constants, expo-secure-store… na versão exata do SDK
   npx expo install --fix      # confere e fixa o restante
   npx expo-doctor@latest      # deve terminar sem erros
   ```

   O projeto **não tem `babel.config.js`** de propósito: sem ele o Expo usa a configuração padrão e encontra o `babel-preset-expo` sozinho.

   O projeto usa o **Expo SDK 58** (o Expo Go das lojas só abre o SDK atual). Se um dia o Expo Go pedir um SDK mais novo, troque o `58` pelo número pedido:

   ```bash
   npx expo install expo@^58.0.0 --fix
   ```

   Depois de alinhar, **versione o `package.json` e o `package-lock.json`** para todos da equipe usarem as mesmas versões.

3. `npx expo start -c` e leia o QR code com o Expo Go (Android) ou com a câmera (iOS). O `-c` limpa o cache do Metro, útil após trocar de SDK.

O app descobre sozinho o IP do computador a partir do servidor do Expo e chama `http://<ip>:8000`. O endereço usado aparece no terminal como `[CoupleHUB] API em http://...`. Para forçar outro: `EXPO_PUBLIC_API_URL=http://192.168.0.10:8000 npx expo start`.

**Erro `reading 'transformFile'`?** É um sintoma: o Metro não conseguiu montar o compilador e esconde o motivo. O motivo real aparece no início do `npx expo start`, na linha `Failed to construct transformer`. Para ver só ela:

```bash
CI=1 timeout 60 npx expo start -c 2>&1 | grep -A 15 "Failed to construct transformer"
```

A causa mais comum é `Cannot find module 'babel-preset-expo'` (versões misturadas no `node_modules`). Solução: apagar `node_modules`, `package-lock.json` e `.expo` e repetir o passo 2.

**Não conecta?** Confira se `http://<ip-do-computador>:8000/saude` abre no navegador do celular. Se não abrir:
- confirme que a API subiu com `--host 0.0.0.0`;
- libere a porta 8000 no firewall (Ubuntu: `sudo ufw allow 8000/tcp`).

## Estrutura

```
App.js                  navegação: Login → Parear → 5 abas + telas de detalhe
src/config.js           URL da API e do WebSocket
src/api/cliente.js      fetch + um método por endpoint + ErroApi {status, codigo}
src/context/AuthContext token no SecureStore, usuário, casal, parceiro
src/hooks/tempoReal.js  WebSocket do casal (RNF01) e useDados (recarrega no foco/evento)
src/components/ui.js    Tela, Cartao, Botao, Campo, Chips, Selo…
src/screens/            Login, Parear, Inicio, Quizzes, QuizDetalhe, NovoQuiz,
                        Vales, Ranking, Decidir, Rodada, Dates
```

## Testar com duas pessoas
Abra o app em dois celulares (ou um celular + Expo Web com `w` no terminal), crie as duas contas, pareie e faça um quiz: a tela do outro aparelho se atualiza sozinha quando chega um evento.
