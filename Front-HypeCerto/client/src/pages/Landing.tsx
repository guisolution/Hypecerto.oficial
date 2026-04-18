import { useLocation } from "wouter";

export default function Landing() {
  // Hook do wouter para fazer a navegação dos botões funcionar
  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#090014] to-[#2b0040] text-white flex flex-col font-poppins">
      
      <main className="flex-1 flex flex-col-reverse md:flex-row items-center justify-center px-5 py-10 md:px-20 md:py-[60px] gap-10 md:gap-[80px]">
        
        {/* Lado Esquerdo - Textos e Botões */}
        <div className="flex-1 max-w-[600px] text-center md:text-left">
          <h1 className="text-[2.2rem] md:text-[2.8rem] font-bold mb-5 leading-tight text-white">
            Automação de Redes Sociais com Inteligência
          </h1>
          
          <p className="text-[#d3d3d3] text-[1rem] md:text-[1.1rem] leading-[1.8] mb-6">
            A <strong className="text-white font-bold">HypeCerto</strong> é uma plataforma de automação de redes sociais acessível e inteligente, criada especialmente para o mercado brasileiro. Nosso foco é ajudar pequenas e médias empresas, criadores de conteúdo e empreendedores a fortalecerem sua presença digital com facilidade.
          </p>
          
          <p className="text-[#d3d3d3] text-[1rem] md:text-[1.1rem] leading-[1.8] mb-6">
            Simplifique sua gestão de redes, aumente seu alcance e deixe a automação trabalhar por você.
          </p>

          <div className="flex flex-row justify-center md:justify-start gap-5 mt-5">
            <button 
              onClick={() => setLocation("/login")}
              className="px-[35px] py-[12px] rounded-[30px] font-semibold text-[1rem] transition-all duration-300 bg-transparent border-2 border-[#bb86fc] text-[#bb86fc] hover:bg-[#bb86fc] hover:text-white hover:scale-105 cursor-pointer"
            >
              Entrar
            </button>
            <button 
              onClick={() => setLocation("/signup")}
              className="px-[35px] py-[12px] rounded-[30px] font-semibold text-[1rem] transition-all duration-300 bg-gradient-to-r from-[#bb86fc] to-[#7b2ff7] text-white border-none hover:scale-105 hover:shadow-[0_0_15px_#7b2ff7] cursor-pointer"
            >
              Cadastrar
            </button>
          </div>
        </div>

        {/* Lado Direito - Imagem */}
        <div className="flex-1 flex items-center justify-center">
          <img 
            src="/logo1.png" 
            alt="Logo HypeCerto" 
            className="w-4/5 max-w-[200px] md:max-w-[400px] drop-shadow-[0_0_10px_rgba(187,134,252,0.4)]"
          />
        </div>

      </main>

      {/* Rodapé */}
      <footer className="text-center text-[#888] text-[0.9rem] py-5 font-poppins">
        © 2025 HypeCerto — Todos os direitos reservados
      </footer>

    </div>
  );
}