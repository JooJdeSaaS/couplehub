import { useState } from 'react';
import { Alert, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Carregando, Cartao, Chips, Tela, Texto, Titulo } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

const PESOS = [1, 2, 3, 4, 5].map((n) => ({ valor: n, rotulo: '♥'.repeat(n) }));
const TIPO = {
  MATCH: 'Deu match! 💘',
  PONDERADO: 'Sorteio ponderado 🎡',
  CARA_OU_COROA: 'Cara ou coroa 🪙',
};

export default function RodadaScreen({ route }) {
  const { id } = route.params;
  const { nomeDe, parceiro } = useAuth();
  const [opcoes, setOpcoes] = useState([{ rotulo: '', peso: 3 }]);
  const [vetos, setVetos] = useState(['']);
  const [enviando, setEnviando] = useState(false);
  const { dados: rodada, recarregar } = useDados(() => Api.rodada(id), ['decisao.']);

  if (!rodada) return <Carregando />;

  async function enviar() {
    setEnviando(true);
    try {
      await Api.enviarOpcoes(
        id,
        opcoes.filter((o) => o.rotulo.trim()).map((o) => ({ rotulo: o.rotulo.trim(), peso: o.peso })),
        vetos.map((v) => v.trim()).filter(Boolean),
      );
      await recarregar();
    } catch (e) {
      Alert.alert('Ops', e.message);
    } finally {
      setEnviando(false);
    }
  }

  const r = rodada.resultado;
  return (
    <Tela aoAtualizar={recarregar}>
      <Titulo sub={rodada.parceiro_enviou ? `${parceiro?.nome} já mandou as opções (em segredo 🤫)` : `${parceiro?.nome} ainda não mandou`}>
        {rodada.titulo}
      </Titulo>

      {r && (
        <Cartao destaque={cores.secundaria}>
          <Texto suave>{TIPO[r.tipo]}</Texto>
          <Texto negrito tamanho={26} estilo={{ marginVertical: 6 }}>
            {r.rotulo ?? `${nomeDe(r.escolhedor_id)} escolhe desta vez!`}
          </Texto>
          <Texto suave tamanho={13}>{r.justificativa}</Texto>
          <Texto suave tamanho={12} estilo={{ marginTop: 6 }}>Semente do sorteio: {r.semente}</Texto>
        </Cartao>
      )}

      {rodada.status === 'COLETANDO' && !rodada.eu_enviei && (
        <Cartao>
          <Texto negrito>Suas opções (até 5) — quanto mais ♥, mais você quer</Texto>
          {opcoes.map((o, i) => (
            <View key={i}>
              <Campo
                value={o.rotulo}
                onChangeText={(v) => setOpcoes((os) => os.map((x, j) => (j === i ? { ...x, rotulo: v } : x)))}
                placeholder={['Japonês', 'Pizza', 'Cinema', 'Hambúrguer', 'Ficar em casa'][i]}
                maxLength={60}
              />
              <Chips opcoes={PESOS} valor={o.peso} aoMudar={(v) => setOpcoes((os) => os.map((x, j) => (j === i ? { ...x, peso: v } : x)))} />
            </View>
          ))}
          {opcoes.length < 5 && <Botao pequeno variante="fantasma" titulo="+ Opção" aoPressionar={() => setOpcoes((os) => [...os, { rotulo: '', peso: 3 }])} />}

          <Texto negrito estilo={{ marginTop: 12 }}>Vetos (até 2) — isso NÃO rola</Texto>
          {vetos.map((v, i) => (
            <Campo key={i} value={v} onChangeText={(t) => setVetos((vs) => vs.map((x, j) => (j === i ? t : x)))} placeholder="Ex.: Fast-food" maxLength={60} />
          ))}
          {vetos.length < 2 && <Botao pequeno variante="fantasma" titulo="+ Veto" aoPressionar={() => setVetos((vs) => [...vs, ''])} />}

          <Botao titulo="Enviar em segredo" carregando={enviando} desabilitado={!opcoes.some((o) => o.rotulo.trim())} aoPressionar={enviar} />
        </Cartao>
      )}

      {rodada.minhas_entradas.length > 0 && (
        <Cartao>
          <Texto negrito>Você mandou</Texto>
          {rodada.minhas_entradas.map((e, i) => (
            <Texto key={i} suave>{e.veto ? `🚫 ${e.rotulo}` : `${'♥'.repeat(e.peso)} ${e.rotulo}`}</Texto>
          ))}
        </Cartao>
      )}
      {rodada.entradas_do_parceiro && (
        <Cartao>
          <Texto negrito>{parceiro?.nome} mandou</Texto>
          {rodada.entradas_do_parceiro.map((e, i) => (
            <Texto key={i} suave>{e.veto ? `🚫 ${e.rotulo}` : `${'♥'.repeat(e.peso)} ${e.rotulo}`}</Texto>
          ))}
        </Cartao>
      )}
    </Tela>
  );
}
