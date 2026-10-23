import { useState } from 'react';
import { Alert, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Chips, Tela, Texto, Titulo } from '../components/ui';

const FORMATOS = [
  { valor: 'MULTIPLA_ESCOLHA', rotulo: 'Opções' },
  { valor: 'VERDADEIRO_FALSO', rotulo: 'V ou F' },
  { valor: 'ESCALA', rotulo: '1 a 5' },
  { valor: 'TEXTO_LIVRE', rotulo: 'Texto' },
];
const TIPOS = [
  { valor: 'PERSONALIZADO', rotulo: 'Sobre mim' },
  { valor: 'SINTONIA', rotulo: 'Sintonia (os dois)' },
];
const novaPergunta = () => ({ enunciado: '', formato: 'MULTIPLA_ESCOLHA', opcoes: '', pontos: '10' });

/** Construtor básico de quiz (REQ-QZ-002). */
export default function NovoQuizScreen({ navigation }) {
  const [tipo, setTipo] = useState('PERSONALIZADO');
  const [titulo, setTitulo] = useState('');
  const [perguntas, setPerguntas] = useState([novaPergunta()]);
  const [salvando, setSalvando] = useState(false);

  const alterar = (i, campo, valor) => setPerguntas((ps) => ps.map((p, j) => (j === i ? { ...p, [campo]: valor } : p)));

  async function salvar() {
    setSalvando(true);
    try {
      const quiz = await Api.criarQuiz({
        tipo,
        titulo,
        perguntas: perguntas.map((p) => ({
          enunciado: p.enunciado,
          formato: p.formato,
          pontos: Number(p.pontos) || 10,
          opcoes: p.formato === 'MULTIPLA_ESCOLHA' ? p.opcoes.split(',').map((o) => o.trim()).filter(Boolean) : null,
        })),
      });
      navigation.replace('Quiz', { id: quiz.id });
    } catch (e) {
      Alert.alert('Revise o quiz', e.message);
    } finally {
      setSalvando(false);
    }
  }

  return (
    <Tela>
      <Titulo sub={tipo === 'SINTONIA' ? 'Os dois respondem sobre si e palpitam sobre o outro.' : 'Você responde; seu par tenta adivinhar.'}>
        Novo quiz
      </Titulo>
      <Chips opcoes={TIPOS} valor={tipo} aoMudar={setTipo} />
      <Campo rotulo="Título" value={titulo} onChangeText={setTitulo} placeholder="Ex.: Você me conhece mesmo?" />

      {perguntas.map((p, i) => (
        <Cartao key={i}>
          <Texto negrito>Pergunta {i + 1}</Texto>
          <Campo value={p.enunciado} onChangeText={(v) => alterar(i, 'enunciado', v)} placeholder="Qual é a minha comida favorita?" />
          <Chips opcoes={FORMATOS} valor={p.formato} aoMudar={(v) => alterar(i, 'formato', v)} />
          {p.formato === 'MULTIPLA_ESCOLHA' && (
            <Campo rotulo="Opções (separadas por vírgula)" value={p.opcoes} onChangeText={(v) => alterar(i, 'opcoes', v)} placeholder="Japonesa, Italiana, Árabe" />
          )}
          <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
            <View style={{ width: 110 }}>
              <Campo rotulo="Pontos (2–50)" value={p.pontos} onChangeText={(v) => alterar(i, 'pontos', v)} keyboardType="number-pad" />
            </View>
            {perguntas.length > 1 && (
              <Botao pequeno variante="fantasma" titulo="Remover" aoPressionar={() => setPerguntas((ps) => ps.filter((_, j) => j !== i))} />
            )}
          </View>
        </Cartao>
      ))}

      <Botao variante="fantasma" titulo="+ Pergunta" desabilitado={perguntas.length >= 15} aoPressionar={() => setPerguntas((ps) => [...ps, novaPergunta()])} />
      <Botao titulo="Criar quiz" carregando={salvando} desabilitado={!titulo.trim()} aoPressionar={salvar} />
    </Tela>
  );
}
