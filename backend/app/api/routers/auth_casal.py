"""Conta (RF01) e pareamento do casal (RF02)."""
from fastapi import APIRouter, status

from app.core.security import criar_token
from app.schemas.auth import CadastroEntrada, CasalSaida, EntrarCasalEntrada, LoginEntrada, TokenSaida, UsuarioSaida
from app.services import casal_service

from ..deps import DB, UsuarioAtual

router = APIRouter(tags=["Conta e casal"])


def _token(usuario) -> TokenSaida:
    return TokenSaida(access_token=criar_token(usuario.id), usuario=UsuarioSaida.model_validate(usuario))


@router.post("/auth/cadastro", response_model=TokenSaida, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: CadastroEntrada, db: DB):
    return _token(casal_service.cadastrar(db, dados.nome, dados.email, dados.senha, dados.avatar_emoji))


@router.post("/auth/login", response_model=TokenSaida)
def login(dados: LoginEntrada, db: DB):
    return _token(casal_service.autenticar(db, dados.email, dados.senha))


@router.get("/auth/eu", response_model=UsuarioSaida)
def eu(usuario: UsuarioAtual):
    return usuario


@router.post("/casais", response_model=CasalSaida, status_code=status.HTTP_201_CREATED,
             summary="Cria o HUB do casal e gera o código de convite")
def criar_casal(usuario: UsuarioAtual, db: DB):
    return casal_service.criar_casal(db, usuario)


@router.post("/casais/entrar", response_model=CasalSaida, summary="Entra no HUB do parceiro(a) pelo código")
def entrar(dados: EntrarCasalEntrada, usuario: UsuarioAtual, db: DB):
    return casal_service.entrar_no_casal(db, usuario, dados.codigo)


@router.post("/casais/meu/novo-codigo", response_model=CasalSaida)
def renovar_codigo(usuario: UsuarioAtual, db: DB):
    return casal_service.renovar_codigo(db, usuario)


@router.get("/casais/meu", response_model=CasalSaida | None)
def meu_casal(usuario: UsuarioAtual):
    return usuario.casal
