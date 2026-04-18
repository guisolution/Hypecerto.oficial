"""
routers/resultados.py
Endpoints de métricas, relatórios e dashboard.
Compatível com Results.tsx e Dashboard.tsx do frontend.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from app.database.connection import get_db
from app.schemas.schemas import (
    MetricaResponse, DashboardMetricasResponse,
    RelatorioResponse
)
from app.services.dependencies import get_current_user
from app.models.models import (
    Usuario, Postagem, Agendamento, Metrica, Relatorio, ContaSocial
)

router = APIRouter(prefix="/resultados", tags=["Resultados e Métricas"])


@router.get("/dashboard", response_model=DashboardMetricasResponse, summary="Métricas do dashboard")
def dashboard_metricas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna todas as métricas necessárias para o Dashboard.tsx:
    - Contadores gerais (postagens, curtidas, alcance, etc.)
    - Atividade da última semana (para o gráfico de linha)
    - Últimas postagens
    """
    # Contadores gerais
    total_postagens = db.query(func.count(Postagem.id)).filter(
        Postagem.usuario_id == current_user.id
    ).scalar() or 0

    publicadas = db.query(func.count(Postagem.id)).filter(
        Postagem.usuario_id == current_user.id,
        Postagem.status == "publicado",
    ).scalar() or 0

    agendadas = db.query(func.count(Agendamento.id)).join(Postagem).filter(
        Postagem.usuario_id == current_user.id,
        Agendamento.status_envio == "agendado",
    ).scalar() or 0

    # Métricas acumuladas
    metricas_agg = (
        db.query(
            func.sum(Metrica.curtidas),
            func.sum(Metrica.comentarios),
            func.sum(Metrica.compartilhamentos),
            func.sum(Metrica.alcance),
        )
        .join(Postagem, Metrica.postagem_id == Postagem.id)
        .filter(Postagem.usuario_id == current_user.id)
        .first()
    )
    total_curtidas = int(metricas_agg[0] or 0)
    total_comentarios = int(metricas_agg[1] or 0)
    total_compartilhamentos = int(metricas_agg[2] or 0)
    total_alcance = int(metricas_agg[3] or 0)

    # Atividade semanal (últimos 7 dias) — agendamentos publicados por dia
    hoje = datetime.now(timezone.utc)
    dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
    atividade_semanal = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        dia_inicio = dia.replace(hour=0, minute=0, second=0, microsecond=0)
        dia_fim = dia.replace(hour=23, minute=59, second=59)
        count = (
            db.query(func.count(Agendamento.id))
            .join(Postagem)
            .filter(
                Postagem.usuario_id == current_user.id,
                Agendamento.data_publicacao_real >= dia_inicio,
                Agendamento.data_publicacao_real <= dia_fim,
            )
            .scalar() or 0
        )
        # Usa valor mock > 0 se não houver dados ainda (melhora visualização no demo)
        if count == 0 and total_postagens == 0:
            import random
            count = random.randint(30, 70)

        atividade_semanal.append({
            "name": dias_semana[dia.weekday()],
            "value": count,
        })

    # Últimas 5 postagens
    postagens_recentes = (
        db.query(Postagem)
        .filter(Postagem.usuario_id == current_user.id)
        .order_by(Postagem.criado_em.desc())
        .limit(5)
        .all()
    )

    postagens_response = [
        {
            "id": p.id,
            "titulo": p.titulo,
            "conteudo": p.conteudo,
            "status": p.status,
            "projeto_id": p.projeto_id,
            "midias": [],
            "agendamentos": [],
            "criado_em": p.criado_em,
            "atualizado_em": p.atualizado_em,
        }
        for p in postagens_recentes
    ]

    return {
        "total_postagens": total_postagens,
        "postagens_publicadas": publicadas,
        "postagens_agendadas": agendadas,
        "total_curtidas": total_curtidas,
        "total_comentarios": total_comentarios,
        "total_compartilhamentos": total_compartilhamentos,
        "total_alcance": total_alcance,
        "atividade_semanal": atividade_semanal,
        "postagens_recentes": postagens_response,
    }


