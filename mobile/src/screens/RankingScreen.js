import { useEffect, useState } from 'react';
import { View } from 'react-native';

import { Api } from '../api/cliente';
import { Cartao, Chips, Tela, Texto, Titulo, Vazio } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useDados } from '../hooks/tempoReal';
import { cores } from '../theme/tema';

const RESULTADO = { EMPATE: 'Empate 🤝', SEM_DISPUTA: 'Ninguém pontuou' };

export default function RankingScreen() {
  const { usuario, casal } = useAuth();
  const [tipo, setTipo] = useState('SEMANAL');
  const { dados, carregando, recarregar } = useDados(
    async () => {
      const [placar, historico] = await Promise.all([
        tipo === 'SEMANAL' ? Api.placarSemanal() : Api.placarMensal(),
        Api.historicoRanking(tipo),
      ]);
      return { placar, historico, tipo };
    },
    ['quiz.'],
  );
  // trocar Semana/Mês recarrega uma vez (o loader já lê o `tipo` novo)
  useEffect(() => {
    if (dados && dados.tipo !== tipo) recarregar();
  }, [tipo, dados, recarregar]);

  const nomePorPapel = Object.fromEntries((casal?.membros ?? []).map((m) => [m.papel, m.id === usuario.id ? 'Você' : m.nome]));
  const vencedor = (r) => RESULTADO[r] ?? `${nomePorPapel[r.slice(-1)]} venceu 🏆`;

  return (
    <Tela aoAtualizar={recarregar} atualizando={carregando}>
      <Titulo sub="Pontos de quizzes e retrospectivas">Ranking</Titulo>
      <Chips
        opcoes={[
          { valor: 'SEMANAL', rotulo: 'Semana' },
          { valor: 'MENSAL', rotulo: 'Mês' },
        ]}
        valor={tipo}
        aoMudar={setTipo}
      />
      {dados?.placar && (
        <Cartao destaque={cores.primaria}>
          <Texto suave>{dados.placar.referencia} · {dados.placar.fechado ? 'fechado' : 'em andamento'}</Texto>
          {[...dados.placar.participantes]
            .sort((a, b) => b.pontos - a.pontos)
            .map((p, i) => (
              <View key={p.usuario_id} style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 }}>
                <Texto negrito={i === 0} tamanho={18}>{i === 0 && p.pontos > 0 ? '👑 ' : ''}{p.usuario_id === usuario.id ? 'Você' : p.nome}</Texto>
                <Texto negrito tamanho={18}>{p.pontos} pts</Texto>
              </View>
            ))}
        </Cartao>
      )}
      <Texto negrito tamanho={18} estilo={{ marginVertical: 8 }}>Histórico</Texto>
      {dados?.historico?.length === 0 && <Vazio>O primeiro período ainda não fechou.</Vazio>}
      {dados?.historico?.map((r) => (
        <Cartao key={r.referencia}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
            <Texto negrito>{r.referencia}</Texto>
            <Texto>{nomePorPapel.A} {r.pontos_a} × {r.pontos_b} {nomePorPapel.B}</Texto>
          </View>
          <Texto suave tamanho={13}>{vencedor(r.resultado)}</Texto>
        </Cartao>
      ))}
    </Tela>
  );
}
