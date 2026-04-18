import DashboardLayout from "@/components/DashboardLayout";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Users, MessageSquare, Heart, Share2, TrendingUp } from "lucide-react";

/**
 * Design: Modern Tech Dashboard
 * - Cards com métricas coloridas
 * - Gráficos com cores roxas
 * - Layout em grid responsivo
 */

const projectsData = [
  { name: "EAD", progress: 65, color: "#6D28D9" },
  { name: "Liderança", progress: 30, color: "#8B5CF6" },
  { name: "Evangelismo", progress: 89, color: "#F59E0B" },
];

const activityData = [
  { name: "Seg", value: 45 },
  { name: "Ter", value: 52 },
  { name: "Qua", value: 48 },
  { name: "Qui", value: 61 },
  { name: "Sex", value: 55 },
  { name: "Sab", value: 67 },
  { name: "Dom", value: 58 },
];

const summaryData = [
  { name: "Projetos", value: 40, color: "#6D28D9" },
  { name: "Atribuída", value: 70, color: "#3B82F6" },
  { name: "Fechada", value: 89, color: "#EC4899" },
];

export default function Results() {
  return (
    <DashboardLayout activeTab="results">
      <div className="space-y-6">
        {/* Título */}
        <h1 className="text-3xl font-bold text-gray-900 font-display">Resultados</h1>

        {/* Projetos Recentes */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 font-display">Projetos Recentes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {projectsData.map((project) => (
              <div key={project.name} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-900">{project.name}</h3>
                  <span className="text-sm font-bold text-gray-700">{project.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-300"
                    style={{ width: `${project.progress}%`, backgroundColor: project.color }}
                  ></div>
                </div>
                <div className="flex gap-2 mt-3">
                  <div className="w-6 h-6 rounded-full bg-purple-200 flex items-center justify-center text-xs font-bold text-purple-600">
                    👤
                  </div>
                  <div className="w-6 h-6 rounded-full bg-purple-200 flex items-center justify-center text-xs font-bold text-purple-600">
                    👤
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Atividade */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900 mb-6 font-display">Atividade</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="name" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#FFFFFF",
                    border: "1px solid #E5E7EB",
                    borderRadius: "8px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#6D28D9"
                  strokeWidth={3}
                  dot={{ fill: "#6D28D9", r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Calendário Mini */}
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 font-display">Abril 2025</h2>
            <div className="grid grid-cols-7 gap-1 text-center text-xs">
              {["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"].map((day) => (
                <div key={day} className="font-semibold text-gray-600 py-1">
                  {day}
                </div>
              ))}
              {Array.from({ length: 30 }).map((_, i) => (
                <div
                  key={i}
                  className={`py-1 rounded transition-colors duration-200 ${
                    i + 1 === 24
                      ? "bg-purple-600 text-white font-bold"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {i + 1}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resumo da Tarefa */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-6 font-display">Resumo da Tarefa</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {summaryData.map((item) => (
              <div
                key={item.name}
                className="p-6 rounded-lg text-white transition-all duration-200 hover:shadow-lg"
                style={{ backgroundColor: item.color }}
              >
                <h3 className="font-semibold mb-2">{item.name}</h3>
                <p className="text-3xl font-bold font-display">{item.value}</p>
              </div>
            ))}
          </div>

          {/* Taxa de Conclusão */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">Taxa de conclusão do projeto</h3>
              <span className="text-sm font-bold text-purple-600">+2.3%</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-300"
                    style={{ width: "95%" }}
                  ></div>
                </div>
              </div>
              <span className="font-bold text-gray-900">95%</span>
            </div>
          </div>
        </div>

        {/* Mensagens */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4 font-display">Mensagens</h2>
          <div className="space-y-3">
            {[
              { name: "Carolina", message: "Ótimo trabalho na última postagem!" },
              { name: "Marcelo", message: "Pode revisar o conteúdo da próxima semana?" },
            ].map((msg) => (
              <div
                key={msg.name}
                className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="w-10 h-10 rounded-full bg-purple-200 flex items-center justify-center font-bold text-purple-600">
                  {msg.name[0]}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{msg.name}</p>
                  <p className="text-sm text-gray-600">{msg.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
