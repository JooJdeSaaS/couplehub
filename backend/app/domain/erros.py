"""Exceções de regra de negócio.

A camada de domínio não conhece HTTP; a API traduz cada classe para um status
(ver app/main.py). O atributo `codigo` é estável e pode ser usado pelo app
mobile para mensagens específicas.
"""


class ErroDominio(Exception):
    codigo = "REGRA_VIOLADA"

    def __init__(self, mensagem: str, codigo: str | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        if codigo:
            self.codigo = codigo


class RegraViolada(ErroDominio):
    """Operação válida sintaticamente, mas proibida pelas regras (HTTP 422)."""


class TransicaoInvalida(ErroDominio):
    """Máquina de estados não permite a transição pedida (HTTP 409)."""
    codigo = "TRANSICAO_INVALIDA"


class AcessoNegado(ErroDominio):
    """Usuário do casal não tem o papel exigido para a ação (HTTP 403)."""
    codigo = "ACESSO_NEGADO"


class NaoAutenticado(ErroDominio):
    """Token ausente, inválido ou credenciais erradas (HTTP 401)."""
    codigo = "NAO_AUTENTICADO"


class NaoEncontrado(ErroDominio):
    """Recurso inexistente OU pertencente a outro casal (HTTP 404).

    Responder 404 também para recursos de outro casal evita revelar que o ID
    existe (RB04 / REQ-PRV-002).
    """
    codigo = "NAO_ENCONTRADO"
