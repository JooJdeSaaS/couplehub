"""Configuração comum: banco em memória e chave de dados efêmera.

As variáveis precisam existir ANTES de importar app.core.database."""
import os

from cryptography.fernet import Fernet

os.environ.setdefault("COUPLEHUB_DATABASE_URL", "sqlite://")
os.environ.setdefault("COUPLEHUB_CHAVE_DADOS", Fernet.generate_key().decode())
os.environ.setdefault("COUPLEHUB_JWT_SEGREDO", "segredo-de-teste-com-mais-de-32-bytes!!")
