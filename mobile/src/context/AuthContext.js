import * as SecureStore from 'expo-secure-store';
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { Api, definirToken } from '../api/cliente';

const CHAVE_TOKEN = 'couplehub.token';
const AuthContext = createContext(null);

// SecureStore não existe no navegador; na web o token fica só em memória.
const armazenamento = {
  ler: () => SecureStore.getItemAsync(CHAVE_TOKEN).catch(() => null),
  gravar: (t) => SecureStore.setItemAsync(CHAVE_TOKEN, t).catch(() => {}),
  apagar: () => SecureStore.deleteItemAsync(CHAVE_TOKEN).catch(() => {}),
};

export function AuthProvider({ children }) {
  const [estado, setEstado] = useState({ carregando: true, token: null, usuario: null, casal: null });

  const carregarSessao = useCallback(async (token) => {
    definirToken(token);
    const [usuario, casal] = await Promise.all([Api.eu(), Api.meuCasal()]);
    setEstado({ carregando: false, token, usuario, casal });
  }, []);

  useEffect(() => {
    (async () => {
      const token = await armazenamento.ler();
      if (!token) return setEstado((e) => ({ ...e, carregando: false }));
      try {
        await carregarSessao(token);
      } catch {
        await armazenamento.apagar();
        setEstado({ carregando: false, token: null, usuario: null, casal: null });
      }
    })();
  }, [carregarSessao]);

  const valor = useMemo(() => {
    const parceiro = estado.casal?.membros?.find((m) => m.id !== estado.usuario?.id) ?? null;
    return {
      ...estado,
      parceiro,
      pareado: estado.casal?.status === 'ATIVO',
      async entrar({ access_token }) {
        await armazenamento.gravar(access_token);
        await carregarSessao(access_token);
      },
      async sair() {
        await armazenamento.apagar();
        definirToken(null);
        setEstado({ carregando: false, token: null, usuario: null, casal: null });
      },
      async atualizarCasal() {
        const casal = await Api.meuCasal();
        setEstado((e) => ({ ...e, casal }));
        return casal;
      },
      nomeDe(usuarioId) {
        if (usuarioId === estado.usuario?.id) return 'Você';
        return parceiro?.nome ?? 'Parceiro(a)';
      },
    };
  }, [estado, carregarSessao]);

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
