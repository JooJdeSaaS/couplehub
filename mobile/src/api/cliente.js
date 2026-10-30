import { API_URL } from '../config';

let tokenAtual = null;

export function definirToken(token) {
  tokenAtual = token;
}

/** Erro da API no formato {erro, mensagem} (ver backend/app/main.py). */
export class ErroApi extends Error {
  constructor(status, codigo, mensagem) {
    super(mensagem);
    this.status = status;
    this.codigo = codigo;
  }
}

function montarQuery(params) {
  const pares = Object.entries(params ?? {}).filter(([, v]) => v !== undefined && v !== null && v !== '');
  if (!pares.length) return '';
  return '?' + pares.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
}

async function requisitar(caminho, { metodo = 'GET', corpo, params } = {}) {
  let resposta;
  try {
    resposta = await fetch(API_URL + caminho + montarQuery(params), {
      method: metodo,
      headers: {
        'Content-Type': 'application/json',
        ...(tokenAtual ? { Authorization: `Bearer ${tokenAtual}` } : {}),
      },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    });
  } catch {
    throw new ErroApi(0, 'SEM_CONEXAO', `Não consegui falar com a API em ${API_URL}. Ela está rodando na mesma rede?`);
  }
  const texto = await resposta.text();
  const dados = texto ? JSON.parse(texto) : null;
  if (!resposta.ok) {
    const validacao = Array.isArray(dados?.detail) ? dados.detail.map((d) => d.msg).join('\n') : null;
    throw new ErroApi(resposta.status, dados?.erro ?? 'ERRO', dados?.mensagem ?? validacao ?? 'Algo deu errado.');
  }
  return dados;
}

const get = (c, params) => requisitar(c, { params });
const post = (c, corpo) => requisitar(c, { metodo: 'POST', corpo });
const put = (c, corpo) => requisitar(c, { metodo: 'PUT', corpo });
const del = (c) => requisitar(c, { metodo: 'DELETE' });

/** Um endpoint — espelha docs/plan.md §2. */
export const Api = {
  // conta e casal
  cadastrar: (nome, email, senha) => post('/auth/cadastro', { nome, email, senha }),
  login: (email, senha) => post('/auth/login', { email, senha }),
  eu: () => get('/auth/eu'),
  meuCasal: () => get('/casais/meu'),
  criarCasal: () => post('/casais'),
  entrarNoCasal: (codigo) => post('/casais/entrar', { codigo }),
  renovarCodigo: () => post('/casais/meu/novo-codigo'),

  // quizzes e retrospectiva
  quizzes: (filtros) => get('/quizzes', filtros),
  quiz: (id) => get(`/quizzes/${id}`),
  criarQuiz: (dados) => post('/quizzes', dados),
  templateRetrospectiva: () => get('/quizzes/templates/retrospectiva'),
  responderSobreMim: (id, respostas) => put(`/quizzes/${id}/sobre-mim`, { respostas }),
  palpitar: (id, respostas) => put(`/quizzes/${id}/palpites`, { respostas }),
  corrigir: (id, correcoes) => post(`/quizzes/${id}/correcoes`, { correcoes }),
  compatibilidade: () => get('/quizzes/compatibilidade'),

  // ranking
  placarSemanal: (referencia) => get('/ranking/semanal', { referencia }),
  placarMensal: (referencia) => get('/ranking/mensal', { referencia }),
  historicoRanking: (tipo = 'SEMANAL') => get('/ranking/historico', { tipo }),

  // vales e créditos
  vales: (status) => get('/vales', { status }),
  creditos: () => get('/vales/creditos'),
  criarVale: (titulo, icone) => post('/vales', { titulo, icone: icone || null }),
  resgatarVale: (id) => post(`/vales/${id}/resgatar`),
  confirmarUso: (id) => post(`/vales/${id}/confirmar-uso`),
  cancelarVale: (id) => del(`/vales/${id}`),

  // minigame de decisão
  rodadas: () => get('/decisoes'),
  rodada: (id) => get(`/decisoes/${id}`),
  abrirRodada: (titulo, contexto = 'RESTAURANTE') => post('/decisoes', { titulo, contexto }),
  enviarOpcoes: (id, preferencias, vetos) => put(`/decisoes/${id}/opcoes`, { preferencias, vetos }),

  // dates
  dates: (filtros) => get('/dates', filtros),
  sortearDate: (ambiente) => get('/dates/sortear', { ambiente }),
  criarDate: (dados) => post('/dates', dados),
  favoritar: (id, sim) => (sim ? put(`/dates/${id}/favorito`) : del(`/dates/${id}/favorito`)),
  marcarRealizado: (id) => put(`/dates/${id}/realizado`),
};
