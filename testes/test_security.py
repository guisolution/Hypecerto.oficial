"""TESTES DE SEGURANÇA (DAST leve contra a API em processo).
Convenção: nome termina com _VULN => o teste PASSA quando a vulnerabilidade É CONFIRMADA (evidência).
           nome termina com _OK   => o teste PASSA quando o controle de segurança FUNCIONA."""
import os, time, statistics, pathlib
from jose import jwt
import pytest

pytestmark = pytest.mark.skip(
    reason="Auditoria PRE-correção: estes testes afirmam as vulnerabilidades originais, já corrigidas. "
           "Cobertura atual em test_fixes.py; registro do estado original em evidencias/50_fixes_on_original.txt."
)

# ---------------- Autenticação / sessão
def test_S01_forjar_jwt_com_secret_padrao_VULN(client, user_a):
    forged = jwt.encode({"sub": str(user_a["id"]), "exp": time.time()+3600}, "dev-secret-key-change-in-production", algorithm="HS256")
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 200 and r.json()["email"] == "alice@example.com"   # takeover sem senha
def test_S02_logout_nao_invalida_token_VULN(client, user_a):
    assert client.post("/auth/logout", headers=user_a["h"]).status_code == 200
    assert client.get("/auth/me", headers=user_a["h"]).status_code == 200      # token segue válido (7 dias)
def test_S03_sem_rate_limit_brute_force_login_VULN(client, user_a):
    codes = [client.post("/auth/login", json={"email":"alice@example.com","password":f"x{i}"}).status_code for i in range(40)]
    assert set(codes) == {401}                                                 # 40 tentativas, nenhum 429/lockout
def test_S04_delete_account_sem_jwt_VULN(client, user_a):
    r = client.request("DELETE", "/auth/delete", json={"email":"alice@example.com","password":"Senha123"})  # sem Authorization
    assert r.status_code == 200 and client.post("/auth/login", json={"email":"alice@example.com","password":"Senha123"}).status_code == 401
def test_S05_delete_sem_rate_limit_e_oraculo_de_enumeracao_VULN(client, user_a):
    assert client.request("DELETE","/auth/delete",json={"email":"naoexiste@x.com","password":"x"}).status_code == 404   # revela inexistência
    assert client.request("DELETE","/auth/delete",json={"email":"alice@example.com","password":"x"}).status_code == 401  # revela existência
def test_S06_enumeracao_via_signup_VULN(client, user_a):
    r = client.post("/auth/signup", json={"nome":"x","email":"alice@example.com","password":"Senha123","confirmPassword":"Senha123"})
    assert r.status_code == 400 and "cadastrado" in r.text
def test_S07_timing_login_usuario_existente_vs_inexistente_VULN(client, user_a):
    def t(email):
        xs=[]
        for _ in range(6):
            s=time.perf_counter(); client.post("/auth/login", json={"email":email,"password":"errada"}); xs.append(time.perf_counter()-s)
        return statistics.median(xs)
    ex, nex = t("alice@example.com"), t("ghost@example.com")
    print(f"\n[timing] existente={ex*1000:.1f}ms inexistente={nex*1000:.1f}ms razão={ex/nex:.1f}x")
    assert ex > 3*nex      # bcrypt só roda quando o e-mail existe
def test_S08_senha_fraca_aceita_pelo_backend_VULN(client):
    assert client.post("/auth/signup", json={"nome":"x","email":"w@x.com","password":"1","confirmPassword":"1"}).status_code == 201
def test_S09_bcrypt_72_bytes_login_com_senha_diferente_VULN(client):
    base="A1"+"x"*70
    client.post("/auth/signup", json={"nome":"x","email":"l@x.com","password":base+"AAAA","confirmPassword":base+"AAAA"})
    assert client.post("/auth/login", json={"email":"l@x.com","password":base+"ZZZZ"}).status_code == 200
def test_S10_sql_injection_login_email_OK(client, user_a):
    for p in ["' OR '1'='1", "alice@example.com' --", "x@x.com'; DROP TABLE usuarios;--"]:
        assert client.post("/auth/login", json={"email":p,"password":"x"}).status_code == 422
    assert client.post("/auth/login", json={"email":"alice@example.com","password":"' OR '1'='1"}).status_code == 401
def test_S11_sql_injection_delete_raw_sql_parametrizado_OK(client, user_a):
    r = client.request("DELETE","/auth/delete",json={"email":"a@b.com","password":"' OR 1=1 --"}); assert r.status_code == 404
    assert client.post("/auth/login", json={"email":"alice@example.com","password":"Senha123"}).status_code == 200  # tabela intacta
def test_S12_sqli_em_query_params_ORM_OK(client, user_a):
    r = client.get("/ia/historico?tipo=' OR 1=1 --", headers=user_a["h"]); assert r.status_code == 200 and r.json() == []
def test_S13_forgot_password_sem_enumeracao_OK(client, user_a):
    a = client.post("/auth/forgot-password?email=alice@example.com"); b = client.post("/auth/forgot-password?email=ghost@x.com")
    assert a.json() == b.json()
