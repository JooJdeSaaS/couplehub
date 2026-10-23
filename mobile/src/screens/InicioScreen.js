import { Alert, Pressable, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Cartao, Tela, Texto, Titulo } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

function formatarFechamento(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('pt-BR', { weekday: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

/** Painel inicial: tudo que importa a no máximo 2 toques (RNF04). */
export default function InicioScreen({ navigation }) {
  const { usuario, parceiro } = useAuth();
  const { dados, carregando, recarregar } = useDados(
    async () => {
      const [placar, creditos, quizzes] = await Promise.all([Api.placarSemanal(), Api.creditos(), Api.quizzes()]);
      return { placar, creditos, quizzes };
    },
    ['quiz.', 'vale.'],
  );

  const placar = dados?.placar;
  const meus = placar?.participantes.find((p) => p.usuario_id === usuario.id)?.pontos ?? 0;
  const dele = placar?.participantes.find((p) => p.usuario_id !== usuario.id)?.pontos ?? 0;
  const pendentes = (dados?.quizzes ?? []).filter((q) => ['RASCUNHO', 'ABERTO', 'EM_CORRECAO'].includes(q.status)).length;
  const lider = placar?.lider_id === usuario.id ? 'Você está na frente! 🏆' : placar?.lider_id ? `${parceiro?.nome} está na frente` : 'Empatados por enquanto';

  async function sugerirDateEmCasa() {
    try {
      const ideia = await Api.sortearDate('EM_CASA');
      Alert.alert('Que tal hoje?', `${ideia.titulo}\n\n${ideia.descricao ?? ''}`);
    } catch (e) {
      Alert.alert('Ops', e.message);
    }
  }

  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub={`Você e ${parceiro?.nome ?? 'seu par'}`}>Oi, {usuario.nome} 👋</Titulo>

      <Pressable onPress={() => navigation.navigate('Ranking')} accessibilityRole="button">
        <Cartao destaque={cores.primaria}>
          <Texto suave>Placar da semana {placar ? `· ${placar.referencia}` : ''}</Texto>
          <View style={{ flexDirection: 'row', justifyContent: 'space-around', marginVertical: 12 }}>
            <View style={{ alignItems: 'center' }}>
              <Texto negrito tamanho={34}>{meus}</Texto>
              <Texto suave>Você</Texto>
            </View>
            <Texto negrito tamanho={28} cor={cores.suave}>×</Texto>
            <View style={{ alignItems: 'center' }}>
              <Texto negrito tamanho={34}>{dele}</Texto>
              <Texto suave>{parceiro?.nome}</Texto>
            </View>
          </View>
          <Texto>{lider}</Texto>
          {placar?.fecha_em ? <Texto suave tamanho={13}>Fecha {formatarFechamento(placar.fecha_em)}</Texto> : null}
        </Cartao>
      </Pressable>

      {dados?.creditos?.length ? (
        <Pressable onPress={() => navigation.navigate('Vales')} accessibilityRole="button">
          <Cartao destaque={cores.secundaria}>
            <Texto negrito>🎟️ Você tem {dados.creditos.length} crédito(s) de vale!</Texto>
            <Texto suave>Toque para escolher um mimo do cardápio de {parceiro?.nome}.</Texto>
          </Cartao>
        </Pressable>
      ) : null}

      <Cartao>
        <Texto negrito>Atalhos</Texto>
        <Botao titulo={`Quizzes ${pendentes ? `(${pendentes} pendente${pendentes > 1 ? 's' : ''})` : ''}`} aoPressionar={() => navigation.navigate('Quizzes')} />
        <Botao variante="secundario" titulo="Onde vamos? 🎲" aoPressionar={() => navigation.navigate('Decidir')} />
        <Botao variante="fantasma" titulo="Ideia de date em casa 🏠" aoPressionar={sugerirDateEmCasa} />
      </Cartao>
    </Tela>
  );
}
