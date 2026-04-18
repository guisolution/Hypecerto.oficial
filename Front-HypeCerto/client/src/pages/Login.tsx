import { useLocation } from "wouter";
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
      // Conecta com o seu back-end FastAPI
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Salva o Token JWT real que vimos no Thunder Client
        localStorage.setItem("token", data.access_token);
        
        // Salva as informações do usuário (opcional, mas útil)
        localStorage.setItem("user", JSON.stringify(data.user));

        // Redireciona apenas se o login for bem-sucedido
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
    <div 
      className="min-h-screen flex justify-center items-center bg-cover bg-center"
      style={{ backgroundImage: "url('/fundo.png')" }}
    >
      <div className="w-full max-w-[1200px] h-full flex items-center justify-between px-10 max-lg:flex-col max-lg:justify-center max-lg:p-5">
        
        {/* Lado esquerdo */}
        <div className="flex-1 text-white flex flex-col justify-start items-center text-center pt-[50px] max-lg:hidden">
          <img 
            src="/logo1.png" 
            alt="Logo HypeCerto" 
            className="w-[280px] h-auto opacity-95 mb-5" 
          />
          <h1 className="text-[26px] mb-2.5 font-bold font-poppins">
            Bem-vindo de volta!
          </h1>
          <p className="text-[14px] text-[#ccc] font-poppins">
            Entre e continue gerenciando suas redes com automação e inteligência.
          </p>
        </div>

        {/* Lado direito (formulário de login) */}
        <div className="flex-1 flex justify-center items-center ml-[90px] max-lg:ml-0 max-lg:w-full max-lg:max-w-[400px]">
          <form 
            onSubmit={handleSubmit}
            className="bg-transparent shadow-[0_4px_10px_rgba(76,76,76,0.3)] p-10 rounded-lg w-[350px] text-white"
          >
            <h2 className="text-center mb-[25px] text-[#bb86fc] font-bold text-2xl font-poppins">
              Login
            </h2>

            {/* Mensagem de Erro Dinâmica */}
            {error && (
              <div className="mb-4 p-2 bg-red-500/20 border border-red-500 text-red-500 text-xs rounded text-center font-poppins">
                {error}
              </div>
            )}

            {/* Input E-mail */}
            <div className="relative mb-5">
              <input
                type="email"
                id="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="peer w-full p-3 border border-[#aaa] rounded-md bg-transparent text-white outline-none text-[14px] font-poppins focus:border-[#8c52ff] transition-colors"
              />
              <label
                htmlFor="email"
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#aaa] text-[14px] font-poppins pointer-events-none transition-all duration-300 peer-focus:top-[-10px] peer-focus:left-2 peer-focus:text-[12px] peer-focus:text-[#8c52ff] peer-focus:bg-[#2a2a2a] peer-focus:px-1 peer-focus:rounded peer-valid:top-[-10px] peer-valid:left-2 peer-valid:text-[12px] peer-valid:text-[#8c52ff] peer-valid:bg-[#2a2a2a] peer-valid:px-1 peer-valid:rounded"
              >
                E-mail
              </label>
            </div>

            {/* Input Senha */}
            <div className="relative mb-5">
              <input
                type="password"
                id="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="peer w-full p-3 border border-[#aaa] rounded-md bg-transparent text-white outline-none text-[14px] font-poppins focus:border-[#8c52ff] transition-colors"
              />
              <label
                htmlFor="password"
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#aaa] text-[14px] font-poppins pointer-events-none transition-all duration-300 peer-focus:top-[-10px] peer-focus:left-2 peer-focus:text-[12px] peer-focus:text-[#8c52ff] peer-focus:bg-[#2a2a2a] peer-focus:px-1 peer-focus:rounded peer-valid:top-[-10px] peer-valid:left-2 peer-valid:text-[12px] peer-valid:text-[#8c52ff] peer-valid:bg-[#2a2a2a] peer-valid:px-1 peer-valid:rounded"
              >
                Senha
              </label>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className={`w-full p-3.5 ${loading ? 'bg-gray-500' : 'bg-[#8c52ff] hover:bg-[#7329ff]'} border-none rounded-md text-[16px] font-bold text-white cursor-pointer transition-colors duration-300 mt-2.5 font-poppins`}
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>

            <div className="mt-5 text-center text-[13px] font-poppins">
              <p className="text-[#aaa] mb-2">
                Ainda não tem conta?{' '}
                <button 
                  type="button"
                  onClick={() => setLocation("/signup")} 
                  className="text-[#bb86fc] hover:underline transition-all bg-transparent border-none cursor-pointer"
                >
                  Cadastre-se
                </button>
              </p>
              <p>
                <button 
                  type="button"
                  onClick={() => setLocation("/forgot-password")}
                  className="text-[#bb86fc] hover:underline transition-all bg-transparent border-none cursor-pointer"
                >
                  Esqueceu a senha?
                </button>
              </p>
            </div>
          </form>
        </div>
        
      </div>
      
      {/* Footer */}
      <footer className="fixed bottom-2.5 w-full text-center text-[#aaa] text-[0.9rem] font-poppins">
        © 2025 HypeCerto
      </footer>
    </div>
  );
}