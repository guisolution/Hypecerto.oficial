"""
routers/meta.py
Endpoints de integração com a API da Meta (Facebook / Instagram).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import PublicarRequest, PublicarResponse
from app.services.dependencies import get_current_user
from app.models.models import Usuario, Agendamento, Postagem
from app.integrations.meta_api import executar_publicacao
from app.config import settings

router = APIRouter(prefix="/meta", tags=["Meta API"])


@router.post("/publicar", response_model=PublicarResponse, summary="Publicar agendamento imediatamente")
async def publicar_agora(
    body: PublicarRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Publica um agendamento imediatamente (sem esperar o scheduler).
    
    Modo MOCK (USE_MOCK_META_API=True): simula envio e atualiza banco.
    Modo REAL (USE_MOCK_META_API=False): chama Graph API da Meta.
    
    Fluxo:
    - Frontend clica em "Publicar" na tela /publish
    - Chama POST /meta/publicar com o agendamento_id
    - Backend executa e retorna resultado
    """
    # Verifica se o agendamento pertence ao usuário
    ag = (
        db.query(Agendamento)
        .join(Postagem)
        .filter(
            Agendamento.id == body.agendamento_id,
            Postagem.usuario_id == current_user.id,
        )
        .first()
    )
    if not ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    resultado = await executar_publicacao(body.agendamento_id, db)

    return PublicarResponse(
        success=resultado["success"],
        message=resultado["message"],
        post_id_externo=resultado.get("post_id_externo"),
        mock=resultado.get("mock", True),
    )


@router.get("/status", summary="Status da integração Meta")
def status_integracao():
    """Retorna configuração atual da integração Meta."""
    return {
        "modo": "mock" if settings.USE_MOCK_META_API else "real",
        "api_version": settings.META_API_VERSION,
        "app_id_configurado": bool(settings.META_APP_ID),
        "descricao": (
            "Modo simulação ativo — nenhuma chamada real é feita."
            if settings.USE_MOCK_META_API
            else "Integração real com a Graph API da Meta ativa."
        ),
    }


@router.post("/publicar-direto", summary="Publicar postagem diretamente (sem agendamento)")
async def publicar_direto(
    postagem_id: int,
    conta_social_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria um agendamento com data = agora e publica imediatamente.
    Usado quando o usuário clica em 'Publicar agora' sem agendar.
    """
    from datetime import datetime, timezone
    from app.models.models import ContaSocial

    postagem = db.query(Postagem).filter(
        Postagem.id == postagem_id,
        Postagem.usuario_id == current_user.id,
    ).first()
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")

    conta = db.query(ContaSocial).filter(
        ContaSocial.id == conta_social_id,
        ContaSocial.usuario_id == current_user.id,
    ).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta social não encontrada")

    # Cria agendamento imediato
    agendamento = Agendamento(
        postagem_id=postagem_id,
        conta_social_id=conta_social_id,
        data_agendada=datetime.now(timezone.utc),
        status_envio="agendado",
        tentativas=0,
    )
    db.add(agendamento)
    db.commit()
    db.refresh(agendamento)

    resultado = await executar_publicacao(agendamento.id, db)
    return resultado
