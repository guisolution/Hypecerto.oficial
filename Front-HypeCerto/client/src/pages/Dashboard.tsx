import { useState } from "react";
import { useLocation } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { 
  ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, 
  List, Clock, X, Pencil, Save, ImageIcon, Filter 
} from "lucide-react";

const AVAILABLE_CHANNELS = ["Facebook", "Instagram", "TikTok", "YouTube", "WhatsApp", "LinkedIn"];

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<"calendar" | "list">("calendar");
  
  // Filtro exclusivo para o modo lista
  const [listFilter, setListFilter] = useState<"day" | "week" | "month">("month");

  const days = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"];
  const months = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
  ];

  // Estado dos agendamentos
  const [schedules, setSchedules] = useState<any[]>([]);

  // Estados para o Modal de Resumo da Postagem
  const [selectedPost, setSelectedPost] = useState<typeof schedules[0] | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ 
    title: "", 
    description: "", 
    time: "", 
    channels: [] as string[] 
  });

  const getDaysInMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const getFirstDayOfMonth = (date: Date) => new Date(date.getFullYear(), date.getMonth(), 1).getDay();

  const handlePrevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  const handleNextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));

  // Funções do Modal
  const openPostModal = (post: typeof schedules[0]) => {
    setSelectedPost(post);
    setEditForm({ 
      title: post.title, 
      description: post.description,
      time: post.time,
      channels: [...post.channels] 
    });
    setIsEditing(false);
  };

  const closePostModal = () => {
    setSelectedPost(null);
    setIsEditing(false);
  };

  const handleSaveEdit = () => {
    if (!selectedPost) return;
    
    // Atualiza a postagem na lista
    setSchedules(prev => prev.map(p => 
      p.id === selectedPost.id 
        ? { 
            ...p, 
            title: editForm.title, 
            description: editForm.description,
            time: editForm.time,
            channels: editForm.channels
          } 
        : p
    ));
    
    // Atualiza o post selecionado no modal para refletir a mudança instantaneamente
    setSelectedPost({ 
      ...selectedPost, 
      title: editForm.title, 
      description: editForm.description,
      time: editForm.time,
      channels: editForm.channels
    });
    
    setIsEditing(false);
  };

  // Função para alternar seleção de canais durante a edição
  const toggleChannel = (channel: string) => {
    setEditForm(prev => {
      const isSelected = prev.channels.includes(channel);
      return {
        ...prev,
        channels: isSelected 
          ? prev.channels.filter(c => c !== channel)
          : [...prev.channels, channel]
      };
    });
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const calendarDays = [];

  for (let i = 0; i < firstDay; i++) calendarDays.push(null);
  for (let i = 1; i <= daysInMonth; i++) calendarDays.push(i);

  // Filtra as postagens do modo lista com base no filtro selecionado
  const getFilteredListSchedules = () => {
    return schedules.filter(s => {
      if (listFilter === "day") return s.day === 1; // Simulação de "Hoje" (Dia 1)
      if (listFilter === "week") return s.day >= 1 && s.day <= 7; // Simulação da primeira semana
      return true; // Mês inteiro
    }).sort((a, b) => a.day - b.day || a.time.localeCompare(b.time));
  };

  return (
    <DashboardLayout activeTab="publications">
      <div className="space-y-6 relative">
        
        {/* Header com Navegação de Mês */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <button onClick={handlePrevMonth} className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200">
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <h2 className="text-2xl font-bold text-gray-900 min-w-[200px] text-center font-display">
                {months[currentDate.getMonth()].toUpperCase()} {currentDate.getFullYear()}
              </h2>
              <button onClick={handleNextMonth} className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200">
                <ChevronRight className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>

        {/* Controles de Visualização (Lista/Calendário) e Novo Post */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex flex-wrap items-center gap-4">
            {/* Alternar Visualização */}
            <div className="flex gap-2 bg-gray-100 p-1 rounded-lg">
              <button 
                onClick={() => setViewMode("list")}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 ${
                  viewMode === "list" ? "bg-white text-purple-700 shadow-sm" : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <List className="w-4 h-4" />
                Lista
              </button>
              <button 
                onClick={() => setViewMode("calendar")}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 ${
                  viewMode === "calendar" ? "bg-white text-purple-700 shadow-sm" : "text-gray-600 hover:text-gray-900"
                }`}
              >
                <CalendarIcon className="w-4 h-4" />
                Calendário
              </button>
            </div>

            {/* Filtros da Lista (Só aparece se estiver no modo lista) */}
            {viewMode === "list" && (
              <div className="flex items-center gap-2 border-l border-gray-200 pl-4">
                <Filter className="w-4 h-4 text-gray-400" />
                <button 
                  onClick={() => setListFilter("day")}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${listFilter === "day" ? "bg-purple-100 text-purple-700" : "text-gray-600 hover:bg-gray-50"}`}
                >
                  Hoje
                </button>
                <button 
                  onClick={() => setListFilter("week")}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${listFilter === "week" ? "bg-purple-100 text-purple-700" : "text-gray-600 hover:bg-gray-50"}`}
                >
                  Semana
                </button>
                <button 
                  onClick={() => setListFilter("month")}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${listFilter === "month" ? "bg-purple-100 text-purple-700" : "text-gray-600 hover:bg-gray-50"}`}
                >
                  Mês Todo
                </button>
              </div>
            )}
          </div>

          <Button 
            onClick={() => setLocation("/create")}
            className="bg-purple-600 text-white hover:bg-purple-700 gap-2 w-full md:w-auto shadow-md shadow-purple-500/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            Nova Postagem
          </Button>
        </div>

        {/* ===================== RENDERIZAÇÃO: CALENDÁRIO OU LISTA ===================== */}
        
        {viewMode === "calendar" ? (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <div className="grid grid-cols-7 gap-2 mb-4">
              {days.map((day) => (
                <div key={day} className="text-center font-bold text-gray-400 text-xs tracking-wider uppercase py-2">
                  {day.slice(0, 3)}
                </div>
              ))}
            </div>

            <div className="grid grid-cols-7 gap-2 min-h-[500px]">
              {calendarDays.map((day, index) => {
                const daySchedules = schedules.filter(s => s.day === day).sort((a,b) => a.time.localeCompare(b.time));

                return (
                  <div
                    key={index}
                    className={`border rounded-lg p-3 min-h-[100px] transition-all duration-200 flex flex-col ${
                      day ? "border-gray-200 hover:border-purple-400 hover:shadow-md bg-white" : "border-transparent bg-gray-50/50"
                    }`}
                  >
                    {day && (
                      <>
                        <div className="font-semibold text-gray-700 text-sm mb-2">{day}</div>
                        <div className="flex flex-col gap-1.5 flex-1">
                          {daySchedules.map((schedule) => (
                            <div 
                              key={schedule.id}
                              onClick={() => openPostModal(schedule)}
                              className="text-xs px-2 py-1.5 rounded bg-purple-50 text-purple-700 border border-purple-100 font-medium truncate cursor-pointer hover:bg-purple-100 transition-colors"
                              title={schedule.title}
                            >
                              {schedule.time} - {schedule.title}
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-gray-900 font-display">Próximas Postagens</h3>
                <p className="text-sm text-gray-500">Acompanhe a fila de agendamentos ({listFilter === 'month' ? 'do mês inteiro' : listFilter === 'week' ? 'desta semana' : 'de hoje'}).</p>
              </div>
            </div>
            
            <div className="divide-y divide-gray-100">
              {getFilteredListSchedules().length > 0 ? (
                getFilteredListSchedules().map((schedule) => (
                  <div 
                    key={schedule.id} 
                    onClick={() => openPostModal(schedule)}
                    className="p-6 hover:bg-gray-50 transition-colors flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 cursor-pointer group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex flex-col items-center justify-center bg-purple-50 border border-purple-100 rounded-lg min-w-[64px] py-2 group-hover:bg-purple-100 transition-colors">
                        <span className="text-sm font-semibold text-purple-600">{months[currentDate.getMonth()].slice(0, 3)}</span>
                        <span className="text-xl font-bold text-purple-900">{schedule.day.toString().padStart(2, '0')}</span>
                      </div>
                      
                      <div>
                        <h4 className="font-bold text-gray-900 mb-1 group-hover:text-purple-700 transition-colors">{schedule.title}</h4>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
                          <span className="flex items-center gap-1 font-medium bg-gray-100 px-2 py-0.5 rounded text-gray-700">
                            <Clock className="w-3.5 h-3.5" />
                            {schedule.time}
                          </span>
                          <span className="flex items-center gap-1 font-medium text-gray-600">
                            {schedule.channels.join(", ")}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 w-full sm:w-auto justify-between sm:justify-end">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        schedule.status === "Agendado" ? "bg-blue-50 text-blue-600 border border-blue-200" : "bg-green-50 text-green-600 border border-green-200"
                      }`}>
                        {schedule.status}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-12 text-center text-gray-500 flex flex-col items-center justify-center">
                  <CalendarIcon className="w-12 h-12 text-gray-300 mb-3" />
                  <p>Nenhuma postagem encontrada para este filtro.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===================== MODAL DE RESUMO / EDIÇÃO ===================== */}
        {selectedPost && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
              
              {/* Header do Modal */}
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${
                    selectedPost.status === "Agendado" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"
                  }`}>
                    {selectedPost.status}
                  </span>
                  
                  {!isEditing && (
                    <span className="text-sm font-medium text-gray-500 flex items-center gap-1.5">
                      <Clock className="w-4 h-4" /> 
                      {selectedPost.day} de {months[currentDate.getMonth()].slice(0,3)} às {selectedPost.time}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-1">
                  {/* Botão de Editar */}
                  {!isEditing && selectedPost.status === "Agendado" && (
                    <button 
                      onClick={() => setIsEditing(true)}
                      className="p-2 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="Editar Postagem"
                    >
                      <Pencil className="w-5 h-5" />
                    </button>
                  )}
                  {/* Botão Fechar */}
                  <button 
                    onClick={closePostModal}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Corpo do Modal */}
              <div className="p-6 overflow-y-auto">
                {!isEditing ? (
                  // MODO VISUALIZAÇÃO
                  <div className="space-y-6">
                    <div className="w-full h-48 bg-gray-100 rounded-xl border border-gray-200 overflow-hidden flex items-center justify-center">
                      {selectedPost.image ? (
                        <img src={selectedPost.image} alt="Preview" className="w-full h-full object-contain" />
                      ) : (
                        <div className="flex flex-col items-center text-gray-400">
                          <ImageIcon className="w-8 h-8 mb-2 opacity-50" />
                          <span className="text-sm">Sem imagem anexada</span>
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2 font-display">{selectedPost.title}</h3>
                      <p className="text-gray-700 whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg border border-gray-100">
                        {selectedPost.description}
                      </p>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Canais de Publicação</h4>
                      <div className="flex gap-2 flex-wrap">
                        {selectedPost.channels.map(c => (
                          <span key={c} className="px-3 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-full text-sm font-medium">
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  // MODO EDIÇÃO
                  <div className="space-y-5">
                    <div className="bg-purple-50 text-purple-700 p-3 rounded-lg text-sm font-medium mb-2 flex items-center gap-2 border border-purple-100">
                      <Pencil className="w-4 h-4" /> Editando Postagem
                    </div>
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1">Título</label>
                      <input 
                        type="text" 
                        value={editForm.title}
                        onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                        className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                      />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      {/* Edição de Horário */}
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-1">Horário</label>
                        <input 
                          type="time" 
                          value={editForm.time}
                          onChange={(e) => setEditForm({...editForm, time: e.target.value})}
                          className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Canais de Publicação</label>
                      <div className="flex flex-wrap gap-2">
                        {AVAILABLE_CHANNELS.map(channel => {
                          const isSelected = editForm.channels.includes(channel);
                          return (
                            <button
                              key={channel}
                              type="button"
                              onClick={() => toggleChannel(channel)}
                              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                                isSelected 
                                  ? "bg-purple-600 text-white shadow-sm" 
                                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                              }`}
                            >
                              {channel}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1">Legenda / Descrição</label>
                      <textarea 
                        value={editForm.description}
                        onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg min-h-[120px] focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all resize-none text-sm"
                      />
                    </div>
                    
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                      <Button variant="outline" onClick={() => setIsEditing(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={handleSaveEdit} className="bg-green-600 hover:bg-green-700 text-white gap-2">
                        <Save className="w-4 h-4" />
                        Salvar Alterações
                      </Button>
                    </div>
                  </div>
                )}
              </div>
              
            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}