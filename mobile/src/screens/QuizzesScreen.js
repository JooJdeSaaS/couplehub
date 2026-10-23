import { useState } from 'react';
import { Alert, Pressable, View } from 'react-native';

import { Api, ErroApi } from '../api/cliente';
import { Botao, Cartao, Selo, Tela, Texto, Titulo, Vazio } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { STATUS_QUIZ, TIPO_QUIZ } from '../theme/tema';

export default function QuizzesScreen({ navigation }) {
  const { nomeDe } = useAuth();
  const [criando, setCriando] = useState(false);
  const { dados, carregando, recarregar } = useDados(
    async () => {
      const [quizzes, compat] = await Promise.all([Api.quizzes(), Api.compatibilidade()]);
      return { quizzes, compat };
    },
    ['quiz.'],
  );

  /** "Como foi sua semana?" a partir do template do backend (REQ-RET-004). */
  async function abrirRetrospectiva() {
    setCriando(true);
    try {
      const perguntas = await Api.templateRetrospectiva();
      const quiz = await Api.criarQuiz({ tipo: 'RETROSPECTIVA', titulo: 'Como foi minha semana', perguntas });
      navigation.navigate('Quiz', { id: quiz.id });
    } catch (e) {
      if (e instanceof ErroApi && e.codigo === 'RETROSPECTIVA_JA_EXISTE') {
        const minha = dados?.quizzes.find((q) => q.tipo === 'RETROSPECTIVA' && nomeDe(q.autor_id) === 'Você');
        if (minha) return navigation.navigate('Quiz', { id: minha.id });
      }
      Alert.alert('Ops', e.message);
    } finally {
      setCriando(false);
    }
  }

  const compat = dados?.compat;
  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub={compat?.indice != null ? `Sintonia média: ${compat.indice}% (últimos ${compat.quizzes_considerados})` : 'Quanto vocês se conhecem?'}>
        Quizzes
      </Titulo>
      <Botao titulo="Contar como foi minha semana" carregando={criando} aoPressionar={abrirRetrospectiva} />
      <Botao variante="fantasma" titulo="Criar quiz" aoPressionar={() => navigation.navigate('NovoQuiz')} />

      <View style={{ height: 12 }} />
      {dados?.quizzes?.length === 0 && <Vazio>Nenhum quiz ainda. Que tal começar pela sua semana?</Vazio>}
      {dados?.quizzes?.map((q) => {
        const st = STATUS_QUIZ[q.status];
        return (
          <Pressable key={q.id} onPress={() => navigation.navigate('Quiz', { id: q.id })} accessibilityRole="button">
            <Cartao>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <Texto suave tamanho={12}>{TIPO_QUIZ[q.tipo]}{q.semana_ref ? ` · ${q.semana_ref}` : ''}</Texto>
                <Selo texto={st.rotulo} cor={st.cor} />
              </View>
              <Texto negrito tamanho={17} estilo={{ marginTop: 6 }}>{q.titulo}</Texto>
              <Texto suave tamanho={13}>
                por {nomeDe(q.autor_id)}
                {q.percentual_sintonia != null ? ` · ${q.percentual_sintonia}% de acerto` : ''}
              </Texto>
            </Cartao>
          </Pressable>
        );
      })}
    </Tela>
  );
}
