"""
schemas/schemas.py
Schemas Pydantic para validação de request/response da API REST.
Estrutura compatível com o que o frontend React consome via Axios/Fetch.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime, timezone
import re


# ═══════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class SignupRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)   # 72 = limite do bcrypt (sem truncamento silencioso)
    confirmPassword: str
    telefone: Optional[str] = Field(default=None, max_length=30)
    plan: Optional[Literal["free", "pro", "enterprise"]] = "free"

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Nome não pode ser vazio")
        return v

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Senha excede 72 bytes")
        if not (re.search(r"[A-Z]", v) and re.search(r"[a-z]", v) and re.search(r"[0-9]", v)):
            raise ValueError("A senha deve conter maiúscula, minúscula e número")
        return v

    @field_validator("confirmPassword")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("As senhas não coincidem")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UsuarioResponse"


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    foto_perfil: Optional[str] = None
    ativo: bool = None
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  CONTAS SOCIAIS / CANAIS
# ═══════════════════════════════════════════════

class ContaSocialResponse(BaseModel):
    id: int
    plataforma_id: Optional[int]
    nome_conta: Optional[str]
    username: Optional[str]
    page_id: Optional[str]
    ig_user_id: Optional[str]
    ativa: bool
    plataforma_nome: Optional[str] = None
    criado_em: Optional[datetime]

    class Config:
        from_attributes = True


PLATAFORMAS_PERMITIDAS = ("facebook", "instagram", "tiktok", "youtube", "whatsapp", "linkedin")


class ConectarContaRequest(BaseModel):
    plataforma_slug: Literal["facebook", "instagram", "tiktok", "youtube", "whatsapp", "linkedin"]
    access_token: str = Field(min_length=1, max_length=4096)
    page_id: Optional[str] = Field(default=None, max_length=255)
    ig_user_id: Optional[str] = Field(default=None, max_length=255)
    nome_conta: Optional[str] = Field(default=None, max_length=255)
    permissions: Optional[Dict[str, bool]] = None


# ═══════════════════════════════════════════════
#  PROJETOS
# ═══════════════════════════════════════════════

class ProjetoCreate(BaseModel):
    nome_do_projeto: str = Field(min_length=1, max_length=255)
    area_do_projeto: Optional[str] = Field(default=None, max_length=255)
    responsavel: Optional[str] = Field(default=None, max_length=255)
    descricao: Optional[str] = Field(default=None, max_length=5000)


class ProjetoResponse(BaseModel):
    id_projeto: int
    usuario_id: int
    nome_do_projeto: Optional[str] = None
    area_do_projeto: Optional[str] = None
    responsavel: Optional[str] = None
    descricao: Optional[str] = None
    data_criacao: Optional[datetime] = None
    status: Optional[str] = "ativo"
    nome_usuario: Optional[str] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  POSTAGENS
# ═══════════════════════════════════════════════

class PostagemCreate(BaseModel):
    titulo: Optional[str] = Field(default=None, max_length=500)
    conteudo: str = Field(min_length=1, max_length=20000)
    projeto_id: Optional[int] = None
    tags: Optional[List[int]] = []


class PostagemUpdate(BaseModel):
    titulo: Optional[str] = Field(default=None, max_length=500)
    conteudo: Optional[str] = Field(default=None, min_length=1, max_length=20000)
    # 'publicado' e 'erro' só são definidos pelo sistema ao publicar, nunca pelo cliente
    status: Optional[Literal["rascunho", "agendado"]] = None
    projeto_id: Optional[int] = None


class MidiaResponse(BaseModel):
    id: int
    tipo: Optional[str]
    url: str
    nome_arquivo: Optional[str]
    mime_type: Optional[str]

    class Config:
        from_attributes = True


class AgendamentoResumido(BaseModel):
    id: int
    data_agendada: datetime
    status_envio: str
    plataforma_nome: Optional[str] = None

    class Config:
        from_attributes = True


class PostagemResponse(BaseModel):
    id: int
    titulo: Optional[str]
    conteudo: str
    status: str
    projeto_id: Optional[int]
    projeto_nome: Optional[str] = None
    midias: List[MidiaResponse] = []
    agendamentos: List[AgendamentoResumido] = []
    criado_em: Optional[datetime]
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  AGENDAMENTOS
# ═══════════════════════════════════════════════

def _futuro(v: datetime) -> datetime:
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    if v < datetime.now(timezone.utc):
        raise ValueError("data_agendada deve estar no futuro")
    return v


class AgendamentoCreate(BaseModel):
    postagem_id: int
    conta_social_id: int
    data_agendada: datetime

    @field_validator("data_agendada")
    @classmethod
    def _data_futura(cls, v):
        return _futuro(v)


class AgendamentoUpdate(BaseModel):
    data_agendada: Optional[datetime] = None
    # o cliente só pode cancelar ou reagendar; 'publicado'/'erro' são definidos pelo sistema
    status_envio: Optional[Literal["agendado", "cancelado"]] = None

    @field_validator("data_agendada")
    @classmethod
    def _data_futura(cls, v):
        return _futuro(v) if v is not None else v


class AgendamentoResponse(BaseModel):
    id: int
    postagem_id: int
    conta_social_id: int
    data_agendada: datetime
    data_publicacao_real: Optional[datetime]
    status_envio: str
    post_id_externo: Optional[str]
    tentativas: int
    erro_mensagem: Optional[str]
    criado_em: Optional[datetime]

    # Dados enriquecidos
    postagem_titulo: Optional[str] = None
    postagem_conteudo: Optional[str] = None
    plataforma_nome: Optional[str] = None
    channels: Optional[List[str]] = []

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  META / PUBLICAÇÃO
# ═══════════════════════════════════════════════

class PublicarRequest(BaseModel):
    agendamento_id: int


class PublicarResponse(BaseModel):
    success: bool
    message: str
    post_id_externo: Optional[str] = None
    mock: bool = False


# ═══════════════════════════════════════════════
#  IA
# ═══════════════════════════════════════════════

class IALegendaRequest(BaseModel):
    tema: str = Field(min_length=1, max_length=300)
    plataforma: Literal["instagram", "facebook", "linkedin", "tiktok", "youtube", "whatsapp"] = "instagram"
    tom: Literal["engajador", "profissional", "divertido", "informativo"] = "engajador"
    incluir_hashtags: bool = True

    @field_validator("plataforma", "tom", "incluir_hashtags", mode="before")
    @classmethod
    def _null_vira_padrao(cls, v, info):
        if v is None:
            return {"plataforma": "instagram", "tom": "engajador", "incluir_hashtags": True}[info.field_name]
        return v


class IAIdeiasRequest(BaseModel):
    segmento: str = Field(min_length=1, max_length=300)
    quantidade: int = Field(default=5, ge=1, le=10)
    plataforma: Optional[Literal["instagram", "facebook", "linkedin", "tiktok", "youtube", "whatsapp"]] = None


class IAResponse(BaseModel):
    id: int
    tipo: str
    conteudo_gerado: str
    criado_em: Optional[datetime]

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  MÉTRICAS / RELATÓRIOS
# ═══════════════════════════════════════════════

class MetricaResponse(BaseModel):
    id: int
    postagem_id: Optional[int]
    curtidas: int
    comentarios: int
    compartilhamentos: int
    alcance: int
    impressoes: int
    cliques: int
    data_coleta: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardMetricasResponse(BaseModel):
    total_postagens: int
    postagens_publicadas: int
    postagens_agendadas: int
    total_curtidas: int
    total_comentarios: int
    total_compartilhamentos: int
    total_alcance: int
    atividade_semanal: List[Dict[str, Any]] = []
    postagens_recentes: List[PostagemResponse] = []


class RelatorioResponse(BaseModel):
    id: int
    titulo: Optional[str]
    tipo: Optional[str]
    periodo_inicio: Optional[datetime]
    periodo_fim: Optional[datetime]
    dados: Optional[Dict[str, Any]]
    criado_em: Optional[datetime]

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  GENÉRICO
# ═══════════════════════════════════════════════

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
