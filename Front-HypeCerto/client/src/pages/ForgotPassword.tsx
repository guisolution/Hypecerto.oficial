import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useLocation } from "wouter";
import { CheckCircle, ArrowLeft } from "lucide-react";

/**
 * Design: Modern Tech Dashboard
 * - Fundo preto/cinza escuro
 * - Formulário centralizado com borda sutil
 * - Botões roxo (enviar) e branco (voltar)
 */
export default function ForgotPassword() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    // Simular envio
    setTimeout(() => {
      setLocation("/login");
    }, 3000);
  };

  const handleBack = () => {
    setLocation("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Elementos decorativos */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <div className="bg-purple-600 p-4 rounded-2xl">
              <CheckCircle className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 font-display">HypeCerto</h1>
          <p className="text-gray-400 text-sm">Social Media Automation</p>
        </div>

        {!submitted ? (
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-2 font-display">Esqueci minha senha</h2>
            <p className="text-gray-400 text-sm mb-8">
              Digite o e-mail cadastrado e enviaremos um link para você redefinir sua senha.
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Campo Email */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                <Input
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-slate-700 border-slate-600 text-white placeholder-gray-500 focus:border-purple-500 focus:ring-purple-500"
                  required
                />
              </div>

              {/* Botões */}
              <div className="flex gap-4 pt-4">
                <Button
                  type="submit"
                  className="flex-1 bg-purple-600 text-white font-semibold hover:bg-purple-700 transition-all duration-200 py-6 rounded-xl"
                >
                  ENVIAR
                </Button>
                <Button
                  type="button"
                  onClick={handleBack}
                  className="flex-1 bg-white text-slate-900 font-semibold hover:bg-gray-100 transition-all duration-200 py-6 rounded-xl"
                >
                  VOLTAR
                </Button>
              </div>
            </form>
          </div>
        ) : (
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-green-600 p-4 rounded-full">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2 font-display">Email enviado!</h2>
            <p className="text-gray-400 text-sm mb-6">
              Verifique sua caixa de entrada para o link de redefinição de senha.
            </p>
            <p className="text-gray-500 text-xs">Redirecionando em breve...</p>
          </div>
        )}
      </div>
    </div>
  );
}
