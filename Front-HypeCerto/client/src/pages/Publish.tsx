import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Check, UploadCloud, Pencil, Save, X, Loader2, AlertTriangle, Link2 } from "lucide-react";

const API_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

interface ContaSocial {
  id: number;
  plataforma_id: number | null;
  nome_conta: string | null;
  page_id: string | null;
  ig_user_id: string | null;
  ativa: boolean;
  plataforma_nome: string | null;
}

const ICONES_PLATAFORMA: Record<string, string> = {
  facebook: "/facebook.png",
  instagram: "/instagran.png",
  tiktok: "/tiktok.png",
  youtube: "/youtube.png",
  whatsapp: "/whatsapp.png",
  linkedin: "/linkedin.png",
};

/**
 * Design: Modern Tech Dashboard
 * - Sidebar com as contas REALMENTE conectadas (vindas de GET /channels)
 * - Preview da postagem no centro com Drag & Drop de Imagem
 * - Opção de Editar Título e Descrição (Lápis)
 * - Seletor de "Publicar agora" ou agendar para uma data/hora
 * - Botão roxo dispara upload de mídia + criação de agendamentos de verdade
 */
export default function Publish() {
  const [, setLocation] = useLocation();
  const [selectedContaIds, setSelectedContaIds] = useState<number[]>([]);
  const [showSuccess, setShowSuccess] = useState(false);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const [contas, setContas] = useState<ContaSocial[]>([]);
  const [loadingContas, setLoadingContas] = useState(true);

  const [scheduleMode, setScheduleMode] = useState<"now" | "later">("now");
  const [scheduledAt, setScheduledAt] = useState("");

  const [isPublishing, setIsPublishing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Carrega os dados salvos na tela anterior (Create.tsx)
  const [projectData, setProjectData] = useState(() =>
    JSON.parse(localStorage.getItem("projectData") || "{}")
  );

  // Estados para controlar o modo de edição
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    projectName: projectData.nome_do_projeto || projectData.projectName || "",
    description: projectData.description || "",
  });

  // Busca as contas sociais REALMENTE conectadas
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setLoadingContas(false);
      return;
    }

    fetch(`${API_URL}/channels`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((data: ContaSocial[]) => setContas(data.filter((c) => c.ativa)))
      .catch(() => setContas([]))
      .finally(() => setLoadingContas(false));
  }, []);

  const toggleConta = (id: number) => {
    setSelectedContaIds((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const toggleAllContas = () => {
    if (selectedContaIds.length === contas.length) {
      setSelectedContaIds([]);
    } else {
      setSelectedContaIds(contas.map((c) => c.id));
    }
  };

  // Funções do Drag & Drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  // Funções de Edição do Texto
  const handleSaveEdit = () => {
    const updatedData = { ...projectData, ...editForm };
    setProjectData(updatedData);
    localStorage.setItem("projectData", JSON.stringify(updatedData));
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditForm({
      projectName: projectData.nome_do_projeto || projectData.projectName || "",
      description: projectData.description || "",
    });
    setIsEditing(false);
  };

  const handlePublish = async () => {
    setErrorMsg(null);

    const token = localStorage.getItem("token");
    const postagemId = projectData.postagem_id;

    if (!token) {
      setErrorMsg("Você precisa estar logado.");
      return;
    }
    if (!postagemId) {
      setErrorMsg(
        "Nenhuma postagem encontrada. Volte para a tela 'Criar' e preencha o conteúdo novamente."
      );
      return;
    }
    if (selectedContaIds.length === 0) {
      setErrorMsg("Selecione ao menos uma conta conectada para publicar.");
      return;
    }
    if (scheduleMode === "later" && !scheduledAt) {
      setErrorMsg("Escolha a data e hora do agendamento, ou selecione 'Publicar agora'.");
      return;
    }

    setIsPublishing(true);
    try {
      // 1. Upload da mídia, se houver
      if (imageFile) {
        const form = new FormData();
        form.append("file", imageFile);
        const uploadResp = await fetch(`${API_URL}/posts/${postagemId}/midia`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: form,
        });
        if (!uploadResp.ok) {
          throw new Error("Falha ao enviar a imagem da postagem.");
        }
      }

      // 2. Data/hora do agendamento — "agora" cria com poucos segundos de folga
      // para o scheduler (que roda a cada 60s) pegar automaticamente.
      const dataAgendada =
        scheduleMode === "now"
          ? new Date(Date.now() + 5000).toISOString()
          : new Date(scheduledAt).toISOString();

      // 3. Cria um agendamento para cada conta selecionada
      const agendamentosCriados: number[] = [];
      for (const contaId of selectedContaIds) {
        const resp = await fetch(`${API_URL}/agendamentos`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            postagem_id: postagemId,
            conta_social_id: contaId,
            data_agendada: dataAgendada,
          }),
        });
        const data = await resp.json();
        if (!resp.ok) {
          throw new Error(data.detail || "Falha ao criar agendamento.");
        }
        agendamentosCriados.push(data.id);
      }

      // 4. Se for "publicar agora", dispara a publicação imediatamente
      //    em vez de esperar o próximo ciclo do scheduler (até 60s).
      if (scheduleMode === "now") {
        await Promise.all(
          agendamentosCriados.map((agendamentoId) =>
            fetch(`${API_URL}/meta/publicar`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({ agendamento_id: agendamentoId }),
            }).catch(() => null)
          )
        );
      }

      setShowSuccess(true);
      localStorage.removeItem("projectData");
      setTimeout(() => setLocation("/dashboard"), 3000);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Erro ao publicar.");
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <DashboardLayout activeTab="publish">
      {!showSuccess ? (
        <div className="space-y-6">
          <h1 className="text-3xl font-bold text-gray-900 font-display">Publicar</h1>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar - Canais REALMENTE conectados */}
            <div className="lg:col-span-1">
              <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm sticky top-24">
                <h2 className="text-lg font-bold text-gray-900 mb-4 font-display">Canais</h2>

                {loadingContas ? (
                  <div className="flex items-center gap-2 text-sm text-gray-500 py-4">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Carregando contas conectadas...
                  </div>
                ) : contas.length === 0 ? (
                  <div className="text-sm text-gray-500 space-y-3 py-2">
                    <p>Você ainda não conectou nenhuma conta.</p>
                    <Button
                      variant="outline"
                      className="w-full border-purple-200 text-purple-700 hover:bg-purple-50"
                      onClick={() => setLocation("/channels")}
                    >
                      <Link2 className="w-4 h-4 mr-2" />
                      Conectar uma conta
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="mb-6 pb-6 border-b border-gray-200">
                      <button
                        onClick={toggleAllContas}
                        className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 text-left"
                      >
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center">
                          <img src="/todoscanais.png" alt="Todos os canais" className="w-6 h-6 object-contain" />
                        </div>
                        <span className="font-medium text-gray-700">Todos os canais</span>
                      </button>
                    </div>

                    <div className="space-y-2 mb-6">
                      {contas.map((conta) => {
                        const slug = (conta.plataforma_nome || "").toLowerCase();
                        const icon = ICONES_PLATAFORMA[slug] || "/todoscanais.png";
                        return (
                          <button
                            key={conta.id}
                            onClick={() => toggleConta(conta.id)}
                            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 ${
                              selectedContaIds.includes(conta.id)
                                ? "bg-purple-100 border border-purple-300"
                                : "hover:bg-gray-50 border border-transparent"
                            }`}
                          >
                            <div className="w-8 h-8 flex items-center justify-center">
                              <img src={icon} alt={conta.plataforma_nome || ""} className="w-7 h-7 object-contain" />
                            </div>
                            <span className="font-medium text-gray-700 flex-1 text-left truncate">
                              {conta.nome_conta || conta.plataforma_nome}
                            </span>
                            {selectedContaIds.includes(conta.id) && (
                              <Check className="w-5 h-5 text-purple-600" />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </>
                )}

                <div className="space-y-2 border-t border-gray-200 pt-4">
                  <button
                    onClick={() => setLocation("/channels")}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200"
                  >
                    Gerenciar Canais
                  </button>
                </div>
              </div>
            </div>

            {/* Preview da Postagem com Drag & Drop */}
            <div className="lg:col-span-3">
              <div className="bg-white border border-gray-200 rounded-xl p-8 shadow-sm">
                <h2 className="text-lg font-bold text-gray-900 mb-6 font-display">Mídia da Postagem</h2>

                <div
                  className={`relative w-full h-80 mb-8 border-2 border-dashed rounded-xl flex flex-col items-center justify-center transition-all duration-200 overflow-hidden ${
                    dragActive
                      ? "border-purple-500 bg-purple-50"
                      : imagePreview
                        ? "border-transparent bg-gray-100"
                        : "border-gray-300 bg-gray-50 hover:bg-gray-100"
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />

                  {imagePreview ? (
                    <>
                      <img
                        src={imagePreview}
                        alt="Preview da Postagem"
                        className="w-full h-full object-contain"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-200">
                        <p className="text-white font-medium flex items-center gap-2">
                          <UploadCloud className="w-5 h-5" />
                          Clique ou arraste para trocar a imagem
                        </p>
                      </div>
                    </>
                  ) : (
                    <div className="flex flex-col items-center text-center p-6 pointer-events-none">
                      <img
                        src="/uplod.png"
                        alt="Ícone de Upload"
                        className="w-24 h-24 object-contain mb-4 opacity-90"
                      />
                      <p className="text-lg font-semibold text-gray-700 mb-1">
                        Arraste e solte sua imagem aqui
                      </p>
                      <p className="text-sm text-gray-500">
                        ou clique para procurar no computador (opcional)
                      </p>
                      <p className="text-xs text-gray-400 mt-4">
                        Formatos suportados: JPG, PNG, GIF
                      </p>
                    </div>
                  )}
                </div>

                {/* Seção Editável de Informações da Postagem */}
                <div className="mb-8 border-t border-gray-100 pt-8 relative">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900 font-display">Texto da Publicação</h3>

                    {!isEditing ? (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-purple-600 bg-purple-50 hover:bg-purple-100 rounded-md transition-colors"
                      >
                        <Pencil className="w-4 h-4" />
                        Editar Texto
                      </button>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={handleCancelEdit}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                        >
                          <X className="w-4 h-4" />
                          Cancelar
                        </button>
                        <button
                          onClick={handleSaveEdit}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                        >
                          <Save className="w-4 h-4" />
                          Salvar
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    {!isEditing ? (
                      <>
                        <div>
                          <h3 className="text-sm font-semibold text-gray-600 mb-1">Título do Projeto</h3>
                          <p className="text-gray-900 font-medium">
                            {projectData.nome_do_projeto || projectData.projectName || "Não definido"}
                          </p>
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-gray-600 mb-1">Legenda / Descrição</h3>
                          <p className="text-gray-700 text-sm whitespace-pre-wrap">
                            {projectData.description || "Nenhuma legenda informada."}
                          </p>
                        </div>
                      </>
                    ) : (
                      <>
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Título do Projeto
                          </label>
                          <Input
                            value={editForm.projectName}
                            onChange={(e) => setEditForm({ ...editForm, projectName: e.target.value })}
                            className="bg-white"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Legenda / Descrição
                          </label>
                          <Textarea
                            value={editForm.description}
                            onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                            className="bg-white min-h-[120px]"
                          />
                        </div>
                      </>
                    )}

                    <div className="pt-4">
                      <h3 className="text-sm font-semibold text-gray-600 mb-2">Canais Selecionados</h3>
                      <div className="flex gap-2 flex-wrap">
                        {selectedContaIds.length > 0 ? (
                          selectedContaIds.map((id) => {
                            const conta = contas.find((c) => c.id === id);
                            const slug = (conta?.plataforma_nome || "").toLowerCase();
                            const icon = ICONES_PLATAFORMA[slug] || "/todoscanais.png";
                            return (
                              <span
                                key={id}
                                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium flex items-center gap-1.5"
                              >
                                <img src={icon} alt="" className="w-3.5 h-3.5 object-contain" />
                                {conta?.nome_conta || conta?.plataforma_nome}
                              </span>
                            );
                          })
                        ) : (
                          <p className="text-gray-500 text-sm italic">Nenhum canal selecionado</p>
                        )}
                      </div>
                    </div>

                    {/* Quando publicar */}
                    <div className="pt-6 border-t border-gray-100">
                      <h3 className="text-sm font-semibold text-gray-600 mb-3">Quando publicar</h3>
                      <div className="flex gap-3 mb-4">
                        <button
                          onClick={() => setScheduleMode("now")}
                          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                            scheduleMode === "now"
                              ? "bg-purple-600 text-white border-purple-600"
                              : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                          }`}
                        >
                          Publicar agora
                        </button>
                        <button
                          onClick={() => setScheduleMode("later")}
                          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                            scheduleMode === "later"
                              ? "bg-purple-600 text-white border-purple-600"
                              : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
                          }`}
                        >
                          Agendar para depois
                        </button>
                      </div>
                      {scheduleMode === "later" && (
                        <Input
                          type="datetime-local"
                          value={scheduledAt}
                          onChange={(e) => setScheduledAt(e.target.value)}
                          className="bg-white max-w-xs"
                        />
                      )}
                    </div>
                  </div>
                </div>

                {errorMsg && (
                  <div className="mb-6 flex items-start gap-2 text-sm text-red-700 bg-red-50 p-4 rounded-lg">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                <div className="flex justify-center">
                  <Button
                    onClick={handlePublish}
                    disabled={isPublishing || selectedContaIds.length === 0}
                    className="bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed px-12 py-6 rounded-lg font-semibold transition-all duration-200"
                  >
                    {isPublishing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Publicando...
                      </>
                    ) : scheduleMode === "now" ? (
                      "Publicar agora"
                    ) : (
                      "Agendar publicação"
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2 font-display">
              Parabéns, sua publicação iniciou o hype
            </h2>
            <p className="text-gray-600">Redirecionando para o dashboard...</p>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
