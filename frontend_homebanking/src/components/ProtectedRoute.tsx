import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { sesion, cargando } = useAuth();

  if (cargando) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-paper text-ink-soft text-sm">
        Cargando…
      </div>
    );
  }

  if (!sesion) return <Navigate to="/login" replace />;
  return <Outlet />;
}