def test_S14_oauth_callback_reflete_code_sem_state_VULN(client):
    r = client.get("/auth/callback/facebook?code=<script>alert(1)</script>")
    assert r.status_code == 200 and "<script>alert(1)</script>" in r.text and r.headers["content-type"].startswith("application/json")
def test_S15_sub_nao_numerico_com_assinatura_valida_gera_500_VULN(client):
    forged = jwt.encode({"sub":"abc","exp":time.time()+60}, "dev-secret-key-change-in-production", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization":f"Bearer {forged}"}).status_code == 500

# ---------------- CORS / exposição
def test_S16_cors_aceita_qualquer_github_dev_com_credenciais_VULN(client):
    r = client.options("/auth/me", headers={"Origin":"https://atacante-123.github.dev","Access-Control-Request-Method":"GET","Access-Control-Request-Headers":"authorization"})
    assert r.headers.get("access-control-allow-origin") == "https://atacante-123.github.dev" and r.headers.get("access-control-allow-credentials") == "true"
def test_S17_cors_origem_externa_bloqueada_OK(client):
    r = client.options("/auth/me", headers={"Origin":"https://evil.com","Access-Control-Request-Method":"GET"}); assert "access-control-allow-origin" not in r.headers
def test_S18_docs_e_health_publicos_VULN(client):
    assert client.get("/docs").status_code == 200 and client.get("/openapi.json").status_code == 200
    h = client.get("/health").json(); assert "ambiente" in h and "mock_meta_api" in h and "ia_configurada" in h
def test_S19_sem_headers_de_seguranca_VULN(client):
    r = client.get("/"); missing=[h for h in ["x-content-type-options","x-frame-options","strict-transport-security","content-security-policy","referrer-policy"] if h not in r.headers]
    print("\n[headers ausentes]", missing); assert len(missing) == 5
def test_S20_erro_interno_nao_vaza_stacktrace_OK(client, user_a):
    r = client.get("/projetos", headers=user_a["h"]); assert r.status_code == 500 and "Traceback" not in r.text and "AttributeError" not in r.text

# ---------------- Entrada / abuso (IA)
def test_S21_ia_sem_limite_de_tamanho_custo_VULN(client, user_a):
    r = client.post("/ia/legenda", json={"tema":"x"*1_000_000}, headers=user_a["h"]); assert r.status_code == 200   # 1 MB de prompt aceito (custo OpenAI / DB)
def test_S22_ia_plataforma_null_500_VULN(client, user_a):
    assert client.post("/ia/legenda", json={"tema":"x","plataforma":None}, headers=user_a["h"]).status_code == 500
def test_S23_ia_quantidade_negativa_500_VULN(client, user_a):
    assert client.post("/ia/ideias", json={"segmento":"x","quantidade":-1}, headers=user_a["h"]).status_code == 500
def test_S24_paginacao_sem_teto_VULN(client, user_a):
    assert client.get("/ia/historico?per_page=100000000", headers=user_a["h"]).status_code == 200
def test_S25_prompt_injection_sem_sanitizacao_VULN():
    import inspect, app.services.ia_service as s
    src = inspect.getsource(s.gerar_legenda); assert "f\"Crie uma legenda {tom} para uma postagem no {plataforma} \"" in src and "sanit" not in src.lower()

# ---------------- Upload / arquivos estáticos (probe com alias_pk: simula correção do bug de mapeamento)
def _mk_post(client, h):
    r = client.post("/posts", json={"conteudo":"c"}, headers=h); assert r.status_code == 201, r.text; return r.json()["id"]
def test_S26_upload_aceita_html_e_serve_publico_XSS_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    payload = b"<html><script>document.title='XSS-'+document.domain</script></html>"
    r = client.post(f"/posts/{pid}/midia", files={"file":("evil.html", payload, "text/html")}, headers=user_a["h"]); assert r.status_code == 200, r.text
    url = r.json()["url"]
    g = client.get(url)                                # SEM autenticação
    assert g.status_code == 200 and g.headers["content-type"].startswith("text/html") and g.content == payload
def test_S27_upload_aceita_svg_php_exe_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    for name, ct in [("x.svg","image/svg+xml"),("shell.php","application/x-php"),("a.exe","application/octet-stream")]:
        assert client.post(f"/posts/{pid}/midia", files={"file":(name,b"AAAA",ct)}, headers=user_a["h"]).status_code == 200
def test_S28_upload_sem_limite_de_tamanho_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    r = client.post(f"/posts/{pid}/midia", files={"file":("big.png", b"0"*(30*1024*1024), "image/png")}, headers=user_a["h"]); assert r.status_code == 200  # 30 MB aceitos
def test_S29_upload_path_traversal_OK(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    r = client.post(f"/posts/{pid}/midia", files={"file":("../../../../tmp/pwn.py", b"x", "text/plain")}, headers=user_a["h"]); assert r.status_code == 200
    assert r.json()["url"].startswith("/uploads/") and ".." not in r.json()["url"] and not pathlib.Path("/tmp/pwn.py").exists()
def test_S30_upload_arquivos_publicos_sem_auth_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    url = client.post(f"/posts/{pid}/midia", files={"file":("privado.png", b"\x89PNG-privado", "image/png")}, headers=user_a["h"]).json()["url"]
    assert client.get(url).status_code == 200      # qualquer pessoa com o link

# ---------------- Autorização / IDOR / lógica (probe com alias_pk)
def test_S31_isolamento_postagens_entre_usuarios_OK(client, user_a, user_b, alias_pk):
    pid = _mk_post(client, user_a["h"])
    assert client.get(f"/posts/{pid}", headers=user_b["h"]).status_code == 404
    assert client.put(f"/posts/{pid}", json={"conteudo":"hack"}, headers=user_b["h"]).status_code == 404
    assert client.delete(f"/posts/{pid}", headers=user_b["h"]).status_code == 404
def test_S32_isolamento_canais_OK(client, user_a, user_b, alias_pk):
    r = client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"SEGREDO"}, headers=user_a["h"]); assert r.status_code == 201, r.text
    cid = r.json()["id"]
    assert client.delete(f"/channels/{cid}", headers=user_b["h"]).status_code == 404
    assert client.get("/channels", headers=user_b["h"]).json() == []
