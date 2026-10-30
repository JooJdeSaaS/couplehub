-- CoupleHUB — DDL de referência (SQLite)
-- Espelha app/models/*.py. Em execução o banco é criado pelo SQLAlchemy
-- (Base.metadata.create_all); este arquivo serve para estudo, revisão e
-- para abrir o modelo em ferramentas como DB Browser / dbdiagram.
-- Datas/horas: TEXT ISO-8601 em UTC. IDs: UUID v4 em TEXT.

PRAGMA foreign_keys = ON;

-- ============================================================ CONTA E CASAL
CREATE TABLE casal (
    id                          VARCHAR(36) PRIMARY KEY,
    status                      VARCHAR(32) NOT NULL DEFAULT 'AGUARDANDO_PARCEIRO'
                                CHECK (status IN ('AGUARDANDO_PARCEIRO', 'ATIVO', 'ENCERRADO')),
    codigo_convite              VARCHAR(8) UNIQUE,              -- uso único; NULL após o pareamento
    convite_expira_em           DATETIME,
    data_inicio_relacionamento  DATE,
    pareado_em                  DATETIME,
    criado_em                   DATETIME NOT NULL
);

CREATE TABLE usuario (
    id             VARCHAR(36) PRIMARY KEY,
    casal_id       VARCHAR(36) REFERENCES casal(id) ON DELETE SET NULL,
    papel          VARCHAR(32) CHECK (papel IN ('A', 'B')),
    nome           VARCHAR(80)  NOT NULL,
    email          VARCHAR(254) NOT NULL UNIQUE,
    senha_hash     VARCHAR(255),                                -- NULL em login social
    provedor_auth  VARCHAR(32) NOT NULL DEFAULT 'EMAIL' CHECK (provedor_auth IN ('EMAIL', 'GOOGLE', 'APPLE')),
    avatar_emoji   VARCHAR(8),
    criado_em      DATETIME NOT NULL,
    CONSTRAINT uq_usuario_casal_papel UNIQUE (casal_id, papel),    -- no máximo 1 "A" e 1 "B" por casal
    CONSTRAINT ck_usuario_papel_com_casal CHECK ((casal_id IS NULL) = (papel IS NULL))
);
CREATE INDEX ix_usuario_casal_id ON usuario (casal_id);

-- ============================================================ QUIZZES
CREATE TABLE quiz (
    id                   VARCHAR(36) PRIMARY KEY,
    casal_id             VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    autor_id             VARCHAR(36) NOT NULL REFERENCES usuario(id),
    tipo                 VARCHAR(32) NOT NULL CHECK (tipo IN ('PERSONALIZADO', 'SINTONIA', 'RETROSPECTIVA')),
    titulo               VARCHAR(120) NOT NULL,
    status               VARCHAR(32) NOT NULL
                         CHECK (status IN ('RASCUNHO', 'ABERTO', 'EM_CORRECAO', 'ENCERRADO', 'EXPIRADO')),
    semana_ref           VARCHAR(8),                            -- '2026-W43' (só retrospectiva)
    prazo                DATETIME,
    percentual_sintonia  FLOAT,                                 -- snapshot ao encerrar
    criado_em            DATETIME NOT NULL,
    publicado_em         DATETIME,
    encerrado_em         DATETIME,
    CONSTRAINT ck_quiz_semana_so_retrospectiva CHECK ((tipo = 'RETROSPECTIVA') = (semana_ref IS NOT NULL))
);
CREATE UNIQUE INDEX uq_retrospectiva_autor_semana ON quiz (autor_id, semana_ref) WHERE tipo = 'RETROSPECTIVA';
CREATE INDEX ix_quiz_casal_status ON quiz (casal_id, status);

CREATE TABLE pergunta (
    id         VARCHAR(36) PRIMARY KEY,
    quiz_id    VARCHAR(36) NOT NULL REFERENCES quiz(id) ON DELETE CASCADE,
    ordem      INTEGER NOT NULL,
    enunciado  VARCHAR(280) NOT NULL,
    formato    VARCHAR(32) NOT NULL
               CHECK (formato IN ('MULTIPLA_ESCOLHA', 'VERDADEIRO_FALSO', 'ESCALA', 'TEXTO_LIVRE')),
    opcoes     JSON,                                            -- só múltipla escolha
    pontos     INTEGER NOT NULL DEFAULT 10,
    CONSTRAINT uq_pergunta_ordem UNIQUE (quiz_id, ordem),
    CONSTRAINT ck_pergunta_pontos CHECK (pontos BETWEEN 2 AND 50)
);

CREATE TABLE resposta (
    id                VARCHAR(36) PRIMARY KEY,
    pergunta_id       VARCHAR(36) NOT NULL REFERENCES pergunta(id) ON DELETE CASCADE,
    usuario_id        VARCHAR(36) NOT NULL REFERENCES usuario(id),
    natureza          VARCHAR(32) NOT NULL CHECK (natureza IN ('SOBRE_SI', 'PALPITE')),
    valor             TEXT NOT NULL,                            -- CIFRADO (Fernet) em repouso
    resultado         VARCHAR(32) CHECK (resultado IN ('PENDENTE', 'ACERTO', 'PARCIAL', 'ERRO')),
    pontos_obtidos    INTEGER,
    corrigida_por_id  VARCHAR(36) REFERENCES usuario(id),       -- NULL = correção automática/sistema
    respondida_em     DATETIME NOT NULL,
    corrigida_em      DATETIME,
    CONSTRAINT uq_resposta_unica UNIQUE (pergunta_id, usuario_id, natureza),
    CONSTRAINT ck_resposta_sobre_si_sem_nota
        CHECK (natureza = 'PALPITE' OR (resultado IS NULL AND pontos_obtidos IS NULL))
);
CREATE INDEX ix_resposta_pergunta_id ON resposta (pergunta_id);

-- ============================================================ PONTOS E RANKING
CREATE TABLE lancamento_pontos (                                -- livro-razão, só INSERT
    id             VARCHAR(36) PRIMARY KEY,
    casal_id       VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    usuario_id     VARCHAR(36) NOT NULL REFERENCES usuario(id),
    pontos         INTEGER NOT NULL,
    origem         VARCHAR(32) NOT NULL
                   CHECK (origem IN ('QUIZ_PALPITE', 'QUIZ_BONUS_PERFEITO', 'RETROSPECTIVA_PARTICIPACAO')),
    referencia_id  VARCHAR(36) NOT NULL,                        -- id do quiz que gerou os pontos
    semana_ref     VARCHAR(8) NOT NULL,                         -- '2026-W43'
    mes_ref        VARCHAR(7) NOT NULL,                         -- '2026-10' (mês da quinta-feira)
    descricao      VARCHAR(120) NOT NULL,
    criado_em      DATETIME NOT NULL,
    CONSTRAINT uq_lancamento_idempotente UNIQUE (usuario_id, origem, referencia_id),
    CONSTRAINT ck_lancamento_pontos_positivos CHECK (pontos >= 0)
);
CREATE INDEX ix_lancamento_casal_semana ON lancamento_pontos (casal_id, semana_ref);
CREATE INDEX ix_lancamento_casal_mes ON lancamento_pontos (casal_id, mes_ref);

CREATE TABLE ranking (                                          -- placar de períodos FECHADOS
    id            VARCHAR(36) PRIMARY KEY,
    casal_id      VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    tipo_periodo  VARCHAR(32) NOT NULL CHECK (tipo_periodo IN ('SEMANAL', 'MENSAL')),
    referencia    VARCHAR(8) NOT NULL,                          -- '2026-W43' ou '2026-10'
    data_inicio   DATE NOT NULL,
    data_fim      DATE NOT NULL,
    pontos_a      INTEGER NOT NULL,
    pontos_b      INTEGER NOT NULL,
    resultado     VARCHAR(32) NOT NULL CHECK (resultado IN ('VITORIA_A', 'VITORIA_B', 'EMPATE', 'SEM_DISPUTA')),
    fechado_em    DATETIME NOT NULL,
    CONSTRAINT uq_ranking_periodo UNIQUE (casal_id, tipo_periodo, referencia)
);

-- ============================================================ VALES
CREATE TABLE credito_vale (
    id            VARCHAR(36) PRIMARY KEY,
    casal_id      VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    usuario_id    VARCHAR(36) NOT NULL REFERENCES usuario(id),
    origem        VARCHAR(32) NOT NULL
                  CHECK (origem IN ('VENCEDOR_SEMANA', 'VENCEDOR_MES', 'VENCEDOR_QUIZ_SINTONIA')),
    referencia    VARCHAR(40) NOT NULL,
    status        VARCHAR(32) NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'CONSUMIDO', 'EXPIRADO')),
    expira_em     DATETIME NOT NULL,
    criado_em     DATETIME NOT NULL,
    consumido_em  DATETIME,
    CONSTRAINT uq_credito_origem UNIQUE (usuario_id, origem, referencia)
);
CREATE INDEX ix_credito_usuario_status ON credito_vale (usuario_id, status);

CREATE TABLE vale (
    id                VARCHAR(36) PRIMARY KEY,
    casal_id          VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    criador_id        VARCHAR(36) NOT NULL REFERENCES usuario(id),  -- quem oferece e cumpre
    titulo            VARCHAR(80) NOT NULL,
    descricao         VARCHAR(280),
    icone             VARCHAR(8),
    status            VARCHAR(32) NOT NULL DEFAULT 'DISPONIVEL'
                      CHECK (status IN ('DISPONIVEL', 'RESGATADO', 'UTILIZADO', 'CANCELADO')),
    resgatado_por_id  VARCHAR(36) REFERENCES usuario(id),
    credito_id        VARCHAR(36) UNIQUE REFERENCES credito_vale(id),
    criado_em         DATETIME NOT NULL,
    resgatado_em      DATETIME,
    utilizado_em      DATETIME,
    cancelado_em      DATETIME,
    CONSTRAINT ck_vale_resgate_coerente CHECK ((status IN ('DISPONIVEL', 'CANCELADO')) = (resgatado_por_id IS NULL)),
    CONSTRAINT ck_vale_nao_proprio CHECK (resgatado_por_id IS NULL OR resgatado_por_id <> criador_id)
);
CREATE INDEX ix_vale_casal_status ON vale (casal_id, status);

-- ============================================================ MINIGAME DE DECISÃO
CREATE TABLE sessao_decisao (
    id                VARCHAR(36) PRIMARY KEY,
    casal_id          VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    criado_por_id     VARCHAR(36) NOT NULL REFERENCES usuario(id),
    titulo            VARCHAR(80) NOT NULL,
    contexto          VARCHAR(32) NOT NULL CHECK (contexto IN ('RESTAURANTE', 'ROLE', 'OUTRO')),
    status            VARCHAR(32) NOT NULL DEFAULT 'COLETANDO' CHECK (status IN ('COLETANDO', 'RESOLVIDA', 'CANCELADA')),
    tipo_resultado    VARCHAR(32) CHECK (tipo_resultado IN ('MATCH', 'PONDERADO', 'CARA_OU_COROA')),
    resultado_rotulo  VARCHAR(60),
    favorecido_id     VARCHAR(36) REFERENCES usuario(id),
    escolhedor_id     VARCHAR(36) REFERENCES usuario(id),
    justificativa     VARCHAR(280),
    semente           INTEGER,                                  -- reproduz o sorteio
    criado_em         DATETIME NOT NULL,
    resolvida_em      DATETIME
);
CREATE INDEX ix_decisao_casal_status ON sessao_decisao (casal_id, status);

CREATE TABLE entrada_decisao (
    id          VARCHAR(36) PRIMARY KEY,
    sessao_id   VARCHAR(36) NOT NULL REFERENCES sessao_decisao(id) ON DELETE CASCADE,
    usuario_id  VARCHAR(36) NOT NULL REFERENCES usuario(id),
    rotulo      VARCHAR(60) NOT NULL,
    peso        INTEGER,
    veto        BOOLEAN NOT NULL DEFAULT 0,
    CONSTRAINT ck_entrada_peso CHECK ((veto = 1 AND peso IS NULL) OR (veto = 0 AND peso BETWEEN 1 AND 5))
);
CREATE INDEX ix_entrada_sessao_usuario ON entrada_decisao (sessao_id, usuario_id);

-- ============================================================ IDEIAS DE DATES
CREATE TABLE ideia_date (                                       -- entidade "Date"
    id             VARCHAR(36) PRIMARY KEY,
    casal_id       VARCHAR(36) REFERENCES casal(id) ON DELETE CASCADE,   -- NULL = catálogo global
    criado_por_id  VARCHAR(36) REFERENCES usuario(id) ON DELETE SET NULL,
    titulo         VARCHAR(100) NOT NULL,
    descricao      VARCHAR(500),
    ambiente       VARCHAR(32) NOT NULL CHECK (ambiente IN ('EM_CASA', 'FORA_DE_CASA')),
    categoria      VARCHAR(32) NOT NULL
                   CHECK (categoria IN ('GASTRONOMIA', 'CULTURA', 'AVENTURA', 'RELAXAMENTO', 'CRIATIVO', 'ESPORTE', 'ROMANTICO')),
    custo          VARCHAR(32) NOT NULL DEFAULT 'BAIXO' CHECK (custo IN ('GRATIS', 'BAIXO', 'MEDIO', 'ALTO')),
    duracao_min    INTEGER,
    criado_em      DATETIME NOT NULL
);
CREATE INDEX ix_ideia_date_casal_id ON ideia_date (casal_id);
CREATE INDEX ix_date_filtros ON ideia_date (ambiente, categoria);

CREATE TABLE date_favorito (
    casal_id       VARCHAR(36) NOT NULL REFERENCES casal(id) ON DELETE CASCADE,
    ideia_id       VARCHAR(36) NOT NULL REFERENCES ideia_date(id) ON DELETE CASCADE,
    favoritado_em  DATETIME NOT NULL,
    realizado_em   DATETIME,
    PRIMARY KEY (casal_id, ideia_id)
);
