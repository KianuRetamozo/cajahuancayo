import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "../lib/api";
import type { Usuario } from "../lib/types";

interface AuthContextValue {
  usuario: Usuario | null;
  cargando: boolean;
  error: string | null;
  login: (correo: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function cargarPerfil() {
    try {
      const { data } = await api.get<Usuario>("/auth/me");
      setUsuario(data);
    } catch {
      setUsuario(null);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      cargarPerfil();
    } else {
      setCargando(false);
    }
  }, []);

  async function login(correo: string, password: string) {
    setError(null);
    try {
      const { data } = await api.post("/auth/login", { correo, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      await cargarPerfil();
    } catch (e: any) {
      const mensaje = e.response?.data?.detail || "No se pudo iniciar sesión";
      setError(mensaje);
      throw e;
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
