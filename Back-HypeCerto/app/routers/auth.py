"""
routers/auth.py
Endpoints de autenticação: login, cadastro, perfil, logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.auth_service import pwd_context
from app.database.connection import get_db
from app.schemas.schemas import (
    LoginRequest, SignupRequest, TokenResponse,
    UsuarioResponse, MessageResponse
)
from app.services.auth_service import (
    authenticate_usuario, create_access_token,
    create_usuario, get_usuario_by_email
)
from app.services.dependencies import get_current_user
from app.models.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse, summary="Fazer login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica o usuário com email e senha.
    Retorna JWT + dados do usuário.
    
    Frontend usa: POST /auth/login  →  salva token no localStorage
    """
    user = authenticate_usuario(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/signup", response_model=TokenResponse, status_code=201, summary="Criar conta")
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Nome recebido no servidor: {body.nome}")
    """
    Cadastra novo usuário.
    Retorna JWT + dados do usuário criado.
    """
    user = create_usuario(
        db,
        nome=body.nome,
        email=body.email,
        password=body.password,
        telefone=body.telefone,
    )
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/me", response_model=UsuarioResponse, summary="Dados do usuário logado")
def me(current_user: Usuario = Depends(get_current_user)):
    """
    Retorna os dados do usuário autenticado.
    Frontend chama em toda inicialização para checar sessão.
    """
    return current_user


@router.post("/logout", response_model=MessageResponse, summary="Logout")
def logout(current_user: Usuario = Depends(get_current_user)):
    """
    Logout (stateless com JWT — apenas confirma ao frontend).
    O frontend deve apagar o token armazenado.
    """
    return {"message": "Logout realizado com sucesso", "success": True}


@router.post("/forgot-password", response_model=MessageResponse, summary="Recuperar senha")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Inicia fluxo de recuperação de senha.
    (Implementação de envio de email a ser adicionada conforme provedor SMTP)
    """
    user = get_usuario_by_email(db, email)
    # Por segurança, não revelamos se o email existe ou não
    return {
        "message": "Se este email estiver cadastrado, você receberá as instruções.",
        "success": True,
    }

@router.delete("/delete")
def delete_account_bruto(body: LoginRequest, db: Session = Depends(get_db)):
    # 1. Busca o usuário usando SQL Puro para não ativar os Mappers quebrados
    result = db.execute(
        text("SELECT id, senha_hash FROM usuarios WHERE email = :email"),
        {"email": body.email}
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user_id, senha_hash = result

    # 2. Verifica a senha manualmente
    if not pwd_context.verify(body.password, senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    # 3. Deleta o infeliz
    try:
        db.execute(text("DELETE FROM usuarios WHERE id = :id"), {"id": user_id})
        db.commit()
        return {"message": "Usuário deletado com sucesso no modo bruto!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")