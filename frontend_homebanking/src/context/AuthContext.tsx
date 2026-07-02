import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "../lib/api";

interface SesionCliente {
  correo: string;
}

interface AuthContextValue {
  sesion: SesionCliente | null;
  cargando: boolean;
  error: string | null;
  login: (correo: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<SesionCliente | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const correo = localStorage.getItem("correo_sesion");
    if (token && correo) {
      setSesion({ correo });
    }
    setCargando(false);
  }, []);

  async function login(correo: string, password: string) {
    setError(null);
    try {
      const { data } = await api.post("/auth/login", { correo, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("correo_sesion", correo);
      setSesion({ correo });
    } catch (e: any) {
      setError(e.response?.data?.detail || "No se pudo iniciar sesión");
      throw e;
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("correo_sesion");
    setSesion(null);
  }

  return (
    <AuthContext.Provider value={{ sesion, cargando, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
