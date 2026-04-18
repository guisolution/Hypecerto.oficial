"""
routers/agendamentos.py
Endpoints de agendamento de postagens.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone
from app.database.connection import get_db
from app.schemas.schemas import (
    AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, MessageResponse
)
from app.services.dependencies import get_current_user
from app.models.models import Usuario, Agendamento, Postagem, ContaSocial

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])


def _enrich_agendamento(ag: Agendamento) -> dict:
    """Enriquece agendamento com dados relacionados."""
    plataforma_nome = None
    channels = []

    if ag.conta_social and ag.conta_social.plataforma:
        plataforma_nome = ag.conta_social.plataforma.nome
        channels = [ag.conta_social.plataforma.nome]

    return {
        "id": ag.id,
        "postagem_id": ag.postagem_id,
        "conta_social_id": ag.conta_social_id,
        "data_agendada": ag.data_agendada,
        "data_publicacao_real": ag.data_publicacao_real,
        "status_envio": ag.status_envio,
        "post_id_externo": ag.post_id_externo,
        "tentativas": ag.tentativas,
        "erro_mensagem": ag.erro_mensagem,
        "criado_em": ag.criado_em,
        "postagem_titulo": ag.postagem.titulo if ag.postagem else None,
        "postagem_conteudo": ag.postagem.conteudo if ag.postagem else None,
        "plataforma_nome": plataforma_nome,
        "channels": channels,
    }


@router.get("", response_model=List[AgendamentoResponse], summary="Listar agendamentos")
def listar_agendamentos(
    status_envio: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    page: int = 1,
    per_page: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista agendamentos do usuário logado.
    Usado pelo Dashboard (calendário e modo lista).
    Filtros opcionais: status_envio, data_inicio, data_fim.
    """
    query = (
        db.query(Agendamento)
        .join(Postagem, Agendamento.postagem_id == Postagem.id)
        .options(
            joinedload(Agendamento.postagem),
            joinedload(Agendamento.conta_social).joinedload(ContaSocial.plataforma),
        )
        .filter(Postagem.usuario_id == current_user.id)
    )

    if status_envio:
        query = query.filter(Agendamento.status_envio == status_envio)
    if data_inicio:
        query = query.filter(Agendamento.data_agendada >= data_inicio)
    if data_fim:
        query = query.filter(Agendamento.data_agendada <= data_fim)

    agendamentos = (
        query.order_by(Agendamento.data_agendada.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return [_enrich_agendamento(ag) for ag in agendamentos]


@router.post("", response_model=AgendamentoResponse, status_code=201, summary="Criar agendamento")
def criar_agendamento(
    body: AgendamentoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria um agendamento para uma postagem em uma conta social.
    
    Fluxo:
    1. Frontend envia postagem_id + conta_social_id + data_agendada
    2. Backend cria o registro com status_envio = 'agendado'
    3. O scheduler verifica automaticamente e publica no horário
    """
    # Valida postagem pertence ao usuário
    postagem = db.query(Postagem).filter(
        Postagem.id == body.postagem_id,
        Postagem.usuario_id == current_user.id,
    ).first()
    if not postagem:
        raise HTTPException(status_code=404, detail="Postagem não encontrada")

    # Valida conta social pertence ao usuário
    conta = db.query(ContaSocial).filter(
        ContaSocial.id == body.conta_social_id,
        ContaSocial.usuario_id == current_user.id,
        ContaSocial.ativa == True,
    ).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta social não encontrada ou inativa")

    # Evita duplicação
    existente = db.query(Agendamento).filter(
        Agendamento.postagem_id == body.postagem_id,
        Agendamento.conta_social_id == body.conta_social_id,
        Agendamento.status_envio.in_(["agendado", "publicado"]),
    ).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um agendamento ativo para esta postagem nesta conta"
        )

    agendamento = Agendamento(
        postagem_id=body.postagem_id,
        conta_social_id=body.conta_social_id,
        data_agendada=body.data_agendada,
        status_envio="agendado",
        tentativas=0,
    )
    db.add(agendamento)

    # Atualiza status da postagem
    postagem.status = "agendado"

    db.commit()
    db.refresh(agendamento)
    return _enrich_agendamento(agendamento)


@router.get("/{agendamento_id}", response_model=AgendamentoResponse, summary="Buscar agendamento")
def buscar_agendamento(
    agendamento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ag = (
        db.query(Agendamento)
        .join(Postagem)
        .options(
            joinedload(Agendamento.postagem),
            joinedload(Agendamento.conta_social).joinedload(ContaSocial.plataforma),
        )
        .filter(Agendamento.id == agendamento_id, Postagem.usuario_id == current_user.id)
        .first()
    )
    if not ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return _enrich_agendamento(ag)


@router.put("/{agendamento_id}", response_model=AgendamentoResponse, summary="Editar agendamento")
def editar_agendamento(
    agendamento_id: int,
    body: AgendamentoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edita data ou status de um agendamento. Não pode editar se já publicado."""
    ag = (
        db.query(Agendamento)
        .join(Postagem)
        .filter(Agendamento.id == agendamento_id, Postagem.usuario_id == current_user.id)
        .first()
    )
    if not ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    if ag.status_envio == "publicado":
        raise HTTPException(status_code=400, detail="Não é possível editar um agendamento já publicado")

    if body.data_agendada is not None:
        ag.data_agendada = body.data_agendada
    if body.status_envio is not None:
        ag.status_envio = body.status_envio

    db.commit()
    db.refresh(ag)
    return _enrich_agendamento(ag)


@router.delete("/{agendamento_id}", response_model=MessageResponse, summary="Cancelar agendamento")
def cancelar_agendamento(
    agendamento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ag = (
        db.query(Agendamento)
        .join(Postagem)
        .filter(Agendamento.id == agendamento_id, Postagem.usuario_id == current_user.id)
        .first()
    )
    if not ag:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    if ag.status_envio == "publicado":
        raise HTTPException(status_code=400, detail="Não é possível cancelar um agendamento já publicado")

    ag.status_envio = "cancelado"
    db.commit()
    return {"message": "Agendamento cancelado com sucesso", "success": True}
