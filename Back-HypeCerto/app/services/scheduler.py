"""
services/scheduler.py
Serviço de agendamento automático com APScheduler.

A cada 60 segundos busca agendamentos com:
  - status_envio = 'agendado'
  - data_agendada <= agora

E executa a publicação via meta_api.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.models import Agendamento
from app.integrations.meta_api import executar_publicacao
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def verificar_e_publicar_agendamentos():
    """
    Job que roda a cada 60 segundos.
    Verifica agendamentos pendentes e publica automaticamente.
    """
    db: Session = SessionLocal()
    try:
        agora = datetime.now(timezone.utc)

        pendentes = db.query(Agendamento).filter(
            Agendamento.status_envio == "agendado",
            Agendamento.data_agendada <= agora,
        ).all()

        if not pendentes:
            return

        logger.info(f"[Scheduler] Encontrados {len(pendentes)} agendamentos para publicar")

        for agendamento in pendentes:
            try:
                resultado = await executar_publicacao(agendamento.id, db)
                logger.info(
                    f"[Scheduler] Agendamento {agendamento.id}: "
                    f"{'✓ Publicado' if resultado['success'] else '✗ Erro'}"
                )
            except Exception as e:
                logger.error(f"[Scheduler] Erro no agendamento {agendamento.id}: {e}")

    except Exception as e:
        logger.error(f"[Scheduler] Erro geral: {e}")
    finally:
        db.close()


def start_scheduler():
    """Inicia o scheduler de agendamentos automáticos."""
    scheduler.add_job(
        verificar_e_publicar_agendamentos,
        trigger=IntervalTrigger(seconds=60),
        id="verificar_agendamentos",
        name="Verificar e publicar agendamentos",
        replace_existing=True,
        max_instances=1,  # evita sobreposição de execuções
    )
    scheduler.start()
    logger.info("[Scheduler] Serviço de agendamento iniciado — verificando a cada 60s")


def stop_scheduler():
    """Para o scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[Scheduler] Serviço de agendamento encerrado")
