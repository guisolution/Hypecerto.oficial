"""
routers/projetos.py
CRUD de projetos — Totalmente sincronizado com o banco de dados e Create.tsx
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database.connection import get_db
from app.schemas.schemas import ProjetoCreate, ProjetoResponse, MessageResponse
from app.services.dependencies import get_current_user
from app.models.models import Usuario, Projeto

router = APIRouter(prefix="/projetos", tags=["Projetos"])


@router.get("", response_model=List[ProjetoResponse], summary="Listar projetos")
def listar_projetos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Usamos joinedload para trazer os dados do usuário e acessar o nome
    # Filtramos por usuario_id e status 'ativo' conforme as imagens do seu banco
    projetos = db.query(Projeto).options(joinedload(Projeto.usuario)).filter(
        Projeto.usuario_id == current_user.id,
        Projeto.status == "ativo"
    ).order_by(Projeto.data_criacao.desc()).all()
    
    # Mapeia o nome do usuário para o campo que o frontend espera exibir
    for p in projetos:
        p.nome_usuario = p.usuario.nome
        
    return projetos


@router.post("", response_model=ProjetoResponse, status_code=201, summary="Criar projeto")
def criar_projeto(
    body: ProjetoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cria projeto vinculando ao usuario_id.
    Mapeia os campos do Schema para as colunas exatas do banco de dados.
    """
    novo_projeto = Projeto(
        usuario_id=current_user.id,
        nome_do_projeto=body.nome_do_projeto,      # Coluna correta: nome_do_projeto
        area_do_projeto=body.area_do_projeto,      # Coluna correta: area_do_projeto
        responsavel=body.responsavel,
        descricao=body.descricao,
        ativo=True                # No banco a coluna chama-se 'status'
    )
    
    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)
    
    # Adiciona o nome do usuário para o retorno imediato ao frontend
    novo_projeto.nome_usuario = current_user.nome
    return novo_projeto


@router.get("/{projeto_id}", response_model=ProjetoResponse, summary="Buscar projeto")
def buscar_projeto(
    projeto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Busca usando a PK correta: id_projeto
    p = db.query(Projeto).options(joinedload(Projeto.usuario)).filter(
        Projeto.id_projeto == projeto_id,
        Projeto.usuario_id == current_user.id,
    ).first()
    
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    p.nome_usuario = p.usuario.nome
    return p


@router.put("/{projeto_id}", response_model=ProjetoResponse, summary="Editar projeto")
def editar_projeto(
    projeto_id: int,
    body: ProjetoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Projeto).filter(
        Projeto.id_projeto == projeto_id,
        Projeto.usuario_id == current_user.id,
    ).first()
    
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # Atualiza os campos respeitando os nomes das colunas
    p.nome_do_projeto = body.nome
    p.area_do_projeto = body.area
    p.responsavel = body.responsavel
    p.descricao = body.descricao
    
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{projeto_id}", response_model=MessageResponse, summary="Arquivar projeto")
def arquivar_projeto(
    projeto_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(Projeto).filter(
        Projeto.id_projeto == projeto_id,
        Projeto.usuario_id == current_user.id,
    ).first()
    
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Em vez de excluir, alteramos o status conforme seu padrão de 'ativo'
    p.status = "arquivado"
    db.commit()
    
    return {"message": "Projeto arquivado com sucesso", "success": True}