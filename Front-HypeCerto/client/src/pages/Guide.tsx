import { useLocation } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import {
  Link2,
  Image as ImageIcon,
  Send,
  Rocket,
  ArrowRight,
} from "lucide-react";
import React from "react";

/**
 * Design: Guia Limpo
 * - Removido contornos coloridos (grades)
 * - Removido pontos de interrogação não funcionais
 */
export default function Guide() {
  const [, setLocation] = useLocation();

  const steps = [
    {
      id: 1,
      title: "Conecte suas Redes",
      description: "Vincule as contas de redes sociais que você deseja automatizar.",
      icon: <Link2 className="w-6 h-6 text-purple-600" />,
      actionText: "Conectar Redes",
      actionRoute: "/channels",
    },
    {
      id: 2,
      title: "Crie sua Postagem",
      description: "Faça upload da imagem, escreva a legenda e adicione emojis.",
      icon: <ImageIcon className="w-6 h-6 text-purple-600" />,
      actionText: "Criar Post",
      actionRoute: "/create",
    },
    {
      id: 3,
      title: "Selecione os Canais",
      description: "Escolha Facebook, Instagram, LinkedIn com um clique.",
      icon: <Send className="w-6 h-6 text-purple-600" />,
      actionText: "Ir para Publicar",
      actionRoute: "/publish",
    },
    {
      id: 4,
      title: "Lance o Hype!",
      description: "Revise tudo e clique em Publicar! Acompanhe no Dashboard.",
      icon: <Rocket className="w-6 h-6 text-purple-600" />,
      actionText: "Ver Dashboard",
      actionRoute: "/dashboard",
    },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900 font-display">Guia de Início</h1>
        </div>

        {/* Banner Superior */}
        <div className="text-center space-y-4 bg-gradient-to-r from-purple-900 to-purple-600 rounded-3xl p-12 text-white shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full blur-3xl"></div>
          
          <div className="relative z-10 flex flex-col items-center">
            {/* Logo HypeCerto centralizada e sem borda */}
            <div className="w-24 h-24 bg-white rounded-3xl flex items-center justify-center mb-6 shadow-2xl p-4">
              <img 
                src="/logo.png" 
                alt="Logo HypeCerto" 
                className="w-full h-full object-contain"
              />
            </div>

            <h2 className="text-4xl font-bold font-display tracking-tight">Como gerar Hype em 4 passos</h2>
            <p className="text-purple-100 text-lg max-w-xl mx-auto mt-4">
              Siga o fluxo abaixo para dominar suas redes sociais com rapidez.
            </p>
          </div>
        </div>

        {/* Lista de Passos - Limpa e sem grades coloridas */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="flex flex-col md:flex-row gap-6 items-center">
              
              {/* Ícone Lateral Circular Suave */}
              <div className="w-14 h-14 rounded-full bg-purple-50 flex-shrink-0 flex items-center justify-center border border-purple-100">
                {step.icon}
              </div>

              {/* Card de Conteúdo - Apenas borda cinza padrão */}
              <div className="flex-1 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm hover:border-purple-200 transition-all duration-200 w-full">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-purple-400 uppercase tracking-[0.2em]">Passo {step.id}</span>
                    <h3 className="text-lg font-bold text-gray-900 font-display">{step.title}</h3>
                    <p className="text-gray-500 text-sm leading-relaxed">{step.description}</p>
                  </div>

                  <Button 
                    onClick={() => setLocation(step.actionRoute)}
                    variant={index === steps.length - 1 ? "default" : "outline"}
                    className={index === steps.length - 1 ? "bg-purple-600 text-white" : "border-gray-200 text-gray-700 hover:text-purple-700 hover:border-purple-200"}
                  >
                    {step.actionText}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </div>

            </div>
          ))}
        </div>

        {/* Rodapé Simples */}
        <div className="mt-12 text-center p-10 bg-gray-50 rounded-3xl border border-gray-100">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Pronto para começar?</h3>
          <p className="text-gray-500 text-sm mb-6 max-w-md mx-auto">Se precisar de qualquer ajuda durante o processo, nossa equipe está disponível no chat de suporte.</p>
          <Button className="bg-gray-900 text-white hover:bg-black rounded-xl px-8">
            Falar com Especialista
          </Button>
        </div>

      </div>
    </DashboardLayout>
  );
}