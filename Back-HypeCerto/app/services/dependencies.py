"""
services/dependencies.py
FastAPI Dependencies: extrai e valida o JWT de cada requisição protegida.
Uso: adicione `current_user: Usuario = Depends(get_current_user)` nos endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import Usuario
from app.services.auth_service import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """
    Dependency que:
    1. Extrai o Bearer token do header Authorization
    2. Decodifica e valida o JWT
    3. Busca o usuário no banco
    4. Retorna o objeto Usuario ou lança 401
    """
    payload = decode_token(credentials.credentials)
    user_id: int = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: usuário não identificado",
        )

    user = db.query(Usuario).filter(
        Usuario.id == int(user_id),
        #Usuario.ativo == True,
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    return user
