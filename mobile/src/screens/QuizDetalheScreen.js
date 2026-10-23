import { useState } from 'react';
import { Alert, View } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Carregando, Cartao, Chips, Selo, Tela, Texto, Titulo } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { cores, STATUS_QUIZ, TIPO_QUIZ } from '../theme/tema';

const COR_RESULTADO = { ACERTO: cores.secundaria, PARCIAL: cores.alerta, ERRO: cores.primaria, PENDENTE: cores.suave };
const ROTULO_RESULTADO = { ACERTO: 'Acertou', PARCIAL: 'Quase', ERRO: 'Errou', PENDENTE: 'Aguardando correção' };

/** Entrada conforme o formato da pergunta (REQ-QZ-005). */
function EntradaResposta({ pergunta, valor, aoMudar }) {
  switch (pergunta.formato) {
    case 'MULTIPLA_ESCOLHA':
      return <Chips opcoes={pergunta.opcoes.map((o) => ({ valor: o, rotulo: o }))} valor={valor} aoMudar={aoMudar} />;
    case 'VERDADEIRO_FALSO':
      return (
        <Chips
          opcoes={[
            { valor: 'VERDADEIRO', rotulo: 'Verdadeiro' },
            { valor: 'FALSO', rotulo: 'Falso' },
          ]}
          valor={valor}
          aoMudar={aoMudar}
        />
      );
    case 'ESCALA':
      return <Chips opcoes={[1, 2, 3, 4, 5].map((n) => ({ valor: String(n), rotulo: String(n) }))} valor={valor} aoMudar={aoMudar} />;
    default:
      return <Campo value={valor ?? ''} onChangeText={aoMudar} placeholder="Sua resposta" maxLength={280} multiline />;
  }
}

function Resultado({ palpite }) {
  if (!palpite?.resultado) return null;
  return (
    <Selo
      texto={`${ROTULO_RESULTADO[palpite.resultado]}${palpite.pontos_obtidos != null ? ` · +${palpite.pontos_obtidos}` : ''}`}
      cor={COR_RESULTADO[palpite.resultado]}
    />
  );
}

export default function QuizDetalheScreen({ route }) {
  const { id } = route.params;
  const { parceiro } = useAuth();
  const [respostas, setRespostas] = useState({});
  const [enviando, setEnviando] = useState(false);
  const { dados: quiz, recarregar } = useDados(() => Api.quiz(id), ['quiz.']);

  if (!quiz) return <Carregando />;

  const acoes = quiz.acoes_disponiveis;
  const modo = acoes.includes('RESPONDER_SOBRE_SI') ? 'SOBRE_SI' : acoes.includes('PALPITAR') ? 'PALPITE' : null;
  const completo = quiz.perguntas.every((p) => (respostas[p.id] ?? '').toString().trim());

  async function enviar() {
    setEnviando(true);
    try {
      const lista = quiz.perguntas.map((p) => ({ pergunta_id: p.id, valor: String(respostas[p.id]) }));
      await (modo === 'SOBRE_SI' ? Api.responderSobreMim(id, lista) : Api.palpitar(id, lista));
      setRespostas({});
      await recarregar();
    } catch (e) {
      Alert.alert('Ops', e.message);
    } finally {
      setEnviando(false);
    }
  }

  async function corrigir(respostaId, resultado) {
    try {
      await Api.corrigir(id, [{ resposta_id: respostaId, resultado }]);
      await recarregar();
    } catch (e) {
      Alert.alert('Ops', e.message);
    }
  }

  const st = STATUS_QUIZ[quiz.status];
  const instrucao =
    modo === 'SOBRE_SI'
      ? 'Responda sobre você. Isso vira o gabarito — só aparece para o seu par depois que o quiz encerrar.'
      : modo === 'PALPITE'
        ? `Tente adivinhar o que ${parceiro?.nome} respondeu. Envio único!`
        : acoes.includes('CORRIGIR')
          ? `Confira os palpites de ${parceiro?.nome} e diga se acertou.`
          : quiz.status === 'ENCERRADO'
            ? `Resultado: ${quiz.percentual_sintonia}% de sintonia.`
            : `Aguardando ${parceiro?.nome}…`;

  return (
    <Tela aoAtualizar={recarregar}>
      <Texto suave tamanho={12}>{TIPO_QUIZ[quiz.tipo]}</Texto>
      <Titulo sub={instrucao}>{quiz.titulo}</Titulo>
      <Selo texto={st.rotulo} cor={st.cor} />
      <View style={{ height: 12 }} />

      {quiz.perguntas.map((p) => {
        const pendenteDeMim = p.palpite_do_parceiro?.resultado === 'PENDENTE';
        return (
          <Cartao key={p.id}>
            <Texto suave tamanho={12}>{p.ordem}. · {p.pontos} pts</Texto>
            <Texto negrito estilo={{ marginBottom: 8 }}>{p.enunciado}</Texto>

            {modo && <EntradaResposta pergunta={p} valor={respostas[p.id]} aoMudar={(v) => setRespostas((r) => ({ ...r, [p.id]: v }))} />}

            {!modo && p.minha_resposta ? <Texto suave>Sobre mim: {p.minha_resposta}</Texto> : null}
            {!modo && p.meu_palpite ? (
              <View style={{ marginTop: 4 }}>
                <Texto>Meu palpite: {p.meu_palpite.valor}</Texto>
                <Resultado palpite={p.meu_palpite} />
              </View>
            ) : null}
            {p.gabarito_do_parceiro ? <Texto suave>Resposta de {parceiro?.nome}: {p.gabarito_do_parceiro}</Texto> : null}

            {p.palpite_do_parceiro && (
              <View style={{ marginTop: 8 }}>
                <Texto>Palpite de {parceiro?.nome}: {p.palpite_do_parceiro.valor}</Texto>
                {pendenteDeMim ? (
                  <View style={{ flexDirection: 'row', gap: 8, marginTop: 6 }}>
                    <Botao pequeno variante="secundario" titulo="Acertou" aoPressionar={() => corrigir(p.palpite_do_parceiro.resposta_id, 'ACERTO')} />
                    <Botao pequeno titulo="Quase" aoPressionar={() => corrigir(p.palpite_do_parceiro.resposta_id, 'PARCIAL')} />
                    <Botao pequeno variante="fantasma" titulo="Errou" aoPressionar={() => corrigir(p.palpite_do_parceiro.resposta_id, 'ERRO')} />
                  </View>
                ) : (
                  <Resultado palpite={p.palpite_do_parceiro} />
                )}
              </View>
            )}
          </Cartao>
        );
      })}

      {modo && (
        <Botao
          titulo={modo === 'SOBRE_SI' ? 'Salvar minhas respostas' : 'Enviar palpites'}
          desabilitado={!completo}
          carregando={enviando}
          aoPressionar={enviar}
        />
      )}
    </Tela>
  );
}
