"""Cadastro, login e pareamento (RF01, RF02)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import relogio
from app.core.security import gerar_hash_senha, verificar_senha
from app.domain import casal as regras
from app.domain.enums import Papel, StatusCasal
from app.domain.erros import NaoAutenticado, NaoEncontrado, RegraViolada, TransicaoInvalida
from app.models import Casal, Usuario

_TENTATIVAS_CODIGO = 5


def cadastrar(db: Session, nome: str, email: str, senha: str, avatar_emoji: str | None = None) -> Usuario:
    email = email.strip().lower()
    if db.scalar(select(Usuario.id).where(Usuario.email == email)):
        raise TransicaoInvalida("Este e-mail já está cadastrado.", "EMAIL_EM_USO")
    usuario = Usuario(nome=nome.strip(), email=email, senha_hash=gerar_hash_senha(senha), avatar_emoji=avatar_emoji)
    db.add(usuario)
    db.commit()
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutenticado("E-mail ou senha incorretos.", "CREDENCIAIS_INVALIDAS")
    return usuario


def _codigo_livre(db: Session) -> str:
    for _ in range(_TENTATIVAS_CODIGO):
        codigo = regras.gerar_codigo()
        if not db.scalar(select(Casal.id).where(Casal.codigo_convite == codigo)):
            return codigo
    raise RuntimeError("Não foi possível gerar um código de convite único.")


def criar_casal(db: Session, usuario: Usuario) -> Casal:
    regras.validar_criacao_casal(usuario.casal_id is not None)
    casal = Casal(
        status=StatusCasal.AGUARDANDO_PARCEIRO,
        codigo_convite=_codigo_livre(db),
        convite_expira_em=relogio.agora() + regras.VALIDADE_CONVITE,
    )
    db.add(casal)
    # atribuir pela relação (não pelo FK) mantém usuario.casal e casal.membros
    # coerentes na mesma sessão (expire_on_commit=False)
    usuario.casal, usuario.papel = casal, Papel.A
    db.commit()
    db.refresh(casal)
    return casal


def entrar_no_casal(db: Session, usuario: Usuario, codigo: str) -> Casal:
    casal = db.scalar(select(Casal).where(Casal.codigo_convite == regras.normalizar_codigo(codigo)))
    if casal is None:
        raise NaoEncontrado("Código de convite inválido.", "CONVITE_INVALIDO")
    agora = relogio.agora()
    regras.validar_entrada(casal.status, casal.convite_expira_em, agora, usuario.casal_id is not None)
    usuario.casal, usuario.papel = casal, Papel.B
    casal.status = StatusCasal.ATIVO
    casal.codigo_convite = None          # código de uso único
    casal.convite_expira_em = None
    casal.pareado_em = agora
    db.commit()                          # uq_usuario_casal_papel barra corrida entre dois "B"
    db.refresh(casal)
    return casal


def renovar_codigo(db: Session, usuario: Usuario) -> Casal:
    casal = usuario.casal
    if casal is None or casal.status is not StatusCasal.AGUARDANDO_PARCEIRO:
        raise RegraViolada("Só é possível renovar o convite enquanto aguarda o parceiro.", "SEM_CONVITE_ATIVO")
    casal.codigo_convite = _codigo_livre(db)
    casal.convite_expira_em = relogio.agora() + regras.VALIDADE_CONVITE
    db.commit()
    db.refresh(casal)
    return casal
