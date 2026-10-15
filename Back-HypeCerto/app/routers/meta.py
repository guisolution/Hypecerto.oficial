"""
routers/meta.py
Endpoints de integração com a API da Meta (Facebook / Instagram).
"""
import httpx
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.schemas import PublicarRequest, PublicarResponse
from app.services.dependencies import get_current_user
from app.models.models import Usuario, Agendamento, Postagem, ContaSocial, Plataforma
from app.integrations.meta_api import executar_publicacao
from app.config import settings
import logging

# Evita gravar o access token no terminal (o httpx loga a URL completa)
logging.getLogger("httpx").setLevel(logging.WARNING)

router = APIRouter(prefix="/meta", tags=["Meta API"])


class FacebookTokenRequest(BaseModel):
    access_token: str


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
        "api_version": getattr(settings, "META_API_VERSION", "v19.0"),
        "app_id_configurado": bool(getattr(settings, "META_APP_ID", False)),
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


def _obter_plataforma(db: Session, slug: str, nome: str) -> Plataforma:
    """Busca a plataforma pelo slug; cria se ainda não existir."""
    plataforma = db.query(Plataforma).filter(Plataforma.slug == slug).first()
    if not plataforma:
        plataforma = Plataforma(nome=nome, slug=slug, ativa=True)
        db.add(plataforma)
        db.flush()
    return plataforma


@router.post("/oauth/facebook", summary="Recebe o token do Facebook e salva as contas")
async def conectar_facebook(
    body: FacebookTokenRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recebe o Access Token do frontend, valida na Graph API,
    busca as Páginas do Facebook e contas do Instagram Business associadas,
    e guarda-as na base de dados.
    """
    avisos = []
    contas_salvas = []
    api_version = getattr(settings, "META_API_VERSION", "v19.0")
    base = f"https://graph.facebook.com/{api_version}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{base}/me/accounts", params={"access_token": body.access_token}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Erro ao validar token na Meta.")

        pages_data = resp.json().get("data", [])

        if not pages_data:
            avisos.append("Nenhuma Página do Facebook encontrada para este utilizador.")
            return {"contas": contas_salvas, "avisos": avisos}

        plat_fb = _obter_plataforma(db, "facebook", "Facebook")
        plat_ig = _obter_plataforma(db, "instagram", "Instagram")

        for page in pages_data:
            page_id = page["id"]
            page_token = page["access_token"]
            page_name = page.get("name", "Página")

            # ── Facebook: atualiza se já existe, senão cria ──
            conta_fb = (
                db.query(ContaSocial)
                .filter(
                    ContaSocial.usuario_id == current_user.id,
                    ContaSocial.plataforma_id == plat_fb.id_plataforma,
                    ContaSocial.page_id == page_id,
                )
                .first()
            )
            if conta_fb:
                conta_fb.access_token = page_token
                conta_fb.nome_conta = page_name
                conta_fb.ativa = True
            else:
                db.add(ContaSocial(
                    usuario_id=current_user.id,
                    plataforma_id=plat_fb.id_plataforma,
                    nome_conta=page_name,
                    access_token=page_token,
                    page_id=page_id,
                    ativa=True,
                ))
            contas_salvas.append({"plataforma": "facebook"})

            # ── Instagram vinculado à Página ──
            resp_ig = await client.get(
                f"{base}/{page_id}",
                params={
                    "fields": "instagram_business_account{id,username}",
                    "access_token": page_token,
                },
            )
            ig_data = resp_ig.json()
            ig_account = ig_data.get("instagram_business_account")

            if ig_account:
                ig_id = ig_account["id"]
                ig_username = ig_account.get("username")
                conta_ig = (
                    db.query(ContaSocial)
                    .filter(
                        ContaSocial.usuario_id == current_user.id,
                        ContaSocial.plataforma_id == plat_ig.id_plataforma,
                        ContaSocial.ig_user_id == ig_id,
                    )
                    .first()
                )
                if conta_ig:
                    conta_ig.access_token = page_token
                    conta_ig.nome_conta = f"Instagram ({page_name})"
                    conta_ig.username = ig_username
                    conta_ig.page_id = page_id
                    conta_ig.ativa = True
                else:
                    db.add(ContaSocial(
                        usuario_id=current_user.id,
                        plataforma_id=plat_ig.id_plataforma,
                        nome_conta=f"Instagram ({page_name})",
                        username=ig_username,
                        access_token=page_token,
                        page_id=page_id,
                        ig_user_id=ig_id,
                        ativa=True,
                    ))
                contas_salvas.append({"plataforma": "instagram"})
            else:
                avisos.append(
                    f"A página '{page_name}' não tem uma conta de Instagram Business associada."
                )

        db.commit()

    return {"contas": contas_salvas, "avisos": avisos}