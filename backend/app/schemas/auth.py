from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import Papel, StatusCasal


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    avatar_emoji: str | None = Field(default=None, max_length=8)


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str


class UsuarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    email: str
    papel: Papel | None
    casal_id: str | None
    avatar_emoji: str | None


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSaida


class MembroSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str
    papel: Papel | None
    avatar_emoji: str | None


class CasalSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: StatusCasal
    codigo_convite: str | None
    convite_expira_em: datetime | None
    data_inicio_relacionamento: date | None
    membros: list[MembroSaida]


class EntrarCasalEntrada(BaseModel):
    codigo: str = Field(min_length=6, max_length=12)
