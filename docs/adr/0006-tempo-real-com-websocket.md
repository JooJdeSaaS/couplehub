# ADR-0006 — Sincronização em tempo real via WebSocket por casal

- **Status:** aceita
- **Data:** 2026-10-22

## Contexto
RNF01: atualizações de jogos, quizzes e resgates devem aparecer no outro aparelho em menos de 2 segundos.

## Decisão
- Endpoint `GET /ws?token=<JWT>`; cada conexão entra na "sala" do seu `casal_id`.
- Após cada comando bem-sucedido, a rota agenda (via `BackgroundTasks`, portanto **depois do commit**) um evento leve, p.ex. `{"tipo": "vale.resgatado", "vale_id": "..."}`. O app recarrega o recurso pela API REST — o evento não carrega dados sensíveis.
- Hub em memória (`app/realtime/hub.py`), suficiente para um processo.
- Fallback (REQ-RT-002): o app recarrega ao voltar ao primeiro plano e no "puxar para atualizar".

## Consequências
- (+) Latência típica de dezenas de milissegundos na mesma rede.
- (–) Não funciona com o app fechado: notificação push (Expo Push) fica como evolução.
- (–) Com vários processos/servidores, trocar o hub por Redis Pub/Sub (mesma interface `publicar`).

## Alternativas consideradas
- **Polling a cada 2 s:** trivial, mas gasta bateria e dados à toa.
- **Server-Sent Events:** suporte irregular no React Native.
