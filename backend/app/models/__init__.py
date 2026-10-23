"""Importar este pacote registra todas as tabelas em Base.metadata."""
from .base import Base
from .casal import Casal, Usuario
from .date import DateFavorito, IdeiaDate
from .decisao import EntradaDecisao, SessaoDecisao
from .quiz import Pergunta, Quiz, Resposta
from .ranking import LancamentoPontos, Ranking
from .vale import CreditoVale, Vale

__all__ = [
    "Base", "Casal", "Usuario", "Quiz", "Pergunta", "Resposta", "IdeiaDate", "DateFavorito",
    "SessaoDecisao", "EntradaDecisao", "Vale", "CreditoVale", "LancamentoPontos", "Ranking",
]
