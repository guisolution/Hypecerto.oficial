"""
models/models.py
Modelos SQLAlchemy mapeados para as tabelas EXISTENTES no Supabase.
⚠️ NÃO recria o banco — apenas adapta ao schema existente.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Enum, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import enum


# ─────────────────────────── ENUMS ───────────────────────────

class StatusEnvioEnum(str, enum.Enum):
    pendente = "pendente"
    agendado = "agendado"
    publicado = "publicado"
    erro = "erro"
    cancelado = "cancelado"


class PlanoTipoEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


# ─────────────────────────── MODELOS ─────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    telefone = Column(String(50))
    #foto_perfil = Column(Text)
    #ativo = Column(Boolean, default=True)
    #email_verificado = Column(Boolean, default=False)
    #criado_em = Column(DateTime(timezone=True), server_default=func.now())
    #atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    contas_sociais = relationship("ContaSocial", back_populates="usuario")
    postagens = relationship("Postagem", back_populates="usuario")
    assinaturas = relationship("Assinatura", back_populates="usuario")
    projetos = relationship("Projeto", back_populates="usuario")
    configuracoes = relationship("ConfiguracaoUsuario", back_populates="usuario", uselist=False)
    sugestoes_ia = relationship("SugestaoIA", back_populates="usuario")


class ContaSocial(Base):
    __tablename__ = "contas_sociais"

    id_conta = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plataforma_id = Column(Integer, ForeignKey("plataformas.id_plataforma"))
    nome_conta = Column(String(255))
    username = Column(String(255))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expira_em = Column(DateTime(timezone=True))
    page_id = Column(String(255))       # Facebook Page ID
    ig_user_id = Column(String(255))    # Instagram User ID
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="contas_sociais")
    plataforma = relationship("Plataforma", back_populates="contas_sociais")


class Plataforma(Base):
    __tablename__ = "plataformas"

    id_plataforma = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)   # Facebook, Instagram, TikTok...
    slug = Column(String(50), unique=True)
    icone_url = Column(Text)
    ativa = Column(Boolean, default=True)

    contas_sociais = relationship("ContaSocial", back_populates="plataforma")


class Projeto(Base):
    __tablename__ = "projetos"

    id_projeto = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome_do_projeto = Column(String(255), nullable=False)
    area_do_projeto = Column(String(255))
    responsavel = Column(String(255))
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    #atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="projetos")
    postagens = relationship("Postagem", back_populates="projeto")


class Postagem(Base):
    __tablename__ = "postagens"

    id_postagem = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    projeto_id = Column(Integer, ForeignKey("projetos.id_projeto"))
    titulo = Column(String(500))
    conteudo = Column(Text, nullable=False)
    status = Column(String(50), default="rascunho")  # rascunho, agendado, publicado, erro
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="postagens")
    projeto = relationship("Projeto", back_populates="postagens")
    agendamentos = relationship("Agendamento", back_populates="postagem")
    midias = relationship("Midia", back_populates="postagem")
    tags = relationship("Tag", secondary="postagem_tags", back_populates="postagens")
    metricas = relationship("Metrica", back_populates="postagem")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id_agendamento = Column(Integer, primary_key=True, index=True)
    postagem_id = Column(Integer, ForeignKey("postagens.id_postagem"), nullable=False)
    conta_social_id = Column(Integer, ForeignKey("contas_sociais.id_conta"), nullable=False)
    data_agendada = Column(DateTime(timezone=True), nullable=False)
    data_publicacao_real = Column(DateTime(timezone=True))
    status_envio = Column(String(50), default="agendado")  # agendado, publicado, erro, cancelado
    response_api = Column(JSON)      # resposta bruta da API Meta
    post_id_externo = Column(String(255))  # ID retornado pela Meta API
    tentativas = Column(Integer, default=0)
    erro_mensagem = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    postagem = relationship("Postagem", back_populates="agendamentos")
    conta_social = relationship("ContaSocial")


class Midia(Base):
    __tablename__ = "midias"

    id = Column(Integer, primary_key=True, index=True)
    postagem_id = Column(Integer, ForeignKey("postagens.id_postagem"))
    tipo = Column(String(50))          # imagem, video, audio
    url = Column(Text, nullable=False)
    nome_arquivo = Column(String(255))
    tamanho_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    postagem = relationship("Postagem", back_populates="midias")


class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(Integer, primary_key=True, index=True)
    postagem_id = Column(Integer, ForeignKey("postagens.id_postagem"))
    conta_social_id = Column(Integer, ForeignKey("contas_sociais.id_conta"))
    curtidas = Column(Integer, default=0)
    comentarios = Column(Integer, default=0)
    compartilhamentos = Column(Integer, default=0)
    alcance = Column(Integer, default=0)
    impressoes = Column(Integer, default=0)
    cliques = Column(Integer, default=0)
    data_coleta = Column(DateTime(timezone=True), server_default=func.now())

    postagem = relationship("Postagem", back_populates="metricas")


class Relatorio(Base):
    __tablename__ = "relatorios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String(255))
    tipo = Column(String(100))           # semanal, mensal, campanha
    periodo_inicio = Column(DateTime(timezone=True))
    periodo_fim = Column(DateTime(timezone=True))
    dados = Column(JSON)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class SugestaoIA(Base):
    __tablename__ = "sugestoes_ia"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String(100))           # legenda, ideia, hashtag
    prompt_entrada = Column(Text)
    conteudo_gerado = Column(Text)
    modelo_usado = Column(String(100))
    tokens_usados = Column(Integer)
    aprovado = Column(Boolean)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="sugestoes_ia")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nome = Column(String(100), nullable=False)
    cor = Column(String(20))

    postagens = relationship("Postagem", secondary="postagem_tags", back_populates="tags")


class PostagemTag(Base):
    __tablename__ = "postagem_tags"

    postagem_id = Column(Integer, ForeignKey("postagens.id_postagem"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class Plano(Base):
    __tablename__ = "planos"

    id_plano = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50))           # free, pro, enterprise
    preco_mensal = Column(Float, default=0.0)
    limite_postagens = Column(Integer)
    limite_canais = Column(Integer)
    recursos = Column(JSON)
    ativo = Column(Boolean, default=True)

    assinaturas = relationship("Assinatura", back_populates="plano")


class Assinatura(Base):
    __tablename__ = "assinaturas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plano_id = Column(Integer, ForeignKey("planos.id_plano"), nullable=False)
    status = Column(String(50), default="ativa")   # ativa, cancelada, expirada
    inicio = Column(DateTime(timezone=True))
    fim = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="assinaturas")
    plano = relationship("Plano", back_populates="assinaturas")


class Automacao(Base):
    __tablename__ = "automacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome = Column(String(255))
    tipo = Column(String(100))          # agendamento_recorrente, resposta_automatica
    configuracao = Column(JSON)
    ativa = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class Interacao(Base):
    __tablename__ = "interacoes"

    id = Column(Integer, primary_key=True, index=True)
    postagem_id = Column(Integer, ForeignKey("postagens.id_postagem"))
    conta_social_id = Column(Integer, ForeignKey("contas_sociais.id_conta"))
    tipo = Column(String(50))           # comentario, mensagem, curtida
    conteudo = Column(Text)
    autor_externo = Column(String(255))
    data_interacao = Column(DateTime(timezone=True))
    respondido = Column(Boolean, default=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())


class ConfiguracaoUsuario(Base):
    __tablename__ = "configuracoes_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    notificacoes_email = Column(Boolean, default=True)
    notificacoes_push = Column(Boolean, default=True)
    tema = Column(String(20), default="light")
    idioma = Column(String(10), default="pt-BR")
    fuso_horario = Column(String(100), default="America/Sao_Paulo")
    configuracoes_extras = Column(JSON)

    usuario = relationship("Usuario", back_populates="configuracoes")
