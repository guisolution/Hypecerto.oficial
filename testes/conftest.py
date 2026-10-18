"""Harness de testes (externo ao repositório). Usa SQLite isolado; nenhum arquivo do repo é alterado."""
import os, sys, tempfile, pathlib
REPO = os.environ.get("HC_REPO", "/home/claude/guisolution/hypecerto.oficial/Back-HypeCerto")
sys.path.insert(0, REPO)
_db = pathlib.Path(tempfile.mkdtemp()) / "t.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"
os.environ.pop("SECRET_KEY", None)           # força uso do DEFAULT do repositório
os.environ["USE_MOCK_META_API"] = "True"
os.environ["OPENAI_API_KEY"] = ""
import pytest
from fastapi.testclient import TestClient
from app.database.connection import Base, engine
from app.main import app
import app.models.models as M

@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    try:
        from app.services.rate_limit import reset_rate_limits; reset_rate_limits()
    except ImportError:
        pass
    yield

@pytest.fixture
def client():
    # sem 'with' => não dispara lifespan/scheduler; raise_server_exceptions=False => 500 viram resposta HTTP
    return TestClient(app, raise_server_exceptions=False)

def _signup(client, nome, email, pw="Senha123"):
    r = client.post("/auth/signup", json={"nome": nome, "email": email, "password": pw, "confirmPassword": pw})
    return r

@pytest.fixture
def user_a(client):
    r = _signup(client, "Alice", "alice@example.com"); assert r.status_code == 201, r.text
    j = r.json(); return {"token": j["access_token"], "id": j["user"]["id"], "h": {"Authorization": f"Bearer {j['access_token']}"}}

@pytest.fixture
def user_b(client):
    r = _signup(client, "Bob", "bob@example.com"); assert r.status_code == 201, r.text
    j = r.json(); return {"token": j["access_token"], "id": j["user"]["id"], "h": {"Authorization": f"Bearer {j['access_token']}"}}

@pytest.fixture
def alias_pk():
    """APENAS para sondagem: cria aliases .id -> PK real, simulando a correção do bug de mapeamento,
    para permitir testar a lógica de autorização/negócio que fica 'atrás' do bug. Marcado nos relatórios."""
    if hasattr(M.Postagem, "id"):      # código já corrigido: nada a simular
        yield; return
    M.Postagem.id = M.Postagem.id_postagem
    M.Agendamento.id = M.Agendamento.id_agendamento
    M.ContaSocial.id = M.ContaSocial.id_conta
    M.Plataforma.id = M.Plataforma.id_plataforma
    M.Projeto.id = M.Projeto.id_projeto
    M.Projeto.nome = M.Projeto.nome_do_projeto
    M.Projeto.status = M.Projeto.ativo
    yield
    for cls, attr in [(M.Postagem,"id"),(M.Agendamento,"id"),(M.ContaSocial,"id"),(M.Plataforma,"id"),(M.Projeto,"id"),(M.Projeto,"nome"),(M.Projeto,"status")]:
        try: delattr(cls, attr)
        except Exception: pass
