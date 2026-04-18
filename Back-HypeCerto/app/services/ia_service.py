"""
services/ia_service.py
Serviço de IA para geração de legendas e ideias de conteúdo.

Se OPENAI_API_KEY estiver configurada, usa a API real.
Caso contrário, retorna sugestões pré-definidas (modo demo).
"""
import httpx
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import SugestaoIA, Usuario
from app.config import settings
import logging
import random

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  TEMPLATES DE FALLBACK (sem OpenAI)
# ─────────────────────────────────────────────────────────

LEGENDAS_DEMO = {
    "instagram": [
        "✨ {tema} — porque o sucesso começa com o primeiro passo!\n\n💡 Dê esse passo agora e transforme seus resultados.\n\n#Motivação #{tema_tag} #Crescimento #Sucesso",
        "🚀 Chegou a hora de falar sobre {tema}!\n\nNão perca essa oportunidade única de elevar seu negócio ao próximo nível.\n\n🔥 Comente SIM se quer saber mais!\n\n#{tema_tag} #Marketing #Negócios",
        "💜 {tema} é o que pode mudar tudo para você!\n\nEstamos aqui para ajudar. Entre em contato agora mesmo.\n\n📲 Link na bio\n\n#{tema_tag} #Oportunidade #Resultado",
    ],
    "facebook": [
        "Olá! Hoje queremos falar sobre {tema}. 🎯\n\nSabia que essa é uma das principais tendências do momento? Aproveite e compartilhe com quem precisa saber!\n\n#HypeCerto #{tema_tag}",
        "📢 ATENÇÃO! Novidades sobre {tema}!\n\nClique em Saiba Mais e fique por dentro de tudo. Compartilhe com seus amigos!\n\n#{tema_tag} #Novidade",
    ],
    "linkedin": [
        "Nos últimos meses, tenho percebido uma tendência importante: {tema}.\n\nEmpresários e gestores que entenderam isso saíram na frente. Veja como você pode aplicar isso no seu negócio.\n\n#Estratégia #{tema_tag} #Liderança #Negócios",
    ],
}

IDEIAS_DEMO = [
    "📊 Compartilhe dados e estatísticas relevantes do seu setor para gerar autoridade",
    "🎥 Faça um bastidores do seu negócio — mostre o processo de criação",
    "❓ Crie uma enquete sobre as maiores dificuldades do seu público",
    "🏆 Apresente um case de sucesso de cliente (com autorização)",
    "💡 Dê 5 dicas rápidas e práticas relacionadas ao seu nicho",
    "📅 Crie um calendário de conteúdo e compartilhe o tema da semana",
    "🤝 Colabore com outro criador do seu nicho (collab post)",
    "🎁 Anuncie uma promoção exclusiva para seguidores",
    "📖 Compartilhe uma lição aprendida na sua jornada empreendedora",
    "🔁 Reutilize conteúdo mais antigo com uma nova perspectiva",
]


# ─────────────────────────────────────────────────────────
#  GERAÇÃO VIA OPENAI
# ─────────────────────────────────────────────────────────

async def _gerar_com_openai(prompt: str) -> tuple[str, int]:
    """Chama a API OpenAI e retorna (texto_gerado, tokens_usados)."""
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um especialista em marketing digital e copywriting para redes sociais. "
                    "Escreva em português do Brasil, de forma envolvente e autêntica. "
                    "Sempre inclua emojis relevantes e hashtags quando solicitado."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.8,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        texto = data["choices"][0]["message"]["content"].strip()
        tokens = data["usage"]["total_tokens"]
        return texto, tokens


# ─────────────────────────────────────────────────────────
#  GERAR LEGENDA
# ─────────────────────────────────────────────────────────

async def gerar_legenda(
    db: Session,
    usuario: Usuario,
    tema: str,
    plataforma: str = "instagram",
    tom: str = "engajador",
    incluir_hashtags: bool = True,
) -> SugestaoIA:
    """
    Gera uma legenda para postagem.
    Salva em sugestoes_ia e retorna o objeto.
    """
    conteudo_gerado = ""
    modelo_usado = "demo"
    tokens_usados = 0

    if settings.OPENAI_API_KEY:
        try:
            hashtag_instrucao = "Inclua de 5 a 10 hashtags relevantes ao final." if incluir_hashtags else ""
            prompt = (
                f"Crie uma legenda {tom} para uma postagem no {plataforma} "
                f"sobre o tema: '{tema}'. "
                f"Seja criativo, use emojis estrategicamente. {hashtag_instrucao}"
            )
            conteudo_gerado, tokens_usados = await _gerar_com_openai(prompt)
            modelo_usado = "gpt-3.5-turbo"
        except Exception as e:
            logger.warning(f"OpenAI indisponível, usando demo: {e}")

    if not conteudo_gerado:
        # Fallback: templates pré-definidos
        opcoes = LEGENDAS_DEMO.get(plataforma.lower(), LEGENDAS_DEMO["instagram"])
        template = random.choice(opcoes)
        tag = tema.replace(" ", "").replace("-", "")
        conteudo_gerado = template.format(tema=tema, tema_tag=tag)
        modelo_usado = "template_demo"

    sugestao = SugestaoIA(
        usuario_id=usuario.id,
        tipo="legenda",
        prompt_entrada=f"tema:{tema}|plataforma:{plataforma}|tom:{tom}",
        conteudo_gerado=conteudo_gerado,
        modelo_usado=modelo_usado,
        tokens_usados=tokens_usados,
    )
    db.add(sugestao)
    db.commit()
    db.refresh(sugestao)
    return sugestao


# ─────────────────────────────────────────────────────────
#  GERAR IDEIAS
# ─────────────────────────────────────────────────────────

async def gerar_ideias(
    db: Session,
    usuario: Usuario,
    segmento: str,
    quantidade: int = 5,
    plataforma: str = None,
) -> SugestaoIA:
    """
    Gera ideias de conteúdo para um segmento.
    Salva em sugestoes_ia e retorna o objeto.
    """
    conteudo_gerado = ""
    modelo_usado = "demo"
    tokens_usados = 0

    if settings.OPENAI_API_KEY:
        try:
            plat_texto = f"para {plataforma}" if plataforma else "para redes sociais"
            prompt = (
                f"Gere {quantidade} ideias criativas de conteúdo {plat_texto} "
                f"para o segmento: '{segmento}'. "
                f"Formato: uma ideia por linha, numeradas, com emoji no início. "
                f"Ideias práticas e originais que gerem engajamento."
            )
            conteudo_gerado, tokens_usados = await _gerar_com_openai(prompt)
            modelo_usado = "gpt-3.5-turbo"
        except Exception as e:
            logger.warning(f"OpenAI indisponível, usando demo: {e}")

    if not conteudo_gerado:
        amostra = random.sample(IDEIAS_DEMO, min(quantidade, len(IDEIAS_DEMO)))
        linhas = [f"{i+1}. {ideia}" for i, ideia in enumerate(amostra)]
        conteudo_gerado = f"Ideias de conteúdo para {segmento}:\n\n" + "\n".join(linhas)
        modelo_usado = "template_demo"

    sugestao = SugestaoIA(
        usuario_id=usuario.id,
        tipo="ideia",
        prompt_entrada=f"segmento:{segmento}|quantidade:{quantidade}|plataforma:{plataforma}",
        conteudo_gerado=conteudo_gerado,
        modelo_usado=modelo_usado,
        tokens_usados=tokens_usados,
    )
    db.add(sugestao)
    db.commit()
    db.refresh(sugestao)
    return sugestao
