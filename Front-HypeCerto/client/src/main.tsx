import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);

// Analytics (Umami) só é carregado se as variáveis estiverem definidas — evita 404 e requisições a "%VITE_...%".
const analyticsEndpoint = import.meta.env.VITE_ANALYTICS_ENDPOINT as string | undefined;
const analyticsId = import.meta.env.VITE_ANALYTICS_WEBSITE_ID as string | undefined;
if (analyticsEndpoint && analyticsId) {
  const s = document.createElement("script");
  s.defer = true;
  s.src = `${analyticsEndpoint}/umami`;
  s.setAttribute("data-website-id", analyticsId);
  document.body.appendChild(s);
}