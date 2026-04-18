"""
services/auth_service.py
Serviço de autenticação: hashing de senha, criação e validação de JWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import Usuario
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(Usuario.email == email).first()


def authenticate_usuario(db: Session, email: str, password: str) -> Optional[Usuario]:
    user = get_usuario_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.senha_hash):
        return None
    return user


def create_usuario(db: Session, nome: str, email: str, password: str, telefone: str = None) -> Usuario:
    existing = get_usuario_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    user = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_password(password),
        telefone=telefone,
        #ativo=True,
        #email_verificado=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
