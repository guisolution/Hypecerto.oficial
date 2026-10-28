"""
routers/auth.py
Endpoints de autenticação: login, cadastro, perfil, logout.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
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
from app.services.rate_limit import check_rate_limit, register_failure, clear_failures
from app.models.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse, summary="Fazer login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Autentica o usuário com email e senha.
    Retorna JWT + dados do usuário.
    
    Frontend usa: POST /auth/login  →  salva token no localStorage
    """
    check_rate_limit(request, "login", body.email)
    user = authenticate_usuario(db, body.email, body.password)
    if not user:
        register_failure(request, "login", body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    clear_failures(request, "login", body.email)

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/signup", response_model=TokenResponse, status_code=201, summary="Criar conta")
def signup(body: SignupRequest, db: Session = Depends(get_db)):
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

@router.delete("/delete", summary="Excluir conta")
def delete_account(body: LoginRequest, request: Request, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    """
    Exclui a conta do usuário autenticado após validação de senha e identidade.
    """
    # Protege contra força bruta na exclusão
    check_rate_limit(request, "delete_account", current_user.email)

    if current_user.email != body.email:
        register_failure(request, "delete_account", current_user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não tem permissão para excluir esta conta."
        )

    if not pwd_context.verify(body.password, current_user.senha_hash):
        register_failure(request, "delete_account", current_user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )

    clear_failures(request, "delete_account", current_user.email)

    try:
        db.delete(current_user)
        db.commit()
        return {"message": "Usuário deletado com sucesso!", "success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")


# ==========================================
# NOVA ROTA PARA O OAUTH DA META (FACEBOOK)
# ==========================================
@router.get("/callback/facebook", summary="Receber código de autorização da Meta")
def facebook_oauth_callback(code: str):
    """
    Endpoint acessado pela Meta após o usuário autorizar o aplicativo.
    Recebe o 'code' na URL, que deverá ser trocado pelo Access Token posteriormente.
    """
    
    # Aqui você implementará a requisição para trocar o 'code' pelo Token da Meta
    # usando a biblioteca requests ou httpx do Python.
    
    return {
        "message": "Autenticação com a Meta realizada. Código recebido.",
        "code": code
    }