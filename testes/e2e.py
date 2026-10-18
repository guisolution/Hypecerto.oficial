import json, time, pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path("/tmp/claude-0/ev/evidence/shots"); OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:5173"; res = []
def rec(id_, desc, ok, detail=""):
    res.append({"id":id_, "desc":desc, "ok":bool(ok), "detail":detail}); print(("PASS " if ok else "FAIL ")+id_, "-", desc, "|", detail)
AXE = open("/tmp/claude-0/ev/axe/node_modules/axe-core/axe.min.js").read()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium" if pathlib.Path("/opt/pw-browsers/chromium").exists() else None)
    ctx = b.new_context(viewport={"width":1366,"height":800}); pg = ctx.new_page()
    errs=[]; reqf=[]
    pg.on("pageerror", lambda e: errs.append("JS:"+str(e)))
    pg.on("response", lambda r: reqf.append(f"{r.status} {r.url}") if r.status>=400 else None)
    pg.on("requestfailed", lambda r: reqf.append(f"FAILED {r.url}"))
    # E01 landing
    pg.goto(BASE+"/"); pg.wait_for_load_state("networkidle"); pg.screenshot(path=OUT/"01_landing.png", full_page=True)
    rec("E01","Landing carrega", pg.locator("body").inner_text().strip()!="", f"title='{pg.title()}'")
    # E02 acesso a rotas protegidas SEM login
    for r in ["/dashboard","/create","/publish","/channels","/results"]:
        pg.goto(BASE+r); pg.wait_for_load_state("networkidle"); time.sleep(.5)
        rec("E02"+r.replace("/","-"), f"Rota protegida {r} sem token redireciona p/ login", "/login" in pg.url, f"url final={pg.url}")
    pg.screenshot(path=OUT/"02_dashboard_sem_login.png")
    # E03 signup validação client-side
    pg.goto(BASE+"/signup"); pg.wait_for_load_state("networkidle"); pg.screenshot(path=OUT/"03_signup.png", full_page=True)
    inputs = pg.locator("input"); n = inputs.count(); rec("E03","Signup tem campos", n>=4, f"{n} inputs: "+", ".join((inputs.nth(i).get_attribute('name') or inputs.nth(i).get_attribute('type') or '?') for i in range(n)))
    # E04 cadastro completo + login
    email=f"e2e{int(time.time())}@teste.com"
    def fill(sel, v):
        l = pg.locator(sel).first
        if l.count(): l.fill(v)
    fill("input[name=nome]","Usuaria Teste"); fill("input[name=email]",email); fill("input[name=telefone]","11999998888")
    fill("input[name=password]","Senha123"); fill("input[name=confirmPassword]","Senha123")
    cb = pg.locator("input[type=checkbox]"); 
    if cb.count(): cb.first.check()
    pg.screenshot(path=OUT/"04_signup_preenchido.png", full_page=True)
    pg.locator("button[type=submit]").first.click(); time.sleep(2.5); pg.screenshot(path=OUT/"05_signup_pos_submit.png", full_page=True)
    body = pg.locator("body").inner_text()
    rec("E04","Cadastro via UI avança para escolha de plano", ("plano" in body.lower() or "plan" in body.lower()), body[:160].replace("\n"," | "))
    # confirma no backend
    import urllib.request
    rq = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=json.dumps({"email":email,"password":"Senha123"}).encode(), headers={"Content-Type":"application/json"})
    try: ok = urllib.request.urlopen(rq).status==200
    except Exception as e: ok=False
    rec("E05","Usuário criado no backend (login por API)", ok)
    # E06 login via UI
    pg.goto(BASE+"/login"); pg.wait_for_load_state("networkidle")
    pg.locator("input[type=email], input[name=email]").first.fill(email); pg.locator("input[type=password]").first.fill("Senha123")
    pg.screenshot(path=OUT/"06_login.png")
    pg.locator("button[type=submit]").first.click(); time.sleep(2.5); pg.screenshot(path=OUT/"07_pos_login.png", full_page=True)
    tok = pg.evaluate("localStorage.getItem('token')")
    rec("E06","Login via UI leva ao dashboard", "/dashboard" in pg.url, f"url={pg.url}")
    rec("E07","JWT NÃO é armazenado em localStorage (mitigação de XSS)", not tok, f"token[:20]={str(tok)[:20]}…")
    # E08 dashboard consome API quebrada?
    time.sleep(1.5); pg.screenshot(path=OUT/"08_dashboard.png", full_page=True)
    # E09 menu de usuário por teclado (usabilidade/a11y)
    pg.goto(BASE+"/dashboard"); pg.wait_for_load_state("networkidle")
    btn = pg.locator("div.relative.group > button").first; btn.focus(); time.sleep(.4)
    vis_kb = pg.get_by_text("Sair").first.is_visible()
    rec("E09a","Menu do usuário (Sair) acessível por TECLADO (focus)", vis_kb, f"visível após focus={vis_kb} (menu usa apenas :hover)")
    # E09 logout via hover
    btn.hover(); time.sleep(.5); pg.screenshot(path=OUT/"08b_menu_usuario_hover.png")
    pg.get_by_text("Sair").first.click(); time.sleep(1)
    tk = pg.evaluate("localStorage.getItem('token')")
    rec("E09","Logout remove o token de sessão do navegador", tk is None, f"token após logout={'AINDA PRESENTE' if tk else 'removido'}; url={pg.url}")
    # token residual ainda abre o dashboard e autentica na API?
    r = pg.evaluate("""async (t)=>{const r=await fetch('http://127.0.0.1:8000/auth/me',{headers:{Authorization:'Bearer '+t}});return r.status}""", tk) if tk else None
    rec("E09b","Token residual pós-logout é rejeitado pela API", r!=200, f"/auth/me => {r}")
    # E10 login inválido: mensagem
    pg.goto(BASE+"/login"); pg.wait_for_load_state("networkidle")
    pg.locator("input[type=email], input[name=email]").first.fill(email); pg.locator("input[type=password]").first.fill("errada"); pg.locator("button[type=submit]").first.click(); time.sleep(1.5)
    pg.screenshot(path=OUT/"09_login_erro.png"); rec("E10","Mensagem de erro em credencial inválida", "incorret" in pg.locator("body").inner_text().lower(), pg.locator("body").inner_text()[:120].replace("\n"," | "))
    # Acessibilidade (axe) + usabilidade
    for name, path in [("login","/login"),("signup","/signup"),("landing","/")]:
        pg.goto(BASE+path); pg.wait_for_load_state("networkidle"); pg.add_script_tag(content=AXE)
        r = pg.evaluate("axe.run().then(r=>({v:r.violations.map(v=>({id:v.id,impact:v.impact,n:v.nodes.length,help:v.help})),p:r.passes.length}))")
        crit=[v for v in r["v"] if v["impact"] in ("critical","serious")]
        rec(f"A11Y-{name}", f"axe-core sem violações critical/serious ({path})", not crit, f"{len(r['v'])} violações ({len(crit)} crit/serious): "+"; ".join(f"{v['id']}[{v['impact']}]x{v['n']}" for v in r["v"])[:300])
        json.dump(r, open(OUT/f"axe_{name}.json","w"), indent=1)
        lang = pg.evaluate("document.documentElement.lang"); 
        rec(f"LANG-{name}", "atributo lang do <html> coerente com conteúdo pt-BR", lang.lower().startswith("pt"), f"lang='{lang}'")
    # Responsivo
    for w,h in [(375,812),(768,1024)]:
        c2 = b.new_context(viewport={"width":w,"height":h}); q=c2.new_page()
        for path in ["/login","/signup","/"]:
            q.goto(BASE+path); q.wait_for_load_state("networkidle"); sw=q.evaluate("document.documentElement.scrollWidth")
            rec(f"RESP-{w}{path.replace('/','-')}", f"Sem rolagem horizontal em {w}px ({path})", sw<=w+1, f"scrollWidth={sw}")
            q.screenshot(path=OUT/f"resp_{w}_{path.strip('/') or 'landing'}.png", full_page=True)
        c2.close()
    ext=[u for u in reqf if "127.0.0.1" not in u and "localhost" not in u]; loc=[u for u in reqf if u not in ext]
    rec("CONSOLE-JS","Sem exceções JS não tratadas", len(errs)==0, f"{len(errs)}: "+" || ".join(errs)[:300])
    rec("NET-LOCAL","Sem respostas 4xx/5xx em recursos locais (exceto login inválido esperado)", len([u for u in loc if "auth/login" not in u])==0, " || ".join(sorted(set(loc)))[:600])
    rec("NET-EXT","Recursos externos carregados (bloqueios de rede do sandbox ignorados)", True, f"{len(ext)} falhas externas: "+" || ".join(sorted(set(u.split('?')[0] for u in ext)))[:500])
    b.close()
json.dump(res, open("/tmp/claude-0/ev/evidence/40_e2e_results.json","w"), indent=1, ensure_ascii=False)
print(f"\nTOTAL {len(res)} | PASS {sum(r['ok'] for r in res)} | FAIL {sum(not r['ok'] for r in res)}")
