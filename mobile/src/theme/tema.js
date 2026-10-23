export const cores = {
  fundo: '#FFF7F4',
  cartao: '#FFFFFF',
  borda: '#F1E3DE',
  texto: '#2D2A32',
  suave: '#7C7480',
  primaria: '#E5484D',
  primariaClara: '#FDE8E8',
  secundaria: '#1F9E89',
  secundariaClara: '#E1F5F1',
  alerta: '#C77700',
  alertaClara: '#FFF3DC',
};

export const espaco = (n) => n * 4;

export const raio = 14;

export const STATUS_QUIZ = {
  RASCUNHO: { rotulo: 'Rascunho', cor: cores.suave },
  ABERTO: { rotulo: 'Aberto', cor: cores.secundaria },
  EM_CORRECAO: { rotulo: 'Em correção', cor: cores.alerta },
  ENCERRADO: { rotulo: 'Encerrado', cor: cores.texto },
  EXPIRADO: { rotulo: 'Expirado', cor: cores.suave },
};

export const TIPO_QUIZ = {
  PERSONALIZADO: 'Você me conhece?',
  SINTONIA: 'Sintonia',
  RETROSPECTIVA: 'Como foi sua semana?',
};
