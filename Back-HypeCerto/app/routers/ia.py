"""
routers/ia.py
Endpoints de geração de conteúdo com IA.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.schemas import IALegendaRequest, IAIdeiasRequest, IAResponse
from app.services.dependencies import get_current_user
from app.services.ia_service import gerar_legenda, gerar_ideias
from app.models.models import Usuario, SugestaoIA

router = APIRouter(prefix="/ia", tags=["Inteligência Artificial"])


@router.post("/legenda", response_model=IAResponse, summary="Gerar legenda com IA")
async def criar_legenda(
    body: IALegendaRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera uma legenda para postagem com IA.
    
    Parâmetros:
    - tema: assunto da postagem (ex: "promoção de matrícula")
    - plataforma: instagram, facebook, linkedin, tiktok
    - tom: engajador, profissional, divertido, informativo
    - incluir_hashtags: true/false
    
    Salva em `sugestoes_ia` para histórico e auditoria.
    """
    sugestao = await gerar_legenda(
        db=db,
        usuario=current_user,
        tema=body.tema,
        plataforma=body.plataforma,
        tom=body.tom,
        incluir_hashtags=body.incluir_hashtags,
    )
    return sugestao


@router.post("/ideias", response_model=IAResponse, summary="Gerar ideias de conteúdo")
async def criar_ideias(
    body: IAIdeiasRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera ideias de conteúdo para um segmento/nicho de mercado.
    
    Parâmetros:
    - segmento: nicho de mercado (ex: "escola de idiomas", "academia de ginástica")
    - quantidade: número de ideias a gerar (padrão: 5)
    - plataforma: filtrar ideias para uma rede específica (opcional)
    
    Salva em `sugestoes_ia`.
    """
    sugestao = await gerar_ideias(
        db=db,
        usuario=current_user,
        segmento=body.segmento,
        quantidade=body.quantidade,
        plataforma=body.plataforma,
    )
    return sugestao


@router.get("/historico", response_model=List[IAResponse], summary="Histórico de sugestões IA")
def historico_ia(
    tipo: Optional[str] = Query(None, description="legenda, ideia"),
    page: int = 1,
    per_page: int = 20,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista o histórico de sugestões geradas pela IA para o usuário.
    """
    query = db.query(SugestaoIA).filter(SugestaoIA.usuario_id == current_user.id)
    if tipo:
        query = query.filter(SugestaoIA.tipo == tipo)

    sugestoes = (
        query.order_by(SugestaoIA.criado_em.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return sugestoes


@router.delete("/historico/{sugestao_id}", summary="Deletar sugestão")
def deletar_sugestao(
    sugestao_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sugestao = db.query(SugestaoIA).filter(
        SugestaoIA.id == sugestao_id,
        SugestaoIA.usuario_id == current_user.id,
    ).first()
    if not sugestao:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")
    db.delete(sugestao)
    db.commit()
    return {"message": "Sugestão removida", "success": True}
