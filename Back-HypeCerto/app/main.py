"""
main.py
Ponto de entrada da aplicação FastAPI — HypeCerto Backend.

Inicializa:
- CORS para comunicação com frontend React
- Todos os routers (auth, posts, agendamentos, meta, ia, etc.)
- Scheduler de publicação automática
- Documentação automática (/docs e /redoc)
- Endpoint de health check
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from app.config import settings
from app.routers import auth, posts, agendamentos, meta, ia, channels, resultados, projetos
from app.services.scheduler import start_scheduler, stop_scheduler

# ─────────────────────────── Logging ───────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────── Lifespan ──────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação:
    - Startup: inicia o scheduler de agendamentos
    - Shutdown: encerra o scheduler
    """
    logger.info("🚀 HypeCerto Backend iniciando...")
    start_scheduler()
    yield
    logger.info("🛑 HypeCerto Backend encerrando...")
    stop_scheduler()


# ─────────────────────────── App ───────────────────────────────
app = FastAPI(
    title="HypeCerto API",
    description="""
## 🚀 HypeCerto — Plataforma SaaS de Automação de Marketing

Backend completo para gerenciamento e publicação automática em redes sociais.

### Funcionalidades
- **Autenticação** JWT com bcrypt
- **Postagens** com upload de mídia
- **Agendamento automático** via APScheduler
- **Integração Meta** (Facebook e Instagram Graph API)
- **IA** para geração de legendas e ideias de conteúdo
- **Métricas e Relatórios** consolidados
- **Multi-canal** (Facebook, Instagram, TikTok, LinkedIn, etc.)

### Modo Mock
Defina `USE_MOCK_META_API=True` no `.env` para simular publicações
sem fazer chamadas reais à API da Meta.
    """,
    version="1.0.0",
    contact={
        "name": "HypeCerto",
        "url": "https://hypecerto.com.br",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─────────────────────────── CORS ──────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────── Routers ───────────────────────────
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(agendamentos.router)
app.include_router(meta.router)
app.include_router(ia.router)
app.include_router(channels.router)
app.include_router(resultados.router)
app.include_router(projetos.router)


# ─────────────────────────── Arquivos estáticos (uploads) ──────
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ─────────────────────────── Health Check ──────────────────────
@app.get("/", tags=["Sistema"], summary="Health check")
def root():
    return {
        "status": "online",
        "app": "HypeCerto API",
        "version": "1.0.0",
        "docs": "/docs",
        "mock_meta": settings.USE_MOCK_META_API,
    }


@app.get("/health", tags=["Sistema"], summary="Status detalhado")
def health():
    from app.services.scheduler import scheduler
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "ambiente": settings.ENVIRONMENT,
        "mock_meta_api": settings.USE_MOCK_META_API,
        "ia_configurada": bool(settings.OPENAI_API_KEY),
    }
