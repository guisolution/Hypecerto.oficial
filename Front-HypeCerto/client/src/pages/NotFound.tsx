import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { AlertCircle } from "lucide-react";

export default function NotFound() {
  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="text-center">
        <AlertCircle className="w-16 h-16 text-purple-400 mx-auto mb-4" />
        <h1 className="text-4xl font-bold text-white mb-2 font-display">404</h1>
        <p className="text-gray-300 mb-8">Página não encontrada</p>
        <Button
          onClick={() => setLocation("/login")}
          className="bg-purple-600 text-white hover:bg-purple-700"
        >
          Voltar ao Login
        </Button>
      </div>
    </div>
  );
}
