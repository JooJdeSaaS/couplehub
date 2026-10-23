import { useFocusEffect } from '@react-navigation/native';
import { useCallback, useEffect, useRef, useState } from 'react';
import { AppState } from 'react-native';

import { WS_URL } from '../config';

// --- barramento de eventos simples (um por app) ------------------------------
const ouvintes = new Set();
const emitir = (evento) => ouvintes.forEach((f) => f(evento));
const assinar = (f) => {
  ouvintes.add(f);
  return () => ouvintes.delete(f);
};

/** Mantém o WebSocket do casal aberto enquanto `token` existir (RNF01 / REQ-RT-001).
 *  Reconecta sozinho e avisa as telas quando o app volta ao primeiro plano (REQ-RT-002). */
export function useCanalDoCasal(token) {
  useEffect(() => {
    if (!token) return undefined;
    let ws;
    let ativo = true;
    let espera = 1000;

    const conectar = () => {
      ws = new WebSocket(`${WS_URL}/ws?token=${encodeURIComponent(token)}`);
      ws.onopen = () => (espera = 1000);
      ws.onmessage = (msg) => {
        try {
          emitir(JSON.parse(msg.data));
        } catch {
          /* mensagem inválida: ignora */
        }
      };
      ws.onclose = () => {
        if (!ativo) return;
        setTimeout(conectar, espera);
        espera = Math.min(espera * 2, 30000);
      };
    };
    conectar();

    const sub = AppState.addEventListener('change', (s) => s === 'active' && emitir({ tipo: 'app.ativo' }));
    return () => {
      ativo = false;
      sub.remove();
      ws?.close();
    };
  }, [token]);
}

/**
 * Carrega dados da API e recarrega: ao focar a tela, ao voltar o app ao primeiro
 * plano e quando chega um evento cujo tipo começa com um dos `prefixos`
 * (ex.: ['vale.', 'quiz.']).
 */
export function useDados(carregar, prefixos = []) {
  const ref = useRef(carregar);
  ref.current = carregar;
  const [estado, setEstado] = useState({ dados: null, carregando: true, erro: null });

  const recarregar = useCallback(async () => {
    try {
      const dados = await ref.current();
      setEstado({ dados, carregando: false, erro: null });
    } catch (erro) {
      setEstado((e) => ({ ...e, carregando: false, erro }));
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      recarregar();
    }, [recarregar]),
  );

  const chave = prefixos.join('|');
  useEffect(
    () =>
      assinar((ev) => {
        if (ev.tipo === 'app.ativo' || chave.split('|').some((p) => p && ev.tipo?.startsWith(p))) recarregar();
      }),
    [recarregar, chave],
  );

  return { ...estado, recarregar };
}