@router.get("/metricas", response_model=List[MetricaResponse], summary="Listar métricas")
def listar_metricas(
    postagem_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista métricas das postagens do usuário."""
    query = (
        db.query(Metrica)
        .join(Postagem, Metrica.postagem_id == Postagem.id)
        .filter(Postagem.usuario_id == current_user.id)
    )
    if postagem_id:
        query = query.filter(Metrica.postagem_id == postagem_id)

    metricas = (
        query.order_by(Metrica.data_coleta.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return metricas


@router.get("/relatorios", response_model=List[RelatorioResponse], summary="Listar relatórios")
def listar_relatorios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista relatórios gerados para o usuário."""
    relatorios = (
        db.query(Relatorio)
        .filter(Relatorio.usuario_id == current_user.id)
        .order_by(Relatorio.criado_em.desc())
        .limit(20)
        .all()
    )
    return relatorios


@router.post("/relatorios/gerar", response_model=RelatorioResponse, summary="Gerar relatório")
def gerar_relatorio(
    tipo: str = Query("mensal", description="semanal, mensal, campanha"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera e persiste um relatório consolidado de métricas.
    """
    hoje = datetime.now(timezone.utc)
    if tipo == "semanal":
        inicio = hoje - timedelta(days=7)
        titulo = f"Relatório Semanal — {inicio.strftime('%d/%m')} a {hoje.strftime('%d/%m/%Y')}"
    else:
        inicio = hoje.replace(day=1)
        titulo = f"Relatório Mensal — {hoje.strftime('%B/%Y')}"

    # Agrega dados
    agg = (
        db.query(
            func.sum(Metrica.curtidas),
            func.sum(Metrica.comentarios),
            func.sum(Metrica.compartilhamentos),
            func.sum(Metrica.alcance),
            func.count(Metrica.id),
        )
        .join(Postagem)
        .filter(
            Postagem.usuario_id == current_user.id,
            Metrica.data_coleta >= inicio,
        )
        .first()
    )

    dados = {
        "curtidas": int(agg[0] or 0),
        "comentarios": int(agg[1] or 0),
        "compartilhamentos": int(agg[2] or 0),
        "alcance": int(agg[3] or 0),
        "total_metricas": int(agg[4] or 0),
        "gerado_em": hoje.isoformat(),
    }

    relatorio = Relatorio(
        usuario_id=current_user.id,
        titulo=titulo,
        tipo=tipo,
        periodo_inicio=inicio,
        periodo_fim=hoje,
        dados=dados,
    )
    db.add(relatorio)
    db.commit()
    db.refresh(relatorio)
    return relatorio


@router.get("/projetos", summary="Progresso dos projetos (para Results.tsx)")
def progresso_projetos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna dados de progresso dos projetos do usuário.
    Usado nos cards 'Projetos Recentes' da tela Results.tsx.
    """
    from app.models.models import Projeto
    projetos = (
        db.query(Projeto)
        .filter(Projeto.usuario_id == current_user.id, Projeto.ativo == True)
        .limit(10)
        .all()
    )

    result = []
    CORES = ["#6D28D9", "#8B5CF6", "#F59E0B", "#3B82F6", "#EC4899"]
    for i, p in enumerate(projetos):
        total = db.query(func.count(Postagem.id)).filter(Postagem.projeto_id == p.id).scalar() or 0
        publicadas = db.query(func.count(Postagem.id)).filter(
            Postagem.projeto_id == p.id, Postagem.status == "publicado"
        ).scalar() or 0
        progresso = int((publicadas / total * 100) if total > 0 else 0)
        result.append({
            "name": p.nome,
            "progress": progresso,
            "color": CORES[i % len(CORES)],
            "total_postagens": total,
            "publicadas": publicadas,
        })

    return result
