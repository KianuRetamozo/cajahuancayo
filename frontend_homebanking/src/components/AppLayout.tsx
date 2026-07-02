import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Inicio", icon: "⌂" },
  { to: "/movimientos", label: "Movimientos", icon: "≡" },
  { to: "/solicitar-credito", label: "Créditos", icon: "＄" },
];

export default function AppLayout() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-paper flex flex-col">
      <header className="bg-rojo text-white sticky top-0 z-10">
        <div className="max-w-lg mx-auto px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-white/15 flex items-center justify-center font-bold text-sm">
              BA
            </div>
            <span className="font-bold tracking-tight">Caja Huancayo</span>
          </div>
          <button
            onClick={logout}
            className="text-xs text-white/80 hover:text-white underline underline-offset-2"
          >
            Cerrar sesión
          </button>
        </div>
      </header>
      <div className="h-1 w-full bg-gradient-to-r from-rojo via-rojo-dark to-oro" />

      <main className="flex-1 max-w-lg w-full mx-auto px-5 py-6 pb-24">
        <Outlet />
      </main>

      {/* Navegación inferior, patrón típico de apps de banca móvil */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-line">
        <div className="max-w-lg mx-auto grid grid-cols-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 py-3 text-xs font-medium transition ${
                  isActive ? "text-rojo" : "text-ink-soft"
                }`
              }
            >
              <span className="text-lg leading-none">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
