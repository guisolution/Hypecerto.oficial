"""
routers/channels.py
Endpoints para gerenciamento de contas sociais (canais).
Compatível com a tela Channels.tsx do frontend.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database.connection import get_db
from app.schemas.schemas import ContaSocialResponse, ConectarContaRequest, MessageResponse
from app.services.dependencies import get_current_user
from app.models.models import Usuario, ContaSocial, Plataforma

router = APIRouter(prefix="/channels", tags=["Canais / Contas Sociais"])


def _to_response(conta: ContaSocial) -> dict:
    return {
        "id": conta.id,
        "plataforma_id": conta.plataforma_id,
        "nome_conta": conta.nome_conta,
        "username": conta.username,
        "page_id": conta.page_id,
        "ig_user_id": conta.ig_user_id,
        "ativa": conta.ativa,
        "plataforma_nome": conta.plataforma.nome if conta.plataforma else None,
        "criado_em": conta.criado_em,
    }


@router.get("", response_model=List[ContaSocialResponse], summary="Listar contas sociais")
def listar_canais(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna todas as contas sociais do usuário.
    Usado na tela Channels.tsx para mostrar quais redes estão conectadas.
    """
    contas = (
        db.query(ContaSocial)
        .options(joinedload(ContaSocial.plataforma))
        .filter(ContaSocial.usuario_id == current_user.id)
        .all()
    )
    return [_to_response(c) for c in contas]


@router.post("/conectar", response_model=ContaSocialResponse, status_code=201, summary="Conectar conta social")
def conectar_conta(
    body: ConectarContaRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Conecta/vincula uma conta de rede social ao usuário.
    
    No fluxo real: o frontend faz OAuth com a Meta e envia o
    access_token resultante para este endpoint.
    """
    # Busca plataforma pelo slug
    plataforma = db.query(Plataforma).filter(
        Plataforma.slug == body.plataforma_slug,
        Plataforma.ativa == True,
    ).first()

    if not plataforma:
        # Cria a plataforma se não existir (para facilitar setup inicial)
        plataforma = Plataforma(
            nome=body.plataforma_slug.capitalize(),
            slug=body.plataforma_slug,
            ativa=True,
        )
        db.add(plataforma)
        db.flush()

    # Verifica se já existe conta ativa para esta plataforma
    existente = db.query(ContaSocial).filter(
        ContaSocial.usuario_id == current_user.id,
        ContaSocial.plataforma_id == plataforma.id,
        ContaSocial.ativa == True,
    ).first()

    if existente:
        # Atualiza tokens existentes
        existente.access_token = body.access_token
        existente.page_id = body.page_id or existente.page_id
        existente.ig_user_id = body.ig_user_id or existente.ig_user_id
        existente.nome_conta = body.nome_conta or existente.nome_conta
        db.commit()
        db.refresh(existente)
        return _to_response(existente)

    conta = ContaSocial(
        usuario_id=current_user.id,
        plataforma_id=plataforma.id,
        access_token=body.access_token,
        page_id=body.page_id,
        ig_user_id=body.ig_user_id,
        nome_conta=body.nome_conta or body.plataforma_slug,
        ativa=True,
    )
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return _to_response(conta)


@router.delete("/{conta_id}", response_model=MessageResponse, summary="Desconectar conta social")
def desconectar_conta(
    conta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desativa (não exclui) a conta social do usuário."""
    conta = db.query(ContaSocial).filter(
        ContaSocial.id == conta_id,
        ContaSocial.usuario_id == current_user.id,
    ).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    conta.ativa = False
    db.commit()
    return {"message": "Conta desconectada com sucesso", "success": True}


@router.get("/plataformas", summary="Listar plataformas suportadas")
def listar_plataformas(db: Session = Depends(get_db)):
    """
    Retorna todas as plataformas suportadas pelo sistema.
    Frontend usa para montar a lista de canais disponíveis.
    """
    plataformas = db.query(Plataforma).filter(Plataforma.ativa == True).all()

    # Se banco vazio, retorna lista padrão
    if not plataformas:
        return [
            {"id": None, "slug": "facebook",  "nome": "Facebook",  "icone_url": "/facebook.png"},
            {"id": None, "slug": "instagram", "nome": "Instagram", "icone_url": "/instagran.png"},
            {"id": None, "slug": "tiktok",    "nome": "TikTok",    "icone_url": "/tiktok.png"},
            {"id": None, "slug": "youtube",   "nome": "YouTube",   "icone_url": "/youtube.png"},
            {"id": None, "slug": "whatsapp",  "nome": "WhatsApp",  "icone_url": "/whatsapp.png"},
            {"id": None, "slug": "linkedin",  "nome": "LinkedIn",  "icone_url": "/linkedin.png"},
        ]

    return [
        {"id": p.id, "slug": p.slug, "nome": p.nome, "icone_url": p.icone_url}
        for p in plataformas
    ]
