import { useLocation } from "wouter";

export default function Landing() {
  const [, setLocation] = useLocation();

  return (
    <div className="relative min-h-screen w-full text-white flex flex-col justify-between font-poppins overflow-hidden bg-[#090014]">
      
      {/* Imagem de Fundo em alta qualidade */}
      <img 
        src="/Background_Landingpage.png" 
        alt="Background Landing Page" 
        className="absolute inset-0 w-full h-full object-cover z-0 pointer-events-none"
      />

      {/* Conteúdo Principal (Texto, Título Ajustado e Botões) */}
      <main className="relative z-10 flex-1 flex flex-col justify-center px-6 md:px-20 py-12 max-w-[680px] my-auto">
        
        {/* Título ajustado para ocupar apenas duas linhas */}
        <h1 className="text-[1.9rem] md:text-[2.3rem] font-bold mb-5 leading-[1.2] text-white drop-shadow-lg tracking-tight">
          Automação de Redes Sociais com Inteligência
        </h1>
        
        <p className="text-[#d3d3d3] text-[0.95rem] md:text-[1.05rem] leading-[1.7] mb-5 drop-shadow-md">
          A <strong className="text-white font-bold">HypeCerto</strong> é uma plataforma de automação de redes sociais acessível e inteligente, criada especialmente para o mercado brasileiro. Nosso foco é ajudar pequenas e médias empresas, criadores de conteúdo e empreendedores a fortalecerem sua presença digital com facilidade.
        </p>
        
        <p className="text-[#d3d3d3] text-[0.95rem] md:text-[1.05rem] leading-[1.7] mb-6 drop-shadow-md">
          Simplifique sua gestão de redes, aumente seu alcance e deixe a automação trabalhar por você.
        </p>

        {/* Botões Reais e Clicáveis */}
        <div className="flex flex-row gap-5 mt-2">
          <button 
            onClick={() => setLocation("/login")}
            className="px-[35px] py-[12px] rounded-[30px] font-semibold text-[1rem] transition-all duration-300 bg-transparent border-2 border-[#bb86fc] text-[#bb86fc] hover:bg-[#bb86fc] hover:text-white hover:scale-105 cursor-pointer shadow-lg"
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

      </main>

      {/* Rodapé */}
      <footer className="relative z-10 text-center text-[#888] text-[0.9rem] py-5 font-poppins">
        © 2025 HypeCerto — Todos os direitos reservados
      </footer>

    </div>
  );
}