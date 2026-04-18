import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useLocation } from "wouter";
import { Eye, EyeOff, AlertCircle, CheckIcon } from "lucide-react";
import {
  validateEmail,
  validatePassword,
  validatePasswordMatch,
  validateSignupForm,
} from "@/lib/validators";

const PLANS = [
  {
    id: "free",
    name: "Teste Grátis",
    price: "Grátis",
    duration: "7 dias",
    features: ["Até 5 postagens", "1 canal", "Suporte por email"],
    color: "bg-gray-700",
  },
  {
    id: "pro",
    name: "Plano Pro",
    price: "R$ 99",
    duration: "por mês",
    features: ["Postagens ilimitadas", "Todos os canais", "Suporte prioritário", "Analytics avançado"],
    color: "bg-purple-600",
    popular: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Customizado",
    duration: "contato",
    features: ["Tudo do Pro", "Múltiplos usuários", "API acesso", "Suporte 24/7"],
    color: "bg-purple-800",
  },
];

export default function Signup() {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState<"form" | "plan" | "success">("form");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    nome: "", // Mantido conforme o banco
    email: "",
    password: "",
    confirmPassword: "",
    telefone: "", // Mantido conforme o banco
    acceptTerms: false,
  });

  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    message: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    setFormData((prev) => ({ ...prev, [name]: newValue }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }

    if (name === "password") {
      const validation = validatePassword(value);
      if (validation.valid) {
        setPasswordStrength({ score: 100, message: "Senha forte" });
      } else {
        setPasswordStrength({
          score: Math.max(0, 100 - validation.errors.length * 25),
          message: "Senha fraca",
        });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    
    // CORREÇÃO: Mapeia para o validador que espera fullName
    const validationErrors = validateSignupForm({
      ...formData,
      fullName: formData.nome,
      phone: formData.telefone
    });

    if (validationErrors.length > 0) {
      const errorMap = validationErrors.reduce(
        (acc, err) => ({ ...acc, [err.field === "fullName" ? "nome" : err.field]: err.message }),
        {}
      );
      setErrors(errorMap);
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nome: formData.nome,
          email: formData.email,
          password: formData.password,
          confirmPassword: formData.confirmPassword,
          telefone: formData.telefone || "",
          plan: "free",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        let errorMessage = "Erro ao realizar cadastro.";
        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail[0].msg || "Dados inválidos.";
        } else if (data.message) {
          errorMessage = data.message;
        }
        setErrors({ email: errorMessage }); 
        setLoading(false);
        return;
      }

      setStep("plan");
    } catch (error) {
      console.error("❌ Erro de conexão:", error);
      setErrors({ nome: "Não foi possível conectar ao servidor." });
    } finally {
      setLoading(false);
    }
  };

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId);
    setStep("success");
    setTimeout(() => {
      localStorage.setItem("user", JSON.stringify({ email: formData.email, name: formData.nome, plan: planId }));
      setLocation("/dashboard");
    }, 2000);
  };

  if (step === "success") {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-500/20">
            <CheckIcon className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2 font-display">Cadastro Realizado!</h2>
          <p className="text-gray-300">Bem-vindo ao HypeCerto, {formData.nome}!</p>
        </div>
      </div>
    );
  }

  if (step === "plan") {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div key={plan.id} className={`rounded-2xl p-8 text-white transition-all cursor-pointer hover:scale-105 ${plan.color}`} onClick={() => handlePlanSelect(plan.id)}>
              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <p className="text-4xl font-bold mb-6">{plan.price}</p>
              <Button className="w-full bg-white text-black font-bold">Selecionar</Button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-md">
        <form 
          onSubmit={handleSubmit} 
          className="bg-purple-50 border border-purple-100 rounded-2xl p-8 shadow-2xl shadow-purple-500/20 space-y-6"
        >
          <div className="text-center mb-8">
            <div className="flex justify-center mb-6">
              <img src="/logo.png" alt="HypeCerto" className="h-16 object-contain" />
            </div>
            <h1 className="text-2xl font-bold text-gray-950 mb-2 font-display">Criar Conta</h1>
            <p className="text-zinc-600 text-sm">Junte-se ao HypeCerto e inicie suas automatizações</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-800 mb-2">Nome Completo</label>
            <Input
              name="nome" // CORREÇÃO: name igual ao estado
              value={formData.nome} // CORREÇÃO: value igual ao estado
              onChange={handleChange}
              placeholder="Seu nome completo"
              className="bg-white border-purple-200 text-gray-950 focus:ring-purple-500"
              required
            />
            {errors.nome && <p className="text-red-500 text-xs mt-1 flex items-center gap-1"><AlertCircle className="w-3 h-3"/>{errors.nome}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-800 mb-2">E-mail</label>
            <Input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="seu@email.com"
              className="bg-white border-purple-200 text-gray-950"
              required
            />
            {errors.email && <p className="text-red-500 text-xs mt-1 flex items-center gap-1"><AlertCircle className="w-3 h-3"/>{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-800 mb-2">Senha</label>
            <div className="relative">
              <Input
                name="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="bg-white border-purple-200 text-gray-950 pr-10"
                required
              />
              <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && <p className="text-red-500 text-xs mt-1 flex items-center gap-1"><AlertCircle className="w-3 h-3"/>{errors.password}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-800 mb-2">Confirmar Senha</label>
            <div className="relative">
                <Input
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="bg-white border-purple-200 text-gray-950 pr-10"
                required
                />
                <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
            </div>
            {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-800 mb-2">Telefone (Opcional)</label>
            <Input
              name="telefone" // CORREÇÃO: name igual ao estado
              value={formData.telefone} // CORREÇÃO: value igual ao estado
              onChange={handleChange}
              placeholder="(11) 99999-9999"
              className="bg-white border-purple-200 text-gray-950"
            />
            {errors.telefone && <p className="text-red-500 text-xs mt-1">{errors.telefone}</p>}
          </div>

          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              name="acceptTerms"
              id="acceptTerms"
              checked={formData.acceptTerms}
              onChange={handleChange}
              className="mt-1 w-4 h-4 rounded border-purple-300 text-purple-600 focus:ring-purple-500 cursor-pointer"
              required
            />
            <label htmlFor="acceptTerms" className="text-sm text-zinc-700 cursor-pointer">
              Concordo com os <span className="text-purple-600 underline font-medium">Termos de Uso</span> e <span className="text-purple-600 underline font-medium">Privacidade</span>.
            </label>
          </div>
          {errors.acceptTerms && <p className="text-red-500 text-xs flex items-center gap-1"><AlertCircle className="w-3 h-3"/>{errors.acceptTerms}</p>}

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white font-semibold hover:bg-purple-700 transition-all py-6 rounded-xl"
          >
            {loading ? "Processando..." : "Cadastrar"}
          </Button>

          <div className="text-center pt-2">
            <p className="text-zinc-600 text-sm">
              Já tem uma conta?{" "}
              <button type="button" onClick={() => setLocation("/login")} className="text-purple-600 hover:text-purple-700 underline font-semibold">
                Entrar aqui
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}