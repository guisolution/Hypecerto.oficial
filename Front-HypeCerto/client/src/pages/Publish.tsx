import { useState } from "react";
import { useLocation } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Check, UploadCloud, Pencil, Save, X } from "lucide-react";

/**
 * Design: Modern Tech Dashboard
 * - Sidebar com canais selecionáveis (com imagens .png)
 * - Preview da postagem no centro com Drag & Drop de Imagem
 * - Opção de Editar Título e Descrição (Lápis)
 * - Botão roxo de publicação
 */
export default function Publish() {
  const [, setLocation] = useLocation();
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [showSuccess, setShowSuccess] = useState(false);
  
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Carrega os dados salvos e cria um estado para eles
  const [projectData, setProjectData] = useState(() => 
    JSON.parse(localStorage.getItem("projectData") || "{}")
  );

  // Estados para controlar o modo de edição
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    projectName: projectData.projectName || "",
    description: projectData.description || "",
  });

  const channels = [
    { id: "facebook", name: "Facebook", icon: "/facebook.png" },
    { id: "instagram", name: "Instagram", icon: "/instagran.png" },
    { id: "tiktok", name: "TikTok", icon: "/tiktok.png" },
    { id: "youtube", name: "YouTube", icon: "/youtube.png" },
    { id: "whatsapp", name: "WhatsApp", icon: "/whatsapp.png" },
    { id: "linkedin", name: "LinkedIn", icon: "/linkedin.png" },
  ];

  const toggleChannel = (id: string) => {
    setSelectedChannels((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const toggleAllChannels = () => {
    if (selectedChannels.length === channels.length) {
      setSelectedChannels([]); 
    } else {
      setSelectedChannels(channels.map(c => c.id)); 
    }
  };

  const handlePublish = () => {
    setShowSuccess(true);
    setTimeout(() => {
      setLocation("/dashboard");
    }, 3000);
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
    const url = URL.createObjectURL(file);
    setImagePreview(url);
  };

  // Funções de Edição do Texto
  const handleSaveEdit = () => {
    const updatedData = { ...projectData, ...editForm };
    setProjectData(updatedData); // Atualiza na tela
    localStorage.setItem("projectData", JSON.stringify(updatedData)); // Salva no LocalStorage
    setIsEditing(false); // Fecha o modo de edição
  };

  const handleCancelEdit = () => {
    // Restaura os valores para o que estava antes
    setEditForm({
      projectName: projectData.projectName || "",
      description: projectData.description || "",
    });
    setIsEditing(false);
  };

  return (
    <DashboardLayout activeTab="publish">
      {!showSuccess ? (
        <div className="space-y-6">
          <h1 className="text-3xl font-bold text-gray-900 font-display">Publicar</h1>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Sidebar - Canais */}
            <div className="lg:col-span-1">
              <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm sticky top-24">
                <h2 className="text-lg font-bold text-gray-900 mb-4 font-display">Canais</h2>

                <div className="mb-6 pb-6 border-b border-gray-200">
                  <button 
                    onClick={toggleAllChannels}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 text-left"
                  >
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center">
                      <img src="/todoscanais.png" alt="Todos os canais" className="w-6 h-6 object-contain" />
                    </div>
                    <span className="font-medium text-gray-700">Todos os canais</span>
                  </button>
                </div>

                <div className="space-y-2 mb-6">
                  {channels.map((channel) => (
                    <button
                      key={channel.id}
                      onClick={() => toggleChannel(channel.id)}
                      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200 ${
                        selectedChannels.includes(channel.id)
                          ? "bg-purple-100 border border-purple-300"
                          : "hover:bg-gray-50 border border-transparent"
                      }`}
                    >
                      <div className="w-8 h-8 flex items-center justify-center">
                        <img src={channel.icon} alt={channel.name} className="w-7 h-7 object-contain" />
                      </div>
                      <span className="font-medium text-gray-700 flex-1 text-left">{channel.name}</span>
                      {selectedChannels.includes(channel.id) && (
                        <Check className="w-5 h-5 text-purple-600" />
                      )}
                    </button>
                  ))}
                </div>

                <div className="space-y-2 border-t border-gray-200 pt-4">
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                    Mostrar mais canais
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                    Gerenciar tags
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors duration-200">
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
                        ou clique para procurar no computador
                      </p>
                      <p className="text-xs text-gray-400 mt-4">
                        Formatos suportados: JPG, PNG, GIF
                      </p>
                    </div>
                  )}
                </div>

                {/* Seção Editável de Informações da Postagem */}
                <div className="mb-8 border-t border-gray-100 pt-8 relative">
                  
                  {/* Cabeçalho da Seção com Botão de Editar/Salvar */}
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
                    {/* Exibição Condicional: Leitura vs Edição */}
                    {!isEditing ? (
                      <>
                        <div>
                          <h3 className="text-sm font-semibold text-gray-600 mb-1">Título do Projeto</h3>
                          <p className="text-gray-900 font-medium">{projectData.projectName || "Não definido"}</p>
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
                        {selectedChannels.length > 0 ? (
                          selectedChannels.map((id) => {
                            const channel = channels.find((c) => c.id === id);
                            return (
                              <span
                                key={id}
                                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium flex items-center gap-1.5"
                              >
                                {channel && <img src={channel.icon} alt="" className="w-3.5 h-3.5 object-contain" />}
                                {channel?.name}
                              </span>
                            );
                          })
                        ) : (
                          <p className="text-gray-500 text-sm italic">Nenhum canal selecionado</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-center">
                  <Button
                    onClick={handlePublish}
                    disabled={selectedChannels.length === 0 || !imagePreview}
                    className="bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed px-12 py-6 rounded-lg font-semibold transition-all duration-200"
                  >
                    Publicar
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