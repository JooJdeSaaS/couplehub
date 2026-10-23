"""Normalização de texto usada para comparar respostas e opções de decisão."""
import re
import unicodedata

_PONTUACAO = re.compile(r"[^\w\s]", re.UNICODE)
_ESPACOS = re.compile(r"\s+")


def normalizar(texto: str) -> str:
    """'  Comida JAPONESA!! ' -> 'comida japonesa'; 'Pão' -> 'pao'."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    sem_pontuacao = _PONTUACAO.sub(" ", sem_acento.casefold())
    return _ESPACOS.sub(" ", sem_pontuacao).strip()
