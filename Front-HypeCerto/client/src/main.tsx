import { trpc } from "@/lib/trpc";
import { UNAUTHED_ERR_MSG } from '@shared/const';
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { httpBatchLink, TRPCClientError } from "@trpc/client";
import { createRoot } from "react-dom/client";
import superjson from "superjson";
import App from "./App";
import { getLoginUrl } from "./const";
import "./index.css";

// ==============================
// 🔥 FIELD MAPPING
// ==============================
const fieldMap: Record<string, string> = {
  nome: "name",
  criado_em: "createdAt",
  atualizado_em: "updatedAt",
  telefone: "phone",
  foto_perfil: "profilePicture",
  ativo: "isActive",
  conteudo: "content",
  titulo: "title",
  projeto_id: "projectId",
  status_envio: "status",
};

const reverseFieldMap = Object.fromEntries(
  Object.entries(fieldMap).map(([k, v]) => [v, k])
);

const isObject = (val: any) =>
  val && typeof val === "object" && !Array.isArray(val);

const toSnake = (str: string) =>
  str.replace(/[A-Z]/g, (l) => "_" + l.toLowerCase());

const toCamel = (str: string) =>
  str.replace(/_([a-z])/g, (_, l) => l.toUpperCase());

const mapRequest = (data: any): any => {
  if (Array.isArray(data)) return data.map(mapRequest);

  if (isObject(data)) {
    return Object.fromEntries(
      Object.entries(data).map(([k, v]) => [
        reverseFieldMap[k] || toSnake(k),
        mapRequest(v),
      ])
    );
  }

  return data;
};

const mapResponse = (data: any): any => {
  if (Array.isArray(data)) return data.map(mapResponse);

  if (isObject(data)) {
    return Object.fromEntries(
      Object.entries(data).map(([k, v]) => [
        fieldMap[k] || toCamel(k),
        mapResponse(v),
      ])
    );
  }

  return data;
};

// ==============================
// 🔥 REACT QUERY
// ==============================
const queryClient = new QueryClient();

const redirectToLoginIfUnauthorized = (error: unknown) => {
  if (!(error instanceof TRPCClientError)) return;
  if (typeof window === "undefined") return;

  const isUnauthorized = error.message === UNAUTHED_ERR_MSG;

  if (!isUnauthorized) return;

  window.location.href = getLoginUrl();
};

queryClient.getQueryCache().subscribe(event => {
  if (event.type === "updated" && event.action.type === "error") {
    const error = event.query.state.error;
    redirectToLoginIfUnauthorized(error);
    console.error("[API Query Error]", error);
  }
});

queryClient.getMutationCache().subscribe(event => {
  if (event.type === "updated" && event.action.type === "error") {
    const error = event.mutation.state.error;
    redirectToLoginIfUnauthorized(error);
    console.error("[API Mutation Error]", error);
  }
});

// ==============================
// 🔥 TRPC CLIENT (COM INTERCEPTOR)
// ==============================
const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: "/api/trpc",
      transformer: superjson,

      async fetch(input, init) {
        // 🟡 FRONT → BACK (request)
        if (init?.body) {
          try {
            const body = JSON.parse(init.body as string);
            init.body = JSON.stringify(mapRequest(body));
          } catch {}
        }

        const res = await globalThis.fetch(input, {
          ...(init ?? {}),
          credentials: "include",
        });

        // 🟢 BACK → FRONT (response)
        try {
          const data = await res.json();
          const mapped = mapResponse(data);

          return new Response(JSON.stringify(mapped), {
            headers: res.headers,
            status: res.status,
          });
        } catch {
          return res;
        }
      },
    }),
  ],
});

// ==============================
// 🔥 RENDER
// ==============================
createRoot(document.getElementById("root")!).render(
  <trpc.Provider client={trpcClient} queryClient={queryClient}>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </trpc.Provider>
);