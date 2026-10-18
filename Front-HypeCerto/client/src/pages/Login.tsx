import { API_URL } from "@/lib/api";
import { useLocation, Link } from "wouter";
import { useState } from "react";

export default function Login() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        setLocation("/dashboard");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "E-mail ou senha incorretos.");
      }
    } catch (err) {
      console.error("Erro na requisição:", err);
      setError("Não foi possível conectar ao servidor. Verifique se o back-end está rodando.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <style dangerouslySetInnerHTML={{ __html: styles }} />
      
      {/* Lado Esquerdo - Formulário Real de Login */}
      <div className="form-side">
        <div className="mark">
          <img 
            src="/logo.png" 
            alt="Logo HypeCerto" 
            style={{ width: '45px', height: '45px', objectFit: 'contain', borderRadius: '10px' }}
          />
          <span className="name">Hype<em>Certo</em></span>
        </div>

        <span className="eyebrow">ACESSO À CONTA</span>
        <h1 style={{ marginBottom: '8px' }}>Bem-Vindo</h1>
        <h2 style={{ color: 'var(--violet)', fontSize: '28px', fontWeight: '700' }}>
          Muito bom ter você aqui.
        </h2>
        <p className="sub">Use seu e-mail e senha para acessar sua conta.</p>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="error-banner">
              {error}
            </div>
          )}

          <div className="field">
            <label htmlFor="email">E-mail</label>
            <input 
              id="email" 
              type="email" 
              placeholder="seunome@email.com" 
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="senha">Senha</label>
            <input 
              id="senha" 
              type="password" 
              placeholder="••••••••" 
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <button className="submit" type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
            {!loading && (
              <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M13 6l6 6-6 6"/>
              </svg>
            )}
          </button>
        </form>

        <div className="links">
          <span>Ainda não tem conta? <Link href="/signup">Cadastre-se</Link></span>
          <Link href="/forgot-password">Esqueceu a senha?</Link>
        </div>

        <p className="note">Acesso restrito à sua conta HypeCerto.</p>
      </div>

      {/* Lado Direito - Imagem ajustada com object-[75%_center] para trazer as pessoas mais para a esquerda */}
      <div className="visual">
        <img 
          src="/LoginBackGround.png" 
          alt="HypeCerto Login Visual" 
          className="w-full h-full object-cover object-[100%_center]"
        />
      </div>
    </div>
  );
}

const styles = `
  .login-container {
    --paper: #fbfaff;
    --paper-2: #f4f2fa;
    --black: #09070e;
    --violet-deep: #2c1354;
    --violet: #7c3aed;
    --violet-2: #a78bfa;
    --violet-soft: #6d28d9;
    --ink: #1a1425;
    --muted: #726a85;
    --line: rgba(26,20,37,0.13);
    
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background-color: var(--paper);
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
  }

  .login-container * {
    box-sizing: inherit;
    margin: 0;
    padding: 0;
  }

  .form-side {
    width: 42%;
    min-width: 420px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 56px;
    background-color: var(--paper);
    position: relative;
    z-index: 1;
    overflow-y: auto;
  }

  .mark {
    display: flex; 
    align-items: center; 
    gap: 12px;
    margin-bottom: 30px;
  }

  .mark span.name { 
    font-family: 'Sora', sans-serif; 
    font-weight: 700; 
    font-size: 22px; 
    color: var(--ink); 
  }
  
  .mark span.name em { 
    font-style: normal; 
    color: var(--violet); 
  }

  .eyebrow {
    display: inline-flex;
    width: fit-content;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--violet-soft);
    background: rgba(124,58,237,0.12);
    padding: 7px 14px;
    border-radius: 999px;
    margin-bottom: 15px;
  }

  .form-side h1 {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: clamp(28px, 3.2vw, 36px);
    line-height: 1.22;
    color: var(--ink);
  }

  .sub { 
    margin-top: 10px; 
    font-size: 14.5px; 
    color: var(--muted); 
    max-width: 36ch; 
    line-height: 1.55; 
  }

  .form-side form { 
    margin-top: 24px; 
    display: flex; 
    flex-direction: column; 
    gap: 16px; 
  }

  .error-banner {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #ef4444;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 13px;
    text-align: center;
    font-weight: 500;
  }
  
  .field { display: flex; flex-direction: column; gap: 7px; }
  .field label { font-size: 13px; font-weight: 500; color: var(--ink); }
  .field input {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 14.5px;
    color: var(--ink);
    outline: none;
    transition: border-color .15s ease, box-shadow .15s ease;
  }
  .field input:disabled {
    background: #f9f9f9;
    color: #6b6480;
    cursor: not-allowed;
  }
  .field input::placeholder { color: #6b6480; }
  .field input:focus:not(:disabled) {
    border-color: var(--violet);
    box-shadow: 0 0 0 3px rgba(124,58,237,0.18);
  }

  .submit {
    margin-top: 6px;
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 8px;
    padding: 14px;
    border: none;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--violet), #5b21b6);
    color: #fff;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 14.5px;
    cursor: pointer;
    transition: transform .15s ease, filter .15s ease;
    box-shadow: 0 16px 32px -14px rgba(124,58,237,0.55);
  }
  
  .submit svg { width: 15px; height: 15px; }
  .submit:hover:not(:disabled) { filter: brightness(1.08); transform: translateY(-1px); }
  .submit:focus-visible { outline: 2px solid var(--violet-soft); outline-offset: 3px; }
  .submit:disabled {
    background: #a78bfa;
    cursor: not-allowed;
    box-shadow: none;
  }

  .note { 
    margin-top: 16px; 
    font-size: 12.5px; 
    color: #6b6480; 
    text-align: center; 
  }

  .links {
    margin-top: 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: var(--muted);
    text-align: center;
  }
  .links a { color: #6d28d9; text-decoration: underline; cursor: pointer; }
  .links a:hover { text-decoration: underline; }

  .visual {
    flex: 1;
    height: 100%;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #09070e;
  }

  @media (max-width: 820px) {
    .login-container { flex-direction: column; overflow: auto; height: auto; min-height: 100vh; }
    .form-side { width: 100%; min-width: 0; padding: 48px 28px; }
    .visual { height: 350px; width: 100%; }
  }

  @media (prefers-reduced-motion: reduce) {
    .submit { transition: none; }
  }
`;