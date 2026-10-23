import { useState } from 'react';
import { Alert, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Selo, Tela, Texto, Titulo, Vazio } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

const ORIGEM = {
  VENCEDOR_SEMANA: 'venceu a semana',
  VENCEDOR_MES: 'venceu o mês',
  VENCEDOR_QUIZ_SINTONIA: 'venceu um quiz de sintonia',
};

function Vale({ vale, children }) {
  return (
    <Cartao>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
        <Texto tamanho={28}>{vale.icone || '🎟️'}</Texto>
        <View style={{ flex: 1 }}>
          <Texto negrito>{vale.titulo}</Texto>
          {vale.descricao ? <Texto suave tamanho={13}>{vale.descricao}</Texto> : null}
        </View>
      </View>
      {children}
    </Cartao>
  );
}

/** RF08/RF09: cardápio de vales de cada um, resgate com crédito e confirmação de uso. */
export default function ValesScreen() {
  const { usuario, parceiro } = useAuth();
  const [titulo, setTitulo] = useState('');
  const [icone, setIcone] = useState('');
  const { dados, carregando, recarregar } = useDados(
    async () => {
      const [vales, creditos] = await Promise.all([Api.vales(), Api.creditos()]);
      return { vales, creditos };
    },
    ['vale.', 'quiz.'],
  );

  async function agir(acao, sucesso) {
    try {
      await acao();
      await recarregar();
      if (sucesso) Alert.alert('Pronto!', sucesso);
    } catch (e) {
      Alert.alert('Ops', e.message);
    }
  }

  const vales = dados?.vales ?? [];
  const creditos = dados?.creditos ?? [];
  const doParceiro = vales.filter((v) => v.status === 'DISPONIVEL' && v.criador_id !== usuario.id);
  const meus = vales.filter((v) => v.status === 'DISPONIVEL' && v.criador_id === usuario.id);
  const emAndamento = vales.filter((v) => v.status === 'RESGATADO');
  const usados = vales.filter((v) => v.status === 'UTILIZADO').slice(0, 10);

  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub="Vença a semana, o mês ou um quiz de sintonia para ganhar créditos">Vales</Titulo>

      <Cartao destaque={creditos.length ? cores.secundaria : undefined}>
        <Texto negrito>🎟️ {creditos.length} crédito(s) disponível(is)</Texto>
        {creditos.map((c) => (
          <Texto key={c.id} suave tamanho={13}>
            • Você {ORIGEM[c.origem]} ({c.referencia.length > 10 ? 'quiz' : c.referencia}) — vence em{' '}
            {new Date(c.expira_em).toLocaleDateString('pt-BR')}
          </Texto>
        ))}
      </Cartao>

      <Texto negrito tamanho={18} estilo={{ marginVertical: 8 }}>Cardápio de {parceiro?.nome}</Texto>
      {doParceiro.length === 0 && <Vazio>{parceiro?.nome} ainda não ofereceu vales.</Vazio>}
      {doParceiro.map((v) => (
        <Vale key={v.id} vale={v}>
          <Botao
            pequeno
            variante="secundario"
            titulo="Resgatar"
            desabilitado={!creditos.length}
            aoPressionar={() => agir(() => Api.resgatarVale(v.id), `${parceiro?.nome} foi avisado(a) 💌`)}
          />
        </Vale>
      ))}

      {emAndamento.length > 0 && (
        <>
          <Texto negrito tamanho={18} estilo={{ marginVertical: 8 }}>Resgatados</Texto>
          {emAndamento.map((v) => (
            <Vale key={v.id} vale={v}>
              {v.resgatado_por_id === usuario.id ? (
                <Botao pequeno titulo="Já recebi! ✅" aoPressionar={() => agir(() => Api.confirmarUso(v.id))} />
              ) : (
                <Selo texto={`Você deve este a ${parceiro?.nome}`} cor={cores.alerta} />
              )}
            </Vale>
          ))}
        </>
      )}

      <Texto negrito tamanho={18} estilo={{ marginVertical: 8 }}>Meu cardápio</Texto>
      {meus.map((v) => (
        <Vale key={v.id} vale={v}>
          <Botao pequeno variante="fantasma" titulo="Retirar do cardápio" aoPressionar={() => agir(() => Api.cancelarVale(v.id))} />
        </Vale>
      ))}
      <Cartao>
        <Campo rotulo="Novo vale" value={titulo} onChangeText={setTitulo} placeholder="Vale massagem de 20 minutos" maxLength={80} />
        <Campo rotulo="Emoji (opcional)" value={icone} onChangeText={setIcone} placeholder="💆" maxLength={4} />
        <Botao
          titulo="Oferecer vale"
          desabilitado={titulo.trim().length < 3}
          aoPressionar={() =>
            agir(async () => {
              await Api.criarVale(titulo, icone);
              setTitulo('');
              setIcone('');
            })
          }
        />
      </Cartao>

      {usados.length > 0 && (
        <>
          <Texto negrito tamanho={18} estilo={{ marginVertical: 8 }}>Já aproveitados</Texto>
          {usados.map((v) => (
            <Texto key={v.id} suave>
              {v.icone || '🎟️'} {v.titulo} — {new Date(v.utilizado_em).toLocaleDateString('pt-BR')}
            </Texto>
          ))}
        </>
      )}
    </Tela>
  );
}
