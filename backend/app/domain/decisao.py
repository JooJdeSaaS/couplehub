"""Minigame "Onde vamos?" — cruzamento secreto de preferências com vetos (REQ-DEC-*).

Algoritmo (executado quando os DOIS parceiros enviaram suas listas):
1. Normaliza rótulos ("Japonês", "japones " -> "japones").
2. Remove de ambas as listas tudo que QUALQUER um vetou.
3. Se sobrar opção em comum -> MATCH. Desempate: maior soma de pesos, depois
   menor diferença de pesos (opção mais equilibrada), depois sorteio.
4. Sem opção em comum -> sorteio PONDERADO pelos pesos entre as opções restantes.
   Regra de equilíbrio: se o último sorteio ponderado favoreceu um parceiro, as
   opções dele entram com metade do peso nesta rodada.
5. Tudo vetado -> CARA_OU_COROA decide QUEM escolhe (fallback do RF03).

O gerador aleatório é injetado: o serviço grava a semente na sessão, o que torna
o resultado reproduzível e auditável.
"""
import random
from dataclasses import dataclass

from .enums import Papel, TipoResultadoDecisao
from .erros import RegraViolada
from .texto import normalizar

MAX_PREFERENCIAS = 5
MAX_VETOS = 2
PESO_MIN, PESO_MAX = 1, 5
TAMANHO_ROTULO = (2, 60)
FATOR_EQUILIBRIO = 0.5


@dataclass(frozen=True)
class Preferencia:
    rotulo: str
    peso: int = 3


@dataclass(frozen=True)
class Submissao:
    preferencias: tuple[Preferencia, ...]
    vetos: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoDecisao:
    tipo: TipoResultadoDecisao
    rotulo: str | None
    favorecido: Papel | None
    escolhedor: Papel | None
    comuns: tuple[str, ...]
    vetadas: tuple[str, ...]
    justificativa: str


def validar_submissao(sub: Submissao) -> None:
    if not 1 <= len(sub.preferencias) <= MAX_PREFERENCIAS:
        raise RegraViolada(f"Envie de 1 a {MAX_PREFERENCIAS} preferências.", "QTD_PREFERENCIAS")
    if len(sub.vetos) > MAX_VETOS:
        raise RegraViolada(f"Máximo de {MAX_VETOS} vetos por rodada.", "QTD_VETOS")
    minimo, maximo = TAMANHO_ROTULO
    for rotulo in [p.rotulo for p in sub.preferencias] + list(sub.vetos):
        if not minimo <= len(rotulo.strip()) <= maximo:
            raise RegraViolada(f"Cada opção deve ter de {minimo} a {maximo} caracteres.", "ROTULO_INVALIDO")
    for p in sub.preferencias:
        if not PESO_MIN <= p.peso <= PESO_MAX:
            raise RegraViolada(f"Peso vai de {PESO_MIN} a {PESO_MAX}.", "PESO_INVALIDO")
    sugeridas = {normalizar(p.rotulo) for p in sub.preferencias}
    if sugeridas & {normalizar(v) for v in sub.vetos}:
        raise RegraViolada("Você vetou uma opção que você mesmo sugeriu.", "VETO_CONTRADITORIO")


def _mapa(sub: Submissao, vetados: set[str]) -> dict[str, tuple[str, int]]:
    """chave normalizada -> (rótulo original, maior peso), sem os vetados."""
    mapa: dict[str, tuple[str, int]] = {}
    for p in sub.preferencias:
        chave = normalizar(p.rotulo)
        if chave in vetados:
            continue
        if chave not in mapa or p.peso > mapa[chave][1]:
            mapa[chave] = (p.rotulo.strip(), p.peso)
    return mapa


def decidir(
    sub_a: Submissao,
    sub_b: Submissao,
    rng: random.Random,
    ultimo_favorecido: Papel | None = None,
) -> ResultadoDecisao:
    validar_submissao(sub_a)
    validar_submissao(sub_b)

    vetados = {normalizar(v) for v in sub_a.vetos + sub_b.vetos}
    sugeridas = {normalizar(p.rotulo): p.rotulo.strip() for p in sub_a.preferencias + sub_b.preferencias}
    vetadas = tuple(sorted(sugeridas[k] for k in sugeridas if k in vetados))
    mapa_a, mapa_b = _mapa(sub_a, vetados), _mapa(sub_b, vetados)

    comuns = sorted(set(mapa_a) & set(mapa_b))
    if comuns:
        def criterio(k: str) -> tuple[int, int]:
            pa, pb = mapa_a[k][1], mapa_b[k][1]
            return (-(pa + pb), abs(pa - pb))

        melhor = min(criterio(k) for k in comuns)
        chave = rng.choice([k for k in comuns if criterio(k) == melhor])
        rotulo = mapa_a[chave][0]
        return ResultadoDecisao(
            TipoResultadoDecisao.MATCH, rotulo, None, None,
            tuple(mapa_a[k][0] for k in comuns), vetadas,
            f"Deu match! '{rotulo}' estava na lista dos dois "
            f"(pesos {mapa_a[chave][1]} + {mapa_b[chave][1]}).",
        )

    candidatos = [(mapa_a[k][0], Papel.A, mapa_a[k][1]) for k in sorted(mapa_a)]
    candidatos += [(mapa_b[k][0], Papel.B, mapa_b[k][1]) for k in sorted(mapa_b)]
    if candidatos:
        pesos = [peso * (FATOR_EQUILIBRIO if autor is ultimo_favorecido else 1.0) for _, autor, peso in candidatos]
        rotulo, autor, _ = rng.choices(candidatos, weights=pesos, k=1)[0]
        return ResultadoDecisao(
            TipoResultadoDecisao.PONDERADO, rotulo, autor, None, (), vetadas,
            f"Sem opção em comum: '{rotulo}' saiu no sorteio ponderado pelos pesos.",
        )

    escolhedor = rng.choice([Papel.A, Papel.B])
    return ResultadoDecisao(
        TipoResultadoDecisao.CARA_OU_COROA, None, None, escolhedor, (), vetadas,
        "Todas as opções foram vetadas. A moeda decidiu quem escolhe desta vez.",
    )
