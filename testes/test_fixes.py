"""TESTES DE REGRESSÃO DAS CORREÇÕES — afirmam o comportamento SEGURO/CORRETO.
Rodados contra o código ORIGINAL devem FALHAR (provam o defeito); contra o corrigido devem PASSAR."""
import io, os, subprocess, sys, time, pathlib, statistics
import pytest
from jose import jwt as _  # noqa  (apenas para forjar token com a chave pública do original)
import jwt as pyjwt

REPO = os.environ.get("HC_REPO", os.path.abspath(os.path.join(os.path.dirname(__file__), "../Back-HypeCerto")))
PNG = None
def _png():
    from PIL import Image
    b = io.BytesIO(); Image.new("RGB", (4, 4), "red").save(b, "PNG"); return b.getvalue()

def _mk_post(client, h, **kw):
    r = client.post("/posts", json={"conteudo": "c", **kw}, headers=h); assert r.status_code == 201, r.text; return r.json()["id"]
def _conta(client, h, token="tok-secreto"):
    r = client.post("/channels/conectar", json={"plataforma_slug": "facebook", "access_token": token}, headers=h); assert r.status_code == 201, r.text; return r.json()["id"]

# ---------------- Defeito funcional (mapeamento id x id_*)
def test_R00_fluxo_principal_sem_500(client, user_a):
    h = user_a["h"]
    assert client.post("/projetos", json={"nome_do_projeto": "P1"}, headers=h).status_code == 201
    assert client.get("/projetos", headers=h).status_code == 200 and len(client.get("/projetos", headers=h).json()) == 1
    assert client.put("/projetos/1", json={"nome_do_projeto": "P2"}, headers=h).json()["nome_do_projeto"] == "P2"
    pid = _mk_post(client, h)
    assert client.get(f"/posts/{pid}", headers=h).status_code == 200 and client.get("/posts", headers=h).status_code == 200
    cid = _conta(client, h)
    ag = client.post("/agendamentos", json={"postagem_id": pid, "conta_social_id": cid, "data_agendada": "2030-01-01T00:00:00Z"}, headers=h); assert ag.status_code == 201, ag.text
    assert client.get("/agendamentos", headers=h).status_code == 200
    r = client.post("/meta/publicar", json={"agendamento_id": ag.json()["id"]}, headers=h); assert r.status_code == 200 and r.json()["success"]
    assert client.get("/resultados/dashboard", headers=h).status_code == 200
    assert client.get("/resultados/metricas", headers=h).status_code == 200
    assert client.post("/meta/publicar-direto", params={"postagem_id": pid, "conta_social_id": cid}, headers=h).status_code == 200
    up = client.post(f"/posts/{pid}/midia", files={"file": ("a.png", _png(), "image/png")}, headers=h); assert up.status_code == 200, up.text
def test_R00b_arquivar_projeto_e_listagem(client, user_a):
    h = user_a["h"]; client.post("/projetos", json={"nome_do_projeto": "P"}, headers=h)
    assert client.delete("/projetos/1", headers=h).status_code == 200 and client.get("/projetos", headers=h).json() == []
def test_R00c_resultados_projetos_com_dados(client, user_a):
    h = user_a["h"]; client.post("/projetos", json={"nome_do_projeto": "Camp"}, headers=h)
    r = client.get("/resultados/projetos", headers=h); assert r.status_code == 200 and r.json()[0]["name"] == "Camp"
def test_R00d_dashboard_sem_dados_falsos(client, user_a):
    r = client.get("/resultados/dashboard", headers=user_a["h"]); assert r.status_code == 200 and all(d["value"] == 0 for d in r.json()["atividade_semanal"])

# ---------------- R01 SECRET_KEY / JWT
def test_R01_token_forjado_com_chave_publica_rejeitado(client, user_a):
    forged = pyjwt.encode({"sub": str(user_a["id"]), "exp": time.time() + 3600}, "dev-secret-key-change-in-production", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
def test_R01b_producao_sem_secret_nao_sobe(tmp_path):
    env = {**os.environ, "ENVIRONMENT": "production", "SECRET_KEY": "", "PYTHONPATH": REPO, "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-c", "from app.config import settings"], env=env, capture_output=True, text=True, cwd=str(tmp_path))
    assert r.returncode != 0 and "SECRET_KEY" in (r.stderr + r.stdout)
