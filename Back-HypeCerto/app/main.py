"""
main.py
Ponto de entrada da aplicação FastAPI — HypeCerto Backend.
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
    """Gerencia ciclo de vida da aplicação"""
    logger.info("🚀 HypeCerto Backend iniciando...")
    start_scheduler()
    yield
    logger.info("🛑 HypeCerto Backend encerrando...")
    stop_scheduler()

# ─────────────────────────── App (CRIADO APENAS UMA VEZ) ───────
app = FastAPI(
    title="HypeCerto API",
    description="Backend completo para gerenciamento e publicação automática em redes sociais.",
    version="1.0.0",
    lifespan=lifespan,
    # Documentação interativa só fora de produção
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

# ─────────────────────────── CORS ──────────────────────────────
# Origens vêm de ALLOWED_ORIGINS (.env). O regex (ex.: Codespaces) só vale em desenvolvimento.
_origins = settings.allowed_origins_list + [
    "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174",
] if not settings.is_production else settings.allowed_origins_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=None if settings.is_production else settings.ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ─────────────────────────── Cabeçalhos de segurança ───────────
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cache-Control", "no-store") if not request.url.path.startswith("/uploads") else None
    if request.url.path.startswith("/uploads"):
        # arquivos enviados nunca são executados como página
        response.headers["Content-Security-Policy"] = "default-src 'none'; img-src 'self'; media-src 'self'; sandbox"
    else:
        if request.url.path not in ("/docs", "/redoc"):
            response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


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
    }

@app.get("/health", tags=["Sistema"], summary="Status detalhado")
def health():
    from app.services.scheduler import scheduler
    if settings.is_production:
        return {"status": "healthy"}
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "ambiente": settings.ENVIRONMENT,
        "mock_meta_api": settings.USE_MOCK_META_API,
        "ia_configurada": bool(settings.OPENAI_API_KEY),
    }