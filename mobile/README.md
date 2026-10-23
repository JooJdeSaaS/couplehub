# CoupleHUB — App (React Native + Expo)

## Rodar no celular com Expo Go

1. Suba o backend com `--host 0.0.0.0` (ver `backend/README.md`). Computador e celular precisam estar **na mesma rede Wi-Fi**.
2. Instale as dependências e alinhe as versões com o SDK do Expo:

   ```bash
   cd mobile
   npm install
   npx expo install --fix
   ```

   O `package.json` foi escrito para o **Expo SDK 54**. Se o Expo Go do seu celular pedir um SDK mais novo, atualize antes de abrir:

   ```bash
   npx expo install expo@latest
   npx expo install --fix
   ```

3. `npx expo start` e leia o QR code com o Expo Go (Android) ou com a câmera (iOS).

O app descobre sozinho o IP do computador a partir do servidor do Expo e chama `http://<ip>:8000`. Para apontar para outra API: `EXPO_PUBLIC_API_URL=https://minha-api.com npx expo start`.

**Não conecta?** Confira se `http://<ip-do-computador>:8000/saude` abre no navegador do celular. Se não abrir, libere a porta 8000 no firewall.

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
