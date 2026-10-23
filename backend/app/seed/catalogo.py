"""Dados iniciais: catálogo global de dates e template da retrospectiva."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import AmbienteDate as A
from app.domain.enums import CategoriaDate as C
from app.domain.enums import CustoDate as G
from app.domain.enums import FormatoPergunta as F
from app.models import IdeiaDate

# (título, descrição, ambiente, categoria, custo, duração em minutos)
CATALOGO_DATES = [
    ("Noite de fondue caseiro", "Queijo, chocolate e frutas. Sem pressa.", A.EM_CASA, C.GASTRONOMIA, G.MEDIO, 120),
    ("Cozinhar um prato de um país sorteado", "Sorteiem um país e aprendam uma receita típica juntos.", A.EM_CASA, C.GASTRONOMIA, G.BAIXO, 120),
    ("Maratona de filmes com tema", "Cada um escolhe um filme dentro de um tema surpresa.", A.EM_CASA, C.RELAXAMENTO, G.GRATIS, 240),
    ("Spa em casa", "Máscara facial, massagem e playlist calma.", A.EM_CASA, C.RELAXAMENTO, G.BAIXO, 90),
    ("Noite de jogos de tabuleiro", "Quem perder lava a louça.", A.EM_CASA, C.CRIATIVO, G.GRATIS, 120),
    ("Pintura a dois", "Pintem o retrato um do outro em 30 minutos e comparem.", A.EM_CASA, C.CRIATIVO, G.BAIXO, 60),
    ("Piquenique na sala", "Toalha no chão, comidinhas e luz baixa.", A.EM_CASA, C.ROMANTICO, G.BAIXO, 90),
    ("Cápsula do tempo do casal", "Escrevam cartas para abrir daqui a um ano.", A.EM_CASA, C.ROMANTICO, G.GRATIS, 60),
    ("Karaokê na sala", "Playlist de músicas que marcaram vocês.", A.EM_CASA, C.CRIATIVO, G.GRATIS, 90),
    ("Treino em dupla", "Um treino funcional de 30 minutos, um motivando o outro.", A.EM_CASA, C.ESPORTE, G.GRATIS, 45),
    ("Piquenique no parque", "Cesta, canga e um livro para ler em voz alta.", A.FORA_DE_CASA, C.ROMANTICO, G.BAIXO, 180),
    ("Restaurante que nenhum dos dois conhece", "Usem o minigame de decisão para escolher a culinária.", A.FORA_DE_CASA, C.GASTRONOMIA, G.MEDIO, 120),
    ("Feira de rua e pastel", "Passeio de domingo de manhã.", A.FORA_DE_CASA, C.GASTRONOMIA, G.BAIXO, 120),
    ("Museu ou exposição gratuita", "Cada um escolhe a obra favorita e explica por quê.", A.FORA_DE_CASA, C.CULTURA, G.GRATIS, 150),
    ("Sessão de cinema no meio da semana", "Ingresso mais barato e sala vazia.", A.FORA_DE_CASA, C.CULTURA, G.MEDIO, 150),
    ("Trilha leve com mirante", "Levem lanche e cheguem para o pôr do sol.", A.FORA_DE_CASA, C.AVENTURA, G.GRATIS, 240),
    ("Aula experimental de dança", "Forró, salsa ou zouk — vale errar o passo.", A.FORA_DE_CASA, C.ESPORTE, G.MEDIO, 90),
    ("Pedalar na ciclovia", "Aluguem bikes compartilhadas e explorem um bairro novo.", A.FORA_DE_CASA, C.ESPORTE, G.BAIXO, 120),
    ("Escape room", "Teste de comunicação sob pressão.", A.FORA_DE_CASA, C.AVENTURA, G.ALTO, 90),
    ("Turistar na própria cidade", "Façam o roteiro que um turista faria.", A.FORA_DE_CASA, C.CULTURA, G.BAIXO, 300),
]

TEMPLATE_RETROSPECTIVA = [
    {"enunciado": "Qual foi o melhor momento da minha semana?", "formato": F.TEXTO_LIVRE, "pontos": 15},
    {"enunciado": "O que mais me estressou nesta semana?", "formato": F.TEXTO_LIVRE, "pontos": 15},
    {"enunciado": "De 1 a 5, como foi minha semana?", "formato": F.ESCALA, "pontos": 10},
    {"enunciado": "Comi algo diferente ou especial esta semana?", "formato": F.VERDADEIRO_FALSO, "pontos": 5},
    {"enunciado": "Qual foi o principal assunto das nossas conversas?", "formato": F.TEXTO_LIVRE, "pontos": 10},
]


def popular_catalogo(db: Session) -> int:
    """Insere o catálogo global uma única vez. Devolve quantos itens criou."""
    existentes = db.scalar(select(func.count(IdeiaDate.id)).where(IdeiaDate.casal_id.is_(None)))
    if existentes:
        return 0
    db.add_all(
        IdeiaDate(titulo=t, descricao=d, ambiente=a, categoria=c, custo=g, duracao_min=m)
        for t, d, a, c, g, m in CATALOGO_DATES
    )
    db.commit()
    return len(CATALOGO_DATES)
