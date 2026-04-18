"""
scripts/seed.py
Popula o banco com dados iniciais:
- Plataformas (Facebook, Instagram, etc.)
- Planos (free, pro, enterprise)
- Usuário admin de teste

Uso: python scripts/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.models import Plataforma, Plano, Usuario
from app.services.auth_service import hash_password

db = SessionLocal()

# ─────────────────── Plataformas ───────────────────
PLATAFORMAS = [
    {"nome": "Facebook",  "slug": "facebook",  "icone_url": "/facebook.png"},
    {"nome": "Instagram", "slug": "instagram", "icone_url": "/instagran.png"},
    {"nome": "TikTok",    "slug": "tiktok",    "icone_url": "/tiktok.png"},
    {"nome": "YouTube",   "slug": "youtube",   "icone_url": "/youtube.png"},
    {"nome": "WhatsApp",  "slug": "whatsapp",  "icone_url": "/whatsapp.png"},
    {"nome": "LinkedIn",  "slug": "linkedin",  "icone_url": "/linkedin.png"},
]

for p in PLATAFORMAS:
    exists = db.query(Plataforma).filter(Plataforma.slug == p["slug"]).first()
    if not exists:
        db.add(Plataforma(**p, ativa=True))
        print(f"✓ Plataforma criada: {p['nome']}")
    else:
        print(f"  Plataforma já existe: {p['nome']}")

# ─────────────────── Planos ───────────────────
PLANOS = [
    {
        "nome": "Teste Grátis",
        "tipo": "free",
        "preco_mensal": 0.0,
        "limite_postagens": 5,
        "limite_canais": 1,
        "recursos": ["Até 5 postagens", "1 canal", "Suporte por email"],
    },
    {
        "nome": "Plano Pro",
        "tipo": "pro",
        "preco_mensal": 99.0,
        "limite_postagens": None,  # ilimitado
        "limite_canais": None,
        "recursos": ["Postagens ilimitadas", "Todos os canais", "Suporte prioritário", "Analytics avançado"],
    },
    {
        "nome": "Enterprise",
        "tipo": "enterprise",
        "preco_mensal": 0.0,  # customizado
        "limite_postagens": None,
        "limite_canais": None,
        "recursos": ["Tudo do Pro", "Múltiplos usuários", "API acesso", "Suporte 24/7"],
    },
]

for pl in PLANOS:
    exists = db.query(Plano).filter(Plano.tipo == pl["tipo"]).first()
    if not exists:
        db.add(Plano(**pl, ativo=True))
        print(f"✓ Plano criado: {pl['nome']}")
    else:
        print(f"  Plano já existe: {pl['nome']}")

# ─────────────────── Usuário de teste ───────────────────
TEST_EMAIL = "admin@hypecerto.com"
test_user = db.query(Usuario).filter(Usuario.email == TEST_EMAIL).first()
if not test_user:
    db.add(Usuario(
        nome="Admin HypeCerto",
        email=TEST_EMAIL,
        senha_hash=hash_password("hypecerto123"),
        ativo=True,
        email_verificado=True,
    ))
    print(f"✓ Usuário de teste criado: {TEST_EMAIL} / hypecerto123")
else:
    print(f"  Usuário de teste já existe: {TEST_EMAIL}")

db.commit()
db.close()
print("\n✅ Seed concluído com sucesso!")
