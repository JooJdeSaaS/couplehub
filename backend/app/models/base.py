"""Base declarativa e tipos de coluna compartilhados."""
import uuid
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import TypeDecorator

from app.core import crypto, relogio


class Base(DeclarativeBase):
    pass


def novo_id() -> str:
    """UUID v4 como texto: IDs não sequenciais dificultam enumeração (RB04)."""
    return str(uuid.uuid4())


def agora_utc() -> datetime:
    return relogio.agora()


def EnumStr(enum_cls: type[StrEnum]) -> Enum:
    """Enum gravado como VARCHAR + CHECK (SQLite não tem ENUM nativo)."""
    return Enum(enum_cls, native_enum=False, length=32, validate_strings=True, create_constraint=True)


class UTCDateTime(TypeDecorator):
    """Grava sempre em UTC e devolve datetime com fuso.

    O SQLite não guarda fuso; sem isto, comparar datetimes "ingênuos" e
    "conscientes" quebra em tempo de execução.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, valor, dialect):
        if valor is None:
            return None
        if valor.tzinfo is None:
            raise ValueError("datetime sem fuso horário")
        return valor.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, valor, dialect):
        return None if valor is None else valor.replace(tzinfo=timezone.utc)


class TextoCifrado(TypeDecorator):
    """Texto cifrado com Fernet no banco, legível na aplicação (RNF02)."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, valor, dialect):
        return None if valor is None else crypto.cifrar(valor)

    def process_result_value(self, valor, dialect):
        return None if valor is None else crypto.decifrar(valor)


def pk():
    return mapped_column(String(36), primary_key=True, default=novo_id)


def coluna_timestamp():
    return mapped_column(UTCDateTime, default=agora_utc, nullable=False)
