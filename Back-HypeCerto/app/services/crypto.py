"""
services/crypto.py
Criptografia em repouso (Fernet) para tokens OAuth de redes sociais.
A chave é derivada de TOKEN_ENCRYPTION_KEY (se definida) ou, na falta dela, de SECRET_KEY.
"""
import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

_PREFIX = "enc:v1:"


def _fernet() -> Fernet:
    raw = os.getenv("TOKEN_ENCRYPTION_KEY") or settings.SECRET_KEY
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(raw.encode()).digest()))


def encrypt_token(value):
    if not value or value.startswith(_PREFIX):
        return value
    return _PREFIX + _fernet().encrypt(value.encode()).decode()


def decrypt_token(value):
    if not value or not value.startswith(_PREFIX):
        return value  # legado em texto claro
    try:
        return _fernet().decrypt(value[len(_PREFIX):].encode()).decode()
    except InvalidToken:
        return None
