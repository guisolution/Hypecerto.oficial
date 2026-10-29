/**
 * lib/api.ts — ponto único para URL da API e sessão.
 * Configure VITE_API_URL no .env do front (ex.: https://api.seudominio.com).
 */
export const API_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

export const getToken = () => {
  try { return localStorage.getItem("token"); } catch { return null; }
};

/** Remove TODOS os dados de sessão do navegador. */
export const clearSession = () => {
  try {
    ["token", "user", "projectData", "manus-runtime-user-info"].forEach((k) => localStorage.removeItem(k));
  } catch { /* storage indisponível */ }
};

/** fetch autenticado: envia o Bearer e, em 401, encerra a sessão e volta ao login. */
export async function authFetch(path: string, init: RequestInit = {}) {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { ...(init.headers || {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  if (res.status === 401) {
    clearSession();
    if (window.location.pathname !== "/login") window.location.href = "/login";
  }
  return res;
}
