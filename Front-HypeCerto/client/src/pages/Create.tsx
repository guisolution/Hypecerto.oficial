import { useState } from "react";
import { useLocation } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight, Loader2 } from "lucide-react";

export default function Create() {
  const [, setLocation] = useLocation();
  const [loading, setLoading] = useState(false);

  // Nomes das chaves mantidos, mas inicializados vazios
  const [formData, setFormData] = useState({
    nome_do_projeto: "",
    area_do_projeto: "",
    responsavel: "",
    description: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePublish = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");

      // 1. Cria o "projeto" (mantém compatibilidade com o fluxo existente)
      const projetoResponse = await fetch("http://localhost:8000/projetos", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          nome_do_projeto: formData.nome_do_projeto,
          area_do_projeto: formData.area_do_projeto,
          responsavel: formData.responsavel,
          descricao: formData.description
        }),
      });

      if (!projetoResponse.ok) {
        throw new Error("Falha ao salvar projeto no banco de dados.");
      }

      const projetoSalvo = await projetoResponse.json();

      // 2. Cria a "postagem" de fato — é ela que será agendada/publicada na próxima tela
      const postagemResponse = await fetch("http://localhost:8000/posts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          titulo: formData.nome_do_projeto,
          conteudo: formData.description,
          projeto_id: projetoSalvo.id_projeto,
        }),
      });

      if (!postagemResponse.ok) {
        throw new Error("Falha ao criar a postagem.");
      }

      const postagemSalva = await postagemResponse.json();

      // Salva no localStorage para a próxima tela (Publish.tsx) usar
      localStorage.setItem("projectData", JSON.stringify({
        ...formData,
        id_projeto: projetoSalvo.id_projeto,
        postagem_id: postagemSalva.id,
      }));

      setLocation("/publish");
    } catch (error) {
      console.error("Erro na integração:", error);
      alert("Erro ao salvar o projeto. Verifique se o back-end está rodando.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout activeTab="create">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 font-display">Criação Novo Projeto</h1>

        <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Coluna Esquerda */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Nome do projeto
                </label>
                <Input
                  type="text"
                  name="nome_do_projeto"
                  value={formData.nome_do_projeto}
                  onChange={handleChange}
                  className="bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500"
                  placeholder="Desconto em Matrícula"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Responsável do projeto
                </label>
                <Input
                  type="text"
                  name="responsavel"
                  value={formData.responsavel}
                  onChange={handleChange}
                  className="bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500"
                  placeholder="Guilherme de Paula"
                />
              </div>
            </div>

            {/* Coluna Direita */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Área do projeto
                </label>
                <Input
                  type="text"
                  name="area_do_projeto"
                  value={formData.area_do_projeto}
                  onChange={handleChange}
                  className="bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500"
                  placeholder="Novos alunos"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Data e Horário
                </label>
                <Input
                  type="text"
                  className="bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed"
                  value="AUTOMÁTICO"
                  disabled
                />
              </div>
            </div>
          </div>

          <div className="mt-8">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Descrição da postagem
            </label>
            <Textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-purple-500 min-h-32"
              placeholder="Garanta 50% de DESCONTO na matrícula até junho e comece a transformar seu futuro hoje! 🎓📚 Vagas limitadas - corre pra aproveitar!&#10;&#10;#Desconto #Matrícula #CursosProfissionalizantes #Promoção #VemPraNossaEscola"
            />
          </div>

          <div className="mt-8 flex justify-end">
            <Button
              onClick={handlePublish}
              disabled={loading}
              className="bg-purple-600 text-white hover:bg-purple-700 gap-2 px-8 py-6 rounded-lg font-semibold transition-all duration-200"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  SALVANDO...
                </>
              ) : (
                <>
                  PRÓXIMO: PUBLICAÇÃO
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}