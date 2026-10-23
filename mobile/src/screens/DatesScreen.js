import { useEffect, useRef, useState } from 'react';
import { Alert, Pressable, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Chips, Selo, Tela, Texto, Titulo, Vazio } from '../components/ui';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

const AMBIENTES = [
  { valor: null, rotulo: 'Todos' },
  { valor: 'EM_CASA', rotulo: '🏠 Em casa' },
  { valor: 'FORA_DE_CASA', rotulo: '🌆 Fora' },
];
const CATEGORIAS = ['GASTRONOMIA', 'CULTURA', 'AVENTURA', 'RELAXAMENTO', 'CRIATIVO', 'ESPORTE', 'ROMANTICO'].map((c) => ({
  valor: c,
  rotulo: c.charAt(0) + c.slice(1).toLowerCase(),
}));
const CUSTO = { GRATIS: 'grátis', BAIXO: '$', MEDIO: '$$', ALTO: '$$$' };

/** RF04: catálogo de ideias (global + do casal), filtros, favoritos e sorteio. */
export default function DatesScreen() {
  const [ambiente, setAmbiente] = useState(null);
  const [favoritos, setFavoritos] = useState(false);
  const [nova, setNova] = useState(null); // {titulo, ambiente, categoria} enquanto o formulário está aberto
  const { dados: ideias, carregando, recarregar } = useDados(
    () => Api.dates({ ambiente, favoritos: favoritos || undefined }),
    [],
  );

  // filtros mudaram -> recarrega (a primeira carga já vem do foco da tela)
  const primeiraVez = useRef(true);
  useEffect(() => {
    if (primeiraVez.current) {
      primeiraVez.current = false;
      return;
    }
    recarregar();
  }, [ambiente, favoritos, recarregar]);

  async function agir(acao) {
    try {
      const resultado = await acao();
      await recarregar();
      return resultado;
    } catch (e) {
      Alert.alert('Ops', e.message);
      return null;
    }
  }

  async function sortear() {
    const ideia = await agir(() => Api.sortearDate(ambiente ?? undefined));
    if (ideia) Alert.alert('Que tal?', `${ideia.titulo}\n\n${ideia.descricao ?? ''}`);
  }

  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub="Inspiração para dias animados e dias de cansaço">Ideias de date</Titulo>
      <Chips opcoes={AMBIENTES} valor={ambiente} aoMudar={setAmbiente} />
      <View style={{ flexDirection: 'row', gap: 8 }}>
        <View style={{ flex: 1 }}>
          <Botao pequeno variante="secundario" titulo="Sortear uma 🎲" aoPressionar={sortear} />
        </View>
        <View style={{ flex: 1 }}>
          <Botao pequeno variante="fantasma" titulo={favoritos ? 'Ver todas' : '★ Favoritas'} aoPressionar={() => setFavoritos((f) => !f)} />
        </View>
      </View>

      {nova ? (
        <Cartao>
          <Campo rotulo="Nossa ideia" value={nova.titulo} onChangeText={(t) => setNova({ ...nova, titulo: t })} placeholder="Noite de fondue" />
          <Chips opcoes={AMBIENTES.slice(1)} valor={nova.ambiente} aoMudar={(v) => setNova({ ...nova, ambiente: v })} />
          <Chips opcoes={CATEGORIAS} valor={nova.categoria} aoMudar={(v) => setNova({ ...nova, categoria: v })} />
          <Botao
            titulo="Salvar ideia"
            desabilitado={nova.titulo.trim().length < 3}
            aoPressionar={async () => {
              const ok = await agir(() => Api.criarDate(nova));
              if (ok) setNova(null);
            }}
          />
          <Botao variante="fantasma" titulo="Cancelar" aoPressionar={() => setNova(null)} />
        </Cartao>
      ) : (
        <Botao variante="fantasma" titulo="+ Adicionar nossa ideia" aoPressionar={() => setNova({ titulo: '', ambiente: 'EM_CASA', categoria: 'ROMANTICO' })} />
      )}

      {ideias?.length === 0 && <Vazio>Nada por aqui com esse filtro.</Vazio>}
      {ideias?.map((d) => (
        <Cartao key={d.id}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <View style={{ flex: 1, paddingRight: 8 }}>
              <Texto negrito>{d.titulo}</Texto>
              {d.descricao ? <Texto suave tamanho={13}>{d.descricao}</Texto> : null}
            </View>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel={d.favorito ? 'Remover dos favoritos' : 'Favoritar'}
              onPress={() => agir(() => Api.favoritar(d.id, !d.favorito))}
              hitSlop={12}
            >
              <Texto tamanho={24} cor={d.favorito ? cores.primaria : cores.suave}>{d.favorito ? '★' : '☆'}</Texto>
            </Pressable>
          </View>
          <View style={{ flexDirection: 'row', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
            <Selo texto={d.ambiente === 'EM_CASA' ? 'em casa' : 'fora'} />
            <Selo texto={CUSTO[d.custo]} />
            {d.duracao_min ? <Selo texto={`${d.duracao_min} min`} /> : null}
            {d.personalizada ? <Selo texto="nossa" cor={cores.secundaria} /> : null}
            {d.realizado_em ? <Selo texto="✔ feito" cor={cores.secundaria} /> : null}
          </View>
          {!d.realizado_em && (
            <Botao pequeno variante="fantasma" titulo="Fizemos!" aoPressionar={() => agir(() => Api.marcarRealizado(d.id))} />
          )}
        </Cartao>
      ))}
    </Tela>
  );
}
