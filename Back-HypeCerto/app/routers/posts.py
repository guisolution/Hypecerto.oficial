"""
routers/posts.py
CRUD completo de postagens + upload de mídia.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.schemas import (
    PostagemCreate, PostagemUpdate, PostagemResponse, MessageResponse
)
from app.services.dependencies import get_current_user
from app.models.models import Usuario, Postagem, Agendamento, Midia, Projeto
import aiofiles
import uuid
import os

router = APIRouter(prefix="/posts", tags=["Postagens"])

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _enrich_postagem(p: Postagem) -> dict:
    """Enriquece postagem com dados relacionados para o frontend."""
    agendamentos_resumidos = []
    for ag in p.agendamentos:
        plataforma_nome = None
        if ag.conta_social and ag.conta_social.plataforma:
            plataforma_nome = ag.conta_social.plataforma.nome
        agendamentos_resumidos.append({
            "id": ag.id,
            "data_agendada": ag.data_agendada,
            "status_envio": ag.status_envio,
            "plataforma_nome": plataforma_nome,
        })

    return {
        "id": p.id,
        "titulo": p.titulo,
        "conteudo": p.conteudo,
        "status": p.status,
        "projeto_id": p.projeto_id,
        "projeto_nome": p.projeto.nome if p.projeto else None,
        "midias": p.midias,
        "agendamentos": agendamentos_resumidos,
        "criado_em": p.criado_em,
        "atualizado_em": p.atualizado_em,
    }


@router.get("", response_model=List[PostagemResponse], summary="Listar postagens")
def listar_postagens(
    status: Optional[str] = None,
    projeto_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista as postagens do usuário logado.
    Suporta filtro por status e projeto_id.
    """
    query = (
        db.query(Postagem)
        .options(
            joinedload(Postagem.midias),
            joinedload(Postagem.agendamentos).joinedload(Agendamento.conta_social),
            joinedload(Postagem.projeto),
        )
        .filter(Postagem.usuario_id == current_user.id)
    )

    if status:
        query = query.filter(Postagem.status == status)
    if projeto_id:
        query = query.filter(Postagem.projeto_id == projeto_id)

    postagens = query.order_by(Postagem.criado_em.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return [_enrich_postagem(p) for p in postagens]


@router.post("", response_model=PostagemResponse, status_code=201, summary="Criar postagem")
def criar_postagem(
    body: PostagemCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria uma nova postagem.
    Fluxo do frontend: Create → POST /posts → redireciona para /publish
    """
    postagem = Postagem(
        usuario_id=current_user.id,
        titulo=body.titulo,
        conteudo=body.conteudo,
        projeto_id=body.projeto_id,
        status="rascunho",
    )
    db.add(postagem)
    db.commit()
    db.refresh(postagem)
    return _enrich_postagem(postagem)


@router.get("/{post_id}", response_model=PostagemResponse, summary="Buscar postagem por ID")
def buscar_postagem(
    post_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    postagem = (
        db.query(Postagem)
        .options(joinedload(Postagem.midias), joinedload(Postagem.agendamentos), joinedload(Postagem.projeto))
        .filter(Postagem.id == post_id, Postagem.usuario_id == current_user.id)
        .first()
    )
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")
    return _enrich_postagem(postagem)


@router.put("/{post_id}", response_model=PostagemResponse, summary="Editar postagem")
def editar_postagem(
    post_id: int,
    body: PostagemUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edita título, conteúdo ou status de uma postagem."""
    postagem = db.query(Postagem).filter(
        Postagem.id == post_id, Postagem.usuario_id == current_user.id
    ).first()
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")

    if body.titulo is not None:
        postagem.titulo = body.titulo
    if body.conteudo is not None:
        postagem.conteudo = body.conteudo
    if body.status is not None:
        postagem.status = body.status
    if body.projeto_id is not None:
        postagem.projeto_id = body.projeto_id

    db.commit()
    db.refresh(postagem)
    return _enrich_postagem(postagem)


@router.delete("/{post_id}", response_model=MessageResponse, summary="Excluir postagem")
def excluir_postagem(
    post_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    postagem = db.query(Postagem).filter(
        Postagem.id == post_id, Postagem.usuario_id == current_user.id
    ).first()
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")

    db.delete(postagem)
    db.commit()
    return {"message": "Postagem excluída com sucesso", "success": True}


@router.post("/{post_id}/midia", summary="Upload de mídia para postagem")
async def upload_midia(
    post_id: int,
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Faz upload de imagem/vídeo e vincula à postagem.
    Frontend usa drag & drop na tela /publish.
    """
    postagem = db.query(Postagem).filter(
        Postagem.id == post_id, Postagem.usuario_id == current_user.id
    ).first()
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")

    # Salva arquivo
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Determina tipo de mídia
    tipo = "imagem"
    if file.content_type and "video" in file.content_type:
        tipo = "video"
    elif file.content_type and "audio" in file.content_type:
        tipo = "audio"

    midia = Midia(
        postagem_id=post_id,
        tipo=tipo,
        url=f"/uploads/{filename}",
        nome_arquivo=file.filename,
        tamanho_bytes=len(content),
        mime_type=file.content_type,
    )
    db.add(midia)
    db.commit()
    db.refresh(midia)

    return {
        "id": midia.id,
        "url": midia.url,
        "tipo": midia.tipo,
        "nome_arquivo": midia.nome_arquivo,
    }