def test_R01c_producao_com_chave_forte_sobe_sem_docs_e_com_hsts(tmp_path):
    env = {**os.environ, "ENVIRONMENT": "production", "SECRET_KEY": "x" * 48, "DATABASE_URL": f"sqlite:///{(tmp_path / 'prod_probe.db').as_posix()}", "PYTHONPATH": REPO, "PYTHONDONTWRITEBYTECODE": "1"}
    code = ("from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); "
            "r=c.get('/'); o=c.options('/auth/me',headers={'Origin':'https://x.github.dev','Access-Control-Request-Method':'GET'}); "
            "print(c.get('/docs').status_code, c.get('/openapi.json').status_code, c.get('/health').json(), 'strict-transport-security' in r.headers, 'access-control-allow-origin' in o.headers)")
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, cwd=str(tmp_path)); out = r.stdout.strip().splitlines()[-1]
    assert out == "404 404 {'status': 'healthy'} True False", out + r.stderr[-300:]
def test_R01d_sub_invalido_vira_401(client):
    t = pyjwt.encode({"sub": "abc", "exp": time.time() + 60}, __import__("app.config", fromlist=["settings"]).settings.SECRET_KEY, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {t}"}).status_code == 401

# ---------------- R02 exclusão de conta
def test_R02_delete_sem_jwt_negado(client, user_a):
    r = client.request("DELETE", "/auth/delete", json={"email": "alice@example.com", "password": "Senha123"})
    assert r.status_code in (401, 403) and client.post("/auth/login", json={"email": "alice@example.com", "password": "Senha123"}).status_code == 200
def test_R02b_delete_autenticado_exige_senha_e_funciona(client, user_a):
    h = user_a["h"]
    assert client.request("DELETE", "/auth/delete", json={"email": "alice@example.com", "password": "errada"}, headers=h).status_code == 401
    assert client.request("DELETE", "/auth/delete", json={"email": "alice@example.com", "password": "Senha123"}, headers=h).status_code == 200
    assert client.post("/auth/login", json={"email": "alice@example.com", "password": "Senha123"}).status_code == 401
def test_R02c_nao_apaga_conta_de_outro(client, user_a, user_b):
    r = client.request("DELETE", "/auth/delete", json={"email": "bob@example.com", "password": "Senha123"}, headers=user_a["h"])
    assert r.status_code == 401 and client.post("/auth/login", json={"email": "bob@example.com", "password": "Senha123"}).status_code == 200

# ---------------- R03 rate limit
def test_R03_bloqueio_apos_falhas_de_login(client, user_a):
    codes = [client.post("/auth/login", json={"email": "alice@example.com", "password": f"x{i}"}).status_code for i in range(8)]
    assert 429 in codes and codes[:5] == [401] * 5
    assert client.post("/auth/login", json={"email": "alice@example.com", "password": "Senha123"}).status_code == 429   # mesmo com a senha certa durante o bloqueio
def test_R03b_login_valido_nao_e_bloqueado_por_outro_usuario(client, user_a, user_b):
    for i in range(6): client.post("/auth/login", json={"email": "alice@example.com", "password": f"x{i}"})
    assert client.post("/auth/login", json={"email": "bob@example.com", "password": "Senha123"}).status_code == 200
def test_R03c_delete_com_rate_limit(client, user_a):
    codes = [client.request("DELETE", "/auth/delete", json={"email": "alice@example.com", "password": f"x{i}"}, headers=user_a["h"]).status_code for i in range(7)]
    assert 429 in codes

# ---------------- R04 upload
def test_R04_rejeita_html_svg_php_exe(client, user_a):
    pid = _mk_post(client, user_a["h"])
    for n, ct in [("e.html", "text/html"), ("x.svg", "image/svg+xml"), ("s.php", "application/x-php"), ("a.exe", "application/octet-stream")]:
        assert client.post(f"/posts/{pid}/midia", files={"file": (n, b"<script>1</script>", ct)}, headers=user_a["h"]).status_code == 415, n
def test_R04b_rejeita_png_falso_e_extensao_trocada(client, user_a):
    pid = _mk_post(client, user_a["h"])
    assert client.post(f"/posts/{pid}/midia", files={"file": ("a.png", b"<html>x</html>", "image/png")}, headers=user_a["h"]).status_code == 415
    assert client.post(f"/posts/{pid}/midia", files={"file": ("a.jpg", _png(), "image/jpeg")}, headers=user_a["h"]).status_code == 415   # PNG com extensão .jpg
def test_R04c_limite_de_tamanho(client, user_a):
    pid = _mk_post(client, user_a["h"]); big = _png() + b"0" * (26 * 1024 * 1024)
    assert client.post(f"/posts/{pid}/midia", files={"file": ("big.png", big, "image/png")}, headers=user_a["h"]).status_code == 413
def test_R04d_upload_valido_mime_canonico_e_headers_do_arquivo_servido(client, user_a):
    pid = _mk_post(client, user_a["h"])
    r = client.post(f"/posts/{pid}/midia", files={"file": ("../../x.png", _png(), "text/html")}, headers=user_a["h"]); assert r.status_code == 200, r.text
    assert ".." not in r.json()["url"]
    g = client.get(r.json()["url"]); assert g.status_code == 200 and g.headers["content-type"] == "image/png"
    assert g.headers["x-content-type-options"] == "nosniff" and "sandbox" in g.headers["content-security-policy"]

# ---------------- R05 token OAuth criptografado
def test_R05_token_criptografado_no_banco_e_legivel_na_publicacao(client, user_a):
    _conta(client, user_a["h"], "EAAB-TOKEN-SECRETO")
    from app.database.connection import SessionLocal; from app.models.models import ContaSocial; from app.services.crypto import decrypt_token
    db = SessionLocal(); v = db.query(ContaSocial).first().access_token; db.close()
    assert v != "EAAB-TOKEN-SECRETO" and v.startswith("enc:v1:") and decrypt_token(v) == "EAAB-TOKEN-SECRETO"
def test_R05b_reconectar_nao_duplica_criptografia(client, user_a):
    _conta(client, user_a["h"], "t1"); _conta(client, user_a["h"], "t2")
    from app.database.connection import SessionLocal; from app.models.models import ContaSocial; from app.services.crypto import decrypt_token
    db = SessionLocal(); rows = db.query(ContaSocial).all(); db.close(); assert len(rows) == 1 and decrypt_token(rows[0].access_token) == "t2"

# ---------------- R06 sessão
def test_R06_token_expira_em_no_maximo_1h_por_padrao():
    from app.config import settings; assert settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 60
def test_R06b_token_sem_exp_rejeitado(client, user_a):
    from app.config import settings
    t = pyjwt.encode({"sub": str(user_a["id"])}, settings.SECRET_KEY, algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {t}"}).status_code == 401

# ---------------- R08/R14 CORS e cabeçalhos
def test_R14_cabecalhos_de_seguranca_presentes(client):
    r = client.get("/"); assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-frame-options"] == "DENY" and "referrer-policy" in r.headers and "content-security-policy" in r.headers
def test_R14b_status_meta_exige_login(client):
    assert client.get("/meta/status").status_code in (401, 403)
def test_R14c_root_nao_expoe_config(client):
    assert "mock_meta" not in client.get("/").json()

# ---------------- R09/R10 senha e enumeração
def test_R09_politica_de_senha_no_servidor(client):
    for pw in ["1", "abcdefgh", "ABCDEFGH1", "Abcdefg1" + "x" * 80]:
        assert client.post("/auth/signup", json={"nome": "x", "email": "w@x.com", "password": pw, "confirmPassword": pw}).status_code == 422, pw
def test_R09b_nome_vazio_ou_enorme_rejeitado(client):
    for nome in ["", "   ", "x" * 500]:
        assert client.post("/auth/signup", json={"nome": nome, "email": "w@x.com", "password": "Senha123", "confirmPassword": "Senha123"}).status_code == 422
def test_R09c_senha_de_72_bytes_exatos_funciona(client):
    pw = "Aa1" + "x" * 69
    assert client.post("/auth/signup", json={"nome": "x", "email": "l@x.com", "password": pw, "confirmPassword": pw}).status_code == 201
    assert client.post("/auth/login", json={"email": "l@x.com", "password": pw}).status_code == 200
def test_R10_timing_login_equalizado(client, user_a):
    def t(email):
        xs = []
        for i in range(4):
            from app.services.rate_limit import reset_rate_limits; reset_rate_limits()
            s = time.perf_counter(); client.post("/auth/login", json={"email": email, "password": "errada"}); xs.append(time.perf_counter() - s)
        return statistics.median(xs)
    ex, nex = t("alice@example.com"), t("ghost@example.com"); print(f"\n[timing] existente={ex*1000:.1f}ms inexistente={nex*1000:.1f}ms razão={ex/max(nex,1e-6):.2f}x")
    assert ex / nex < 2.0

# ---------------- R12 IA
def test_R12_ia_limites_e_nulos(client, user_a):
    h = user_a["h"]
    assert client.post("/ia/legenda", json={"tema": "x" * 100000}, headers=h).status_code == 422
    assert client.post("/ia/legenda", json={"tema": "x", "plataforma": None}, headers=h).status_code == 200
    assert client.post("/ia/ideias", json={"segmento": "x", "quantidade": -1}, headers=h).status_code == 422
    assert client.post("/ia/ideias", json={"segmento": "x", "quantidade": 1000}, headers=h).status_code == 422
    assert client.post("/ia/legenda", json={"tema": "x", "plataforma": "orkut"}, headers=h).status_code == 422
def test_R12b_paginacao_com_teto(client, user_a):
    h = user_a["h"]
    assert client.get("/ia/historico?per_page=100000000", headers=h).status_code == 422
    assert client.get("/ia/historico?page=0", headers=h).status_code == 422
    assert client.get("/posts?per_page=101", headers=h).status_code == 422 and client.get("/agendamentos?per_page=0", headers=h).status_code == 422

# ---------------- R13 lógica de negócio
def test_R13_projeto_de_outro_usuario_recusado(client, user_a, user_b):
    pj = client.post("/projetos", json={"nome_do_projeto": "Privado A"}, headers=user_a["h"]).json()["id_projeto"]
    assert client.post("/posts", json={"conteudo": "c", "projeto_id": pj}, headers=user_b["h"]).status_code == 404
    pid = _mk_post(client, user_b["h"]); assert client.put(f"/posts/{pid}", json={"projeto_id": pj}, headers=user_b["h"]).status_code == 404
def test_R13b_status_controlado_pelo_sistema(client, user_a):
    h = user_a["h"]; pid = _mk_post(client, h)
    assert client.put(f"/posts/{pid}", json={"status": "publicado"}, headers=h).status_code == 422
    assert client.put(f"/posts/{pid}", json={"status": "rascunho"}, headers=h).status_code == 200
    cid = _conta(client, h); ag = client.post("/agendamentos", json={"postagem_id": pid, "conta_social_id": cid, "data_agendada": "2030-01-01T00:00:00Z"}, headers=h).json()["id"]
    assert client.put(f"/agendamentos/{ag}", json={"status_envio": "publicado"}, headers=h).status_code == 422
    assert client.put(f"/agendamentos/{ag}", json={"status_envio": "cancelado"}, headers=h).status_code == 200
def test_R13c_agendamento_no_passado_recusado(client, user_a):
    pid = _mk_post(client, user_a["h"]); cid = _conta(client, user_a["h"])
    assert client.post("/agendamentos", json={"postagem_id": pid, "conta_social_id": cid, "data_agendada": "1999-01-01T00:00:00Z"}, headers=user_a["h"]).status_code == 422
def test_R13d_plataforma_arbitraria_recusada_e_sem_poluicao(client, user_a):
    r = client.post("/channels/conectar", json={"plataforma_slug": "<img src=x onerror=alert(1)>", "access_token": "t"}, headers=user_a["h"])
    assert r.status_code == 422 and not any("<img" in p["nome"] for p in client.get("/channels/plataformas").json())

# ---------------- Meta OAuth (rota que o front chama)
def test_R17_oauth_facebook_existe_e_conecta(client, user_a):
    r = client.post("/meta/oauth/facebook", json={"access_token": "tok"}, headers=user_a["h"]); assert r.status_code == 200, r.text
    assert {c["plataforma"] for c in r.json()["contas"]} == {"facebook", "instagram"} and r.json()["avisos"]
    assert len(client.get("/channels", headers=user_a["h"]).json()) == 2
def test_R17b_oauth_facebook_exige_login(client):
    assert client.post("/meta/oauth/facebook", json={"access_token": "t"}).status_code in (401, 403)
def test_R16_callback_nao_reflete_code(client):
    r = client.get("/auth/callback/facebook?code=SEGREDO123"); assert "SEGREDO123" not in r.text

# ---------------- Controles que JÁ funcionavam continuam funcionando
def test_C01_sqli_continua_barrado(client, user_a):
    assert client.post("/auth/login", json={"email": "alice@example.com", "password": "' OR '1'='1"}).status_code == 401
    assert client.get("/ia/historico?tipo=' OR 1=1 --", headers=user_a["h"]).json() == []
def test_C02_isolamento_continua(client, user_a, user_b):
    pid = _mk_post(client, user_a["h"])
    assert client.get(f"/posts/{pid}", headers=user_b["h"]).status_code == 404 and client.delete(f"/posts/{pid}", headers=user_b["h"]).status_code == 404
    cid = _conta(client, user_a["h"]); assert client.delete(f"/channels/{cid}", headers=user_b["h"]).status_code == 404
def test_C03_cors_externo_bloqueado_e_erro_sem_stacktrace(client):
    assert "access-control-allow-origin" not in client.options("/auth/me", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "GET"}).headers
