"""
integrations/meta_api.py
Integração com a Graph API da Meta Platforms.

Controle via variável USE_MOCK_META_API:
  True  → simula envio, atualiza banco, retorna resposta fake
  False → chamada real via httpx para Facebook/Instagram
"""
import httpx
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.models import Agendamento, ContaSocial, Postagem, Midia
import logging

logger = logging.getLogger(__name__)

META_BASE_URL = f"https://graph.facebook.com/{settings.META_API_VERSION}"


# ─────────────────────────────────────────────────────────
#  PUBLICAÇÃO FACEBOOK
# ─────────────────────────────────────────────────────────

async def publicar_facebook(
    page_id: str,
    access_token: str,
    mensagem: str,
    imagem_url: Optional[str] = None,
) -> dict:
    """Publica em uma Facebook Page via Graph API."""
    endpoint = f"{META_BASE_URL}/{page_id}/feed"
    payload = {
        "message": mensagem,
        "access_token": access_token,
    }
    if imagem_url:
        payload["link"] = imagem_url

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(endpoint, data=payload)
        resp.raise_for_status()
        return resp.json()


# ─────────────────────────────────────────────────────────
#  PUBLICAÇÃO INSTAGRAM
# ─────────────────────────────────────────────────────────

async def publicar_instagram(
    ig_user_id: str,
    access_token: str,
    caption: str,
    imagem_url: Optional[str] = None,
) -> dict:
    """
    Publicação no Instagram via Graph API (2 etapas):
    1. Cria container de mídia
    2. Publica o container
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Etapa 1: criar container
        media_endpoint = f"{META_BASE_URL}/{ig_user_id}/media"
        media_payload: dict = {
            "caption": caption,
            "access_token": access_token,
        }
        if imagem_url:
            media_payload["image_url"] = imagem_url
        else:
            media_payload["media_type"] = "TEXT"

        media_resp = await client.post(media_endpoint, data=media_payload)
        media_resp.raise_for_status()
        creation_id = media_resp.json()["id"]

        # Etapa 2: publicar container
        publish_endpoint = f"{META_BASE_URL}/{ig_user_id}/media_publish"
        pub_payload = {
            "creation_id": creation_id,
            "access_token": access_token,
        }
        pub_resp = await client.post(publish_endpoint, data=pub_payload)
        pub_resp.raise_for_status()
        return pub_resp.json()


# ─────────────────────────────────────────────────────────
#  MOCK
# ─────────────────────────────────────────────────────────

def _mock_response(plataforma: str) -> dict:
    """Simula resposta de sucesso da Meta API."""
    fake_id = f"mock_{plataforma}_{uuid.uuid4().hex[:10]}"
    return {
        "id": fake_id,
        "mock": True,
        "plataforma": plataforma,
        "publicado_em": datetime.now(timezone.utc).isoformat(),
        "status": "success",
    }


# ─────────────────────────────────────────────────────────
#  ORQUESTRADOR PRINCIPAL
# ─────────────────────────────────────────────────────────

async def executar_publicacao(agendamento_id: int, db: Session) -> dict:
    """
    Orquestra a publicação de um agendamento:
    1. Busca agendamento + postagem + conta social
    2. Decide mock vs real conforme settings.USE_MOCK_META_API
    3. Chama a API correta (Facebook ou Instagram)
    4. Atualiza status_envio, data_publicacao_real, post_id_externo no banco
    """
    agendamento: Agendamento = db.query(Agendamento).filter(
        Agendamento.id == agendamento_id
    ).first()

    if not agendamento:
        raise ValueError(f"Agendamento {agendamento_id} não encontrado")

    if agendamento.status_envio == "publicado":
        return {"success": True, "message": "Já publicado anteriormente", "mock": False}

    postagem: Postagem = agendamento.postagem
    conta: ContaSocial = agendamento.conta_social

    # Pega primeira mídia da postagem (se houver)
    midia: Optional[Midia] = postagem.midias[0] if postagem.midias else None
    imagem_url = midia.url if midia else None

    resultado = {}
    plataforma_nome = conta.plataforma.nome.lower() if conta.plataforma else "desconhecido"

    try:
        agendamento.tentativas += 1

        if settings.USE_MOCK_META_API:
            # ── MODO MOCK ──────────────────────────────────────
            logger.info(f"[MOCK] Publicando agendamento {agendamento_id} em {plataforma_nome}")
            resultado = _mock_response(plataforma_nome)

        else:
            # ── MODO REAL ──────────────────────────────────────
            if "facebook" in plataforma_nome:
                if not conta.page_id or not conta.access_token:
                    raise ValueError("Conta Facebook sem page_id ou access_token configurados")
                resultado = await publicar_facebook(
                    page_id=conta.page_id,
                    access_token=conta.access_token,
                    mensagem=postagem.conteudo,
                    imagem_url=imagem_url,
                )
            elif "instagram" in plataforma_nome:
                if not conta.ig_user_id or not conta.access_token:
                    raise ValueError("Conta Instagram sem ig_user_id ou access_token configurados")
                resultado = await publicar_instagram(
                    ig_user_id=conta.ig_user_id,
                    access_token=conta.access_token,
                    caption=postagem.conteudo,
                    imagem_url=imagem_url,
                )
            else:
                # Plataformas não suportadas ainda (TikTok, LinkedIn...)
                resultado = _mock_response(plataforma_nome)
                resultado["aviso"] = f"Plataforma {plataforma_nome} ainda sem integração real, usando mock"

        # ── ATUALIZA BANCO ─────────────────────────────────────
        agendamento.status_envio = "publicado"
        agendamento.data_publicacao_real = datetime.now(timezone.utc)
        agendamento.post_id_externo = resultado.get("id")
        agendamento.response_api = resultado
        agendamento.erro_mensagem = None

        # Atualiza postagem
        postagem.status = "publicado"
        postagem.atualizado_em = datetime.now(timezone.utc)

        db.commit()

        return {
            "success": True,
            "message": f"Publicado com sucesso em {plataforma_nome}",
            "post_id_externo": resultado.get("id"),
            "mock": settings.USE_MOCK_META_API,
        }

    except Exception as exc:
        logger.error(f"Erro ao publicar agendamento {agendamento_id}: {exc}")
        agendamento.status_envio = "erro"
        agendamento.erro_mensagem = str(exc)
        db.commit()

        return {
            "success": False,
            "message": f"Erro ao publicar: {str(exc)}",
            "mock": settings.USE_MOCK_META_API,
        }