def test_S33_token_oauth_armazenado_em_texto_claro_VULN(client, user_a, alias_pk):
    client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"EAAB-TOKEN-SECRETO"}, headers=user_a["h"])
    from app.database.connection import SessionLocal; from app.models.models import ContaSocial
    db = SessionLocal(); v = db.query(ContaSocial).first().access_token; db.close(); assert v == "EAAB-TOKEN-SECRETO"
def test_S34_usuario_cria_plataformas_globais_arbitrarias_VULN(client, user_a, user_b, alias_pk):
    client.post("/channels/conectar", json={"plataforma_slug":"<img src=x onerror=alert(1)>","access_token":"t"}, headers=user_a["h"])
    nomes = [p["nome"] for p in client.get("/channels/plataformas").json()]      # endpoint público, sem auth
    assert any("<img" in n for n in nomes)
def test_S35_postagem_pode_apontar_para_projeto_de_outro_usuario_VULN(client, user_a, user_b, alias_pk):
    from app.database.connection import SessionLocal; from app.models.models import Projeto
    db = SessionLocal(); pr = Projeto(usuario_id=user_a["id"], nome_do_projeto="Privado A"); db.add(pr); db.commit(); pj = pr.id_projeto; db.close()
    r = client.post("/posts", json={"conteudo":"c","projeto_id":pj}, headers=user_b["h"]); assert r.status_code == 201   # sem checar dono do projeto
def test_S36_status_arbitrario_em_postagem_e_agendamento_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    r = client.put(f"/posts/{pid}", json={"status":"publicado"}, headers=user_a["h"]); assert r.status_code == 200 and r.json()["status"] == "publicado"  # sem publicar nada
def test_S37_agendamento_no_passado_aceito_VULN(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    cid = client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"t"}, headers=user_a["h"]).json()["id"]
    r = client.post("/agendamentos", json={"postagem_id":pid,"conta_social_id":cid,"data_agendada":"1999-01-01T00:00:00Z"}, headers=user_a["h"]); assert r.status_code == 201, r.text
def test_S38_isolamento_agendamento_publicar_OK(client, user_a, user_b, alias_pk):
    pid = _mk_post(client, user_a["h"])
    cid = client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"t"}, headers=user_a["h"]).json()["id"]
    ag = client.post("/agendamentos", json={"postagem_id":pid,"conta_social_id":cid,"data_agendada":"2030-01-01T00:00:00Z"}, headers=user_a["h"]).json()["id"]
    assert client.post("/meta/publicar", json={"agendamento_id":ag}, headers=user_b["h"]).status_code == 404
def test_S39_modo_mock_marca_publicado_sem_publicar_RISCO(client, user_a, alias_pk):
    pid = _mk_post(client, user_a["h"])
    cid = client.post("/channels/conectar", json={"plataforma_slug":"facebook","access_token":"t"}, headers=user_a["h"]).json()["id"]
    ag = client.post("/agendamentos", json={"postagem_id":pid,"conta_social_id":cid,"data_agendada":"2030-01-01T00:00:00Z"}, headers=user_a["h"]).json()["id"]
    r = client.post("/meta/publicar", json={"agendamento_id":ag}, headers=user_a["h"]); j = r.json()
    assert j["success"] is True and j["mock"] is True and j["post_id_externo"].startswith("mock_")
def test_S40_isolamento_ia_historico_OK(client, user_a, user_b):
    client.post("/ia/legenda", json={"tema":"segredo-da-alice"}, headers=user_a["h"])
    assert client.get("/ia/historico", headers=user_b["h"]).json() == []
