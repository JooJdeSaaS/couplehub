import { useState } from 'react';
import { Alert, Pressable, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Selo, Tela, Texto, Titulo, Vazio } from '../components/ui';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

/** RF03: lista de rodadas do "Onde vamos?" e abertura de nova rodada. */
export default function DecidirScreen({ navigation }) {
  const [titulo, setTitulo] = useState('');
  const { dados: rodadas, carregando, recarregar } = useDados(() => Api.rodadas(), ['decisao.']);

  async function abrir() {
    try {
      const rodada = await Api.abrirRodada(titulo.trim());
      setTitulo('');
      navigation.navigate('Rodada', { id: rodada.id });
    } catch (e) {
      Alert.alert('Ops', e.message);
    }
  }

  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub="Cada um manda opções e vetos em segredo. O app cruza tudo.">Onde vamos? 🎲</Titulo>
      <Cartao>
        <Campo rotulo="Nova rodada" value={titulo} onChangeText={setTitulo} placeholder="Jantar de sábado" maxLength={80} />
        <Botao titulo="Abrir rodada" desabilitado={titulo.trim().length < 2} aoPressionar={abrir} />
      </Cartao>
      {rodadas?.length === 0 && <Vazio>Nenhuma rodada ainda.</Vazio>}
      {rodadas?.map((r) => (
        <Pressable key={r.id} onPress={() => navigation.navigate('Rodada', { id: r.id })} accessibilityRole="button">
          <Cartao>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
              <Texto negrito>{r.titulo}</Texto>
              {r.status === 'RESOLVIDA' ? (
                <Selo texto="Decidido" cor={cores.secundaria} />
              ) : r.status === 'CANCELADA' ? (
                <Selo texto="Cancelada" />
              ) : (
                <Selo texto={r.eu_enviei ? 'Aguardando par' : 'Sua vez'} cor={r.eu_enviei ? cores.suave : cores.primaria} />
              )}
            </View>
            {r.resultado?.rotulo ? <Texto suave>→ {r.resultado.rotulo}</Texto> : null}
          </Cartao>
        </Pressable>
      ))}
    </Tela>
  );
}
