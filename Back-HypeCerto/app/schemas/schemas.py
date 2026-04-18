"""
schemas/schemas.py
Schemas Pydantic para validação de request/response da API REST.
Estrutura compatível com o que o frontend React consome via Axios/Fetch.
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime


# ═══════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str
    confirmPassword: str
    telefone: Optional[str] = None
    plan: Optional[str] = "free"

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


class ConectarContaRequest(BaseModel):
    plataforma_slug: str           # facebook, instagram, tiktok...
    access_token: str
    page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    nome_conta: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None


# ═══════════════════════════════════════════════
#  PROJETOS
# ═══════════════════════════════════════════════

class ProjetoCreate(BaseModel):
    nome_do_projeto: str  # Nome exato da coluna no banco
    area_do_projeto: Optional[str] = None
    responsavel: Optional[str] = None
    descricao: Optional[str] = None


class ProjetoResponse(BaseModel):
    id_projeto: int
    usuario_id: int
    data_criacao: datetime
    status: Optional[str] = "ativo"

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════
#  POSTAGENS
# ═══════════════════════════════════════════════

class PostagemCreate(BaseModel):
    titulo: Optional[str] = None
    conteudo: str
    projeto_id: Optional[int] = None
    tags: Optional[List[int]] = []


class PostagemUpdate(BaseModel):
    titulo: Optional[str] = None
    conteudo: Optional[str] = None
    status: Optional[str] = None
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

class AgendamentoCreate(BaseModel):
    postagem_id: int
    conta_social_id: int
    data_agendada: datetime


class AgendamentoUpdate(BaseModel):
    data_agendada: Optional[datetime] = None
    status_envio: Optional[str] = None


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
    tema: str
    plataforma: Optional[str] = "instagram"
    tom: Optional[str] = "engajador"     # engajador, profissional, divertido, informativo
    incluir_hashtags: Optional[bool] = True


class IAIdeiasRequest(BaseModel):
    segmento: str
    quantidade: Optional[int] = 5
    plataforma: Optional[str] = None


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
