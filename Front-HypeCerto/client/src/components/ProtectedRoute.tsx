import { useEffect, useState, type ComponentType } from "react";
import { useLocation } from "wouter";
import { API_URL, clearSession, getToken } from "@/lib/api";

/**
 * Exige sessão válida: sem token, ou com token rejeitado pelo backend (/auth/me), redireciona para /login.
 * Nada da página protegida é renderizado antes da verificação.
 */
export default function ProtectedRoute({ component: Component }: { component: ComponentType }) {
  const [, setLocation] = useLocation();
  const [ok, setOk] = useState(false);

  useEffect(() => {
    let vivo = true;
    const token = getToken();
    if (!token) { setLocation("/login"); return; }
    fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => {
        if (!vivo) return;
        if (r.ok) setOk(true);
        else { clearSession(); setLocation("/login"); }
      })
      .catch(() => { if (vivo) { clearSession(); setLocation("/login"); } });
    return () => { vivo = false; };
  }, [setLocation]);

  return ok ? <Component /> : null;
}
