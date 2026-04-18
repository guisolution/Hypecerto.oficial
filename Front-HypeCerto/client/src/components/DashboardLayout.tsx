import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Plus, LogOut, Settings, User, Link2, HelpCircle } from "lucide-react";
import React from "react";

/**
 * Design: Modern Tech Dashboard - Navbar Limpa
 * - Ícone de ajuda (?) posicionado ao lado do perfil
 * - Removido ícone de grade desnecessário
 */

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeTab?: "publications" | "results" | "create" | "publish" | "channels";
}

export default function DashboardLayout({
  children,
  activeTab = "publications",
}: DashboardLayoutProps) {
  const [, setLocation] = useLocation();

  const navItems = [
    { id: "publications", label: "Publicações", route: "/dashboard" },
    { id: "results", label: "Resultados", route: "/results" },
    { id: "create", label: "Criar", route: "/create" },
    { id: "publish", label: "Publicar", route: "/publish" },
  ];

  const handleLogout = () => {
    localStorage.removeItem("user");
    setLocation("/login");
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar Superior */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center justify-between">
          
          {/* Esquerda: Logo e Itens de Navegação */}
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setLocation("/dashboard")}>
              <img 
                src="/logo.png" 
                alt="Logo HypeCerto" 
                className="w-10 h-10 object-contain" 
              />
              <span className="font-bold text-gray-900 hidden sm:inline">HypeCerto</span>
            </div>

            <div className="hidden md:flex gap-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setLocation(item.route)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 text-sm ${
                    activeTab === item.id
                      ? "bg-purple-100 text-purple-600"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Direita: Botão Novo, Ajuda e Perfil */}
          <div className="flex items-center gap-2 md:gap-4">
            <Button
              onClick={() => setLocation("/create")}
              className="bg-purple-600 text-white hover:bg-purple-700 gap-2 hidden sm:flex mr-2"
            >
              <Plus className="w-4 h-4" />
              Novo
            </Button>

            {/* Ícone de Ajuda (?) - Agora posicionado ao lado do perfil */}
            <button 
              onClick={() => setLocation("/guide")}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 group"
              title="Como usar o HypeCerto"
            >
              <HelpCircle className="w-5.5 h-5.5 text-gray-400 group-hover:text-purple-600 transition-colors" />
            </button>

            {/* Menu do Usuário */}
            <div className="relative group">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 border border-transparent hover:border-gray-200">
                <User className="w-5.5 h-5.5 text-gray-600" />
              </button>
              
              {/* Opções do Menu Suspenso */}
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <button className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-700 rounded-t-lg font-medium">
                  Perfil
                </button>
                
                <button 
                  onClick={() => setLocation("/channels")}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-700"
                >
                  <Link2 className="w-4 h-4 inline mr-2 text-purple-600" />
                  Editar Redes
                </button>

                <button className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-700">
                  <Settings className="w-4 h-4 inline mr-2" />
                  Configurações
                </button>
                
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-red-600 rounded-b-lg border-t border-gray-200"
                >
                  <LogOut className="w-4 h-4 inline mr-2" />
                  Sair
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Conteúdo Principal */}
      <main className="p-6 md:p-8">
        {children}
      </main>
    </div>
  );
}