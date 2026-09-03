import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CheckCircle2, Link2, Settings2, ShieldCheck, Loader2, AlertTriangle } from "lucide-react";
import { loginComFacebook, loadFacebookSdk } from "@/lib/facebookSdk";

const API_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

// Redes que usam o fluxo real de login com a Meta (Facebook/Instagram).
// As demais plataformas ainda não têm integração OAuth implementada.
const REDES_META = new Set(["facebook", "instagram"]);

const INITIAL_NETWORKS = [
  { id: "facebook", name: "Facebook", icon: "/facebook.png", isConnected: false },
  { id: "instagram", name: "Instagram", icon: "/instagran.png", isConnected: false },
  { id: "tiktok", name: "TikTok", icon: "/tiktok.png", isConnected: false },
  { id: "youtube", name: "YouTube", icon: "/youtube.png", isConnected: false },
  { id: "whatsapp", name: "WhatsApp", icon: "/whatsapp.png", isConnected: false },
  { id: "linkedin", name: "LinkedIn", icon: "/linkedin.png", isConnected: false },
];

export default function Channels() {
  const [networks, setNetworks] = useState(INITIAL_NETWORKS);
  const [selectedNetwork, setSelectedNetwork] = useState<typeof INITIAL_NETWORKS[0] | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [avisos, setAvisos] = useState<string[]>([]);

  // Estados dos "Switches" de permissão (usados apenas no fluxo simulado
  // de redes ainda sem integração OAuth real, ex: TikTok, YouTube...)
  const [permissions, setPermissions] = useState({
    publish: true,
    analytics: true,
    messages: false,
  });

  // Pré-carrega o SDK do Facebook assim que a página abre — é essencial
  // fazer isso ANTES do clique, senão o navegador bloqueia o popup por
  // achar que a abertura não veio de uma ação direta do usuário.
  useEffect(() => {
    loadFacebookSdk().catch((err) => {
      console.error("Falha ao pré-carregar o SDK do Facebook:", err);
    });
  }, []);

  // Busca as contas já conectadas no backend ao carregar a página
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;

    fetch(`${API_URL}/channels`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : []))
      .then((contas: { plataforma_nome?: string }[]) => {
        const slugsConectados = new Set(
          contas.map((c) => (c.plataforma_nome || "").toLowerCase())
        );
        setNetworks((prev) =>
          prev.map((n) => ({ ...n, isConnected: slugsConectados.has(n.id) || n.isConnected }))
        );
      })
      .catch(() => {
        /* silencioso — a tela funciona mesmo se essa checagem falhar */
      });
  }, []);

  const handleOpenConnect = (network: typeof INITIAL_NETWORKS[0]) => {
    if (network.isConnected) return; // Já conectado — não abre o fluxo de novo

    setSelectedNetwork(network);
    setErrorMsg(null);
    setAvisos([]);

    if (REDES_META.has(network.id)) {
      // Facebook/Instagram usam login real via Facebook SDK — sem modal de permissões,
      // as permissões são solicitadas diretamente pelo popup do Facebook.
      void handleConnectMeta(network);
      return;
    }

    // Demais redes: fluxo simulado (ainda não têm integração OAuth implementada)
    setPermissions({ publish: true, analytics: true, messages: false });
    setIsModalOpen(true);
  };

  const handleConnectMeta = async (network: typeof INITIAL_NETWORKS[0]) => {
    const token = localStorage.getItem("token");
    if (!token) {
      setErrorMsg("Você precisa estar logado para conectar uma conta.");
      return;
    }

    setIsLoading(true);
    setSelectedNetwork(network);
    setIsModalOpen(true); // Reaproveita o modal só para exibir o estado de carregamento/erro

    try {
      const { accessToken } = await loginComFacebook();

      const response = await fetch(`${API_URL}/meta/oauth/facebook`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ access_token: accessToken }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Não foi possível conectar com a Meta.");
      }

      const plataformasConectadas = new Set(
        (data.contas as { plataforma: string }[]).map((c) => c.plataforma)
      );

      setNetworks((prev) =>
        prev.map((n) =>
          plataformasConectadas.has(n.id) ? { ...n, isConnected: true } : n
        )
      );
      setAvisos(data.avisos || []);
      setIsModalOpen(plataformasConectadas.size === 0 && (data.avisos || []).length > 0);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Erro ao conectar com o Facebook.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = () => {
    if (!selectedNetwork) return;

    if (REDES_META.has(selectedNetwork.id)) {
      // Já tratado por handleConnectMeta — este botão só fecha o modal nesse caso
      setIsModalOpen(false);
      return;
    }

    setIsLoading(true);

    // Simula o tempo de conexão com a API da Rede Social (redes ainda sem OAuth real)
    setTimeout(() => {
      setNetworks((prev) =>
        prev.map((n) =>
          n.id === selectedNetwork.id ? { ...n, isConnected: true } : n
        )
      );
      setIsLoading(false);
      setIsModalOpen(false);
    }, 1500);
  };

  return (
    <DashboardLayout activeTab="channels">
      <div className="space-y-8">
        
        {/* Cabeçalho */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 font-display">Minhas Conexões</h1>
          <p className="text-gray-500 mt-2">
            Gerencie as contas de redes sociais vinculadas ao HypeCerto. 
            Contas não conectadas aparecem em cinza.
          </p>
        </div>

        {/* Grade de Redes Sociais */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {networks.map((network) => (
            <div
              key={network.id}
              onClick={() => handleOpenConnect(network)}
              className={`relative flex flex-col items-center p-8 rounded-2xl border-2 transition-all duration-300 ${
                network.isConnected
                  ? "bg-white border-purple-200 shadow-sm cursor-default"
                  : "bg-gray-50 border-gray-200 hover:border-purple-300 hover:shadow-md cursor-pointer group"
              }`}
            >
              {/* Ícone de Status no canto */}
              <div className="absolute top-4 right-4">
                {network.isConnected ? (
                  <CheckCircle2 className="w-6 h-6 text-green-500" />
                ) : (
                  <Link2 className="w-5 h-5 text-gray-400 group-hover:text-purple-500 transition-colors" />
                )}
              </div>

              {/* Logo da Rede - Fica cinza se não estiver conectado */}
              <div className={`w-20 h-20 mb-4 transition-all duration-300 ${!network.isConnected && "grayscale opacity-50 group-hover:grayscale-0 group-hover:opacity-100"}`}>
                <img src={network.icon} alt={network.name} className="w-full h-full object-contain" />
              </div>

              <h3 className="text-lg font-bold text-gray-900 mb-1">{network.name}</h3>
              
              <p className="text-sm font-medium mb-6">
                {network.isConnected ? (
                  <span className="text-green-600 bg-green-50 px-3 py-1 rounded-full">Conectado</span>
                ) : (
                  <span className="text-gray-500">Não conectado</span>
                )}
              </p>

              {/* Botão Inferior */}
              {!network.isConnected ? (
                <Button 
                  variant="outline" 
                  className="w-full border-purple-200 text-purple-700 hover:bg-purple-50"
                >
                  Conectar Conta
                </Button>
              ) : (
                <Button 
                  variant="ghost" 
                  className="w-full text-gray-500 hover:text-gray-700"
                >
                  <Settings2 className="w-4 h-4 mr-2" />
                  Configurações
                </Button>
              )}
            </div>
          ))}
        </div>

        {/* Modal de Conexão e Permissões */}
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="sm:max-w-[500px] bg-white">
            <DialogHeader>
              <div className="flex items-center gap-4 mb-2">
                <div className="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center p-2">
                  {selectedNetwork && <img src={selectedNetwork.icon} alt="" className="w-full h-full object-contain" />}
                </div>
                <div>
                  <DialogTitle className="text-xl font-display">Conectar ao {selectedNetwork?.name}</DialogTitle>
                  <DialogDescription className="text-gray-500">
                    O HypeCerto precisa de permissões para automatizar seu perfil.
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            {selectedNetwork && REDES_META.has(selectedNetwork.id) ? (
              <div className="py-6 space-y-4">
                {isLoading && (
                  <div className="flex items-center gap-3 text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
                    <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
                    Aguardando login no pop-up do Facebook e verificando suas Páginas...
                  </div>
                )}
                {errorMsg && (
                  <div className="flex items-start gap-2 text-sm text-red-700 bg-red-50 p-4 rounded-lg">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <span>{errorMsg}</span>
                  </div>
                )}
                {avisos.length > 0 && (
                  <div className="flex items-start gap-2 text-sm text-amber-700 bg-amber-50 p-4 rounded-lg">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <ul className="list-disc pl-4 space-y-1">
                      {avisos.map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {!isLoading && !errorMsg && avisos.length === 0 && (
                  <p className="text-sm text-gray-500">
                    Um pop-up do Facebook vai abrir pedindo para você autorizar o HypeCerto a
                    ler suas Páginas e publicar em seu nome.
                  </p>
                )}
              </div>
            ) : (
              <div className="py-6 space-y-6">
                <div className="flex items-center gap-2 text-sm font-semibold text-purple-700 bg-purple-50 p-3 rounded-lg">
                  <ShieldCheck className="w-5 h-5" />
                  Selecione apenas o que deseja permitir:
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5 pr-4">
                    <h4 className="font-medium text-gray-900">Publicações e Agendamentos</h4>
                    <p className="text-sm text-gray-500">Permite criar, editar e agendar posts na sua conta do {selectedNetwork?.name}.</p>
                  </div>
                  <Switch
                    checked={permissions.publish}
                    onCheckedChange={(c) => setPermissions({ ...permissions, publish: c })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5 pr-4">
                    <h4 className="font-medium text-gray-900">Leitura de Métricas (Analytics)</h4>
                    <p className="text-sm text-gray-500">Coleta dados de engajamento, visualizações e alcance para seus relatórios.</p>
                  </div>
                  <Switch
                    checked={permissions.analytics}
                    onCheckedChange={(c) => setPermissions({ ...permissions, analytics: c })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5 pr-4">
                    <h4 className="font-medium text-gray-900">Mensagens e Comentários</h4>
                    <p className="text-sm text-gray-500">Permite ao bot do HypeCerto responder comentários e DMs automaticamente.</p>
                  </div>
                  <Switch
                    checked={permissions.messages}
                    onCheckedChange={(c) => setPermissions({ ...permissions, messages: c })}
                  />
                </div>
              </div>
            )}

            <DialogFooter className="gap-2 sm:gap-0">
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>
                {selectedNetwork && REDES_META.has(selectedNetwork.id) ? "Fechar" : "Cancelar"}
              </Button>
              {!(selectedNetwork && REDES_META.has(selectedNetwork.id)) && (
                <Button
                  onClick={handleConnect}
                  disabled={isLoading}
                  className="bg-purple-600 hover:bg-purple-700 text-white min-w-[140px]"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : "Autorizar e Conectar"}
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>

      </div>
    </DashboardLayout>
  );
}