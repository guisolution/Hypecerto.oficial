"""TESTES DE INTEGRAÇÃO (API + ORM + SQLite) — código do repositório SEM modificação ("AS-IS").
Expectativa = comportamento descrito no README/docstrings. FAIL = defeito funcional real."""
import io, pytest

def _png():
    from PIL import Image
    b = io.BytesIO(); Image.new("RGB", (4, 4), "red").save(b, "PNG"); return b.getvalue()

# ---------- Auth (fluxo principal)
def test_I01_signup_login_me(client):
    r = client.post("/auth/signup", json={"nome":"Ana","email":"ana@x.com","password":"Senha123","confirmPassword":"Senha123"})
    assert r.status_code == 201 and r.json()["token_type"] == "bearer"
    r = client.post("/auth/login", json={"email":"ana@x.com","password":"Senha123"}); assert r.status_code == 200
    tok = r.json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {tok}"}); assert r.status_code == 200 and r.json()["email"] == "ana@x.com"
def test_I02_login_senha_errada_401(client, user_a):
    assert client.post("/auth/login", json={"email":"alice@example.com","password":"errada"}).status_code == 401
def test_I03_email_duplicado_400(client, user_a):
    r = client.post("/auth/signup", json={"nome":"x","email":"alice@example.com","password":"Senha123","confirmPassword":"Senha123"}); assert r.status_code == 400
def test_I04_rota_protegida_sem_token_403_ou_401(client):
    assert client.get("/auth/me").status_code in (401, 403)
def test_I05_token_invalido_401(client):
    assert client.get("/auth/me", headers={"Authorization":"Bearer lixo"}).status_code == 401
def test_I06_resposta_nao_vaza_senha_hash(client, user_a):
    r = client.get("/auth/me", headers=user_a["h"]); assert "senha" not in r.text.lower() and "hash" not in r.text.lower()
def test_I07_signup_senhas_divergentes_422(client):
    r = client.post("/auth/signup", json={"nome":"a","email":"a@b.com","password":"1","confirmPassword":"2"}); assert r.status_code == 422

# ---------- Funcionalidades de negócio (as-is)
def test_I10_criar_projeto(client, user_a):
    r = client.post("/projetos", json={"nome_do_projeto":"P1","area_do_projeto":"mkt"}, headers=user_a["h"]); assert r.status_code == 201, r.text
def test_I11_listar_projetos(client, user_a):
    assert client.get("/projetos", headers=user_a["h"]).status_code == 200
def test_I12_editar_projeto(client, user_a):
    client.post("/projetos", json={"nome_do_projeto":"P1"}, headers=user_a["h"])
    r = client.put("/projetos/1", json={"nome_do_projeto":"P2"}, headers=user_a["h"]); assert r.status_code == 200, r.text
def test_I13_criar_postagem(client, user_a):
    r = client.post("/posts", json={"titulo":"t","conteudo":"c"}, headers=user_a["h"]); assert r.status_code == 201, r.text
def test_I14_listar_postagens(client, user_a):
    assert client.get("/posts", headers=user_a["h"]).status_code == 200
def test_I15_conectar_canal(client, user_a):
    r = client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"tok"}, headers=user_a["h"]); assert r.status_code == 201, r.text
def test_I16_listar_canais(client, user_a):
    assert client.get("/channels", headers=user_a["h"]).status_code == 200
def test_I17_plataformas_padrao(client):
    r = client.get("/channels/plataformas"); assert r.status_code == 200 and len(r.json()) >= 6
def test_I18_dashboard(client, user_a):
    assert client.get("/resultados/dashboard", headers=user_a["h"]).status_code == 200
def test_I19_listar_agendamentos(client, user_a):
    assert client.get("/agendamentos", headers=user_a["h"]).status_code == 200
def test_I20_gerar_legenda_ia_demo(client, user_a):
    r = client.post("/ia/legenda", json={"tema":"promo"}, headers=user_a["h"]); assert r.status_code == 200, r.text
def test_I21_gerar_ideias_ia_demo(client, user_a):
    r = client.post("/ia/ideias", json={"segmento":"academia","quantidade":3}, headers=user_a["h"]); assert r.status_code == 200, r.text
def test_I22_historico_ia(client, user_a):
    assert client.get("/ia/historico", headers=user_a["h"]).status_code == 200
def test_I23_gerar_relatorio(client, user_a):
    assert client.post("/resultados/relatorios/gerar", headers=user_a["h"]).status_code == 200
def test_I24_listar_metricas(client, user_a):
    assert client.get("/resultados/metricas", headers=user_a["h"]).status_code == 200
def test_I25_progresso_projetos(client, user_a):
    assert client.get("/resultados/projetos", headers=user_a["h"]).status_code == 200
def test_I26_meta_status(client, user_a):
    # após correção R14b a rota exige login
    assert client.get("/meta/status", headers=user_a["h"]).status_code == 200
def test_I27_health(client):
    # /health importa scheduler; scheduler.running False sem lifespan, mas endpoint deve responder
    assert client.get("/health").status_code == 200
def test_I28_upload_midia(client, user_a):
    client.post("/posts", json={"conteudo":"c"}, headers=user_a["h"])
    r = client.post("/posts/1/midia", files={"file":("a.png", _png(), "image/png")}, headers=user_a["h"]); assert r.status_code == 200, r.text
def test_I29_publicar_direto(client, user_a):
    r = client.post("/meta/publicar-direto?postagem_id=1&conta_social_id=1", headers=user_a["h"]); assert r.status_code in (200, 404), r.text
def test_I30_esqueci_senha(client):
    assert client.post("/auth/forgot-password?email=a@b.com").status_code == 200
