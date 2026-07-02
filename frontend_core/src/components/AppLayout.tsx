import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Resumen", icon: "🔹" },
  { to: "/clientes", label: "Gestión de Clientes", icon: "👥" },
  { to: "/cuentas", label: "Cuentas y Depósitos", icon: "💳" },
  { to: "/creditos", label: "Solicitudes de crédito", icon: "📋" },
  { to: "/desembolsos", label: "Desembolsos", icon: "💰" },
  { to: "/mora", label: "Recuperaciones / Mora", icon: "⏱" },
  { to: "/configuracion", label: "Motor de Riesgos", icon: "⚙️" },
];

const ROL_LABELS: Record<string, string> = {
  ASESOR: "Asesor de negocios",
  ADMINISTRADOR: "Administrador de agencia",
  JEFE_REGIONAL: "Jefe Regional",
  RIESGOS: "Analista de Riesgos",
  COMITE: "Comité de Créditos",
  GERENCIA: "Gerencia",
  CLIENTE: "Cliente",
};

export default function AppLayout() {
  const { usuario, logout } = useAuth();

  return (
    <div className="min-h-screen flex bg-paper">
      <aside className="w-64 shrink-0 bg-noche text-paper flex flex-col">
        <div className="px-6 py-6 border-b border-noche-line">
          <span className="font-[family-name:var(--font-display)] text-xl font-medium">
            Caja Huancayo
          </span>
          <div className="mt-1 text-[11px] uppercase tracking-wider text-paper/40">
            Panel Core
          </div>
        </div>

        <nav className="flex-1 px-3 py-5 space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
                  isActive
                    ? "bg-terracota text-white"
                    : "text-paper/70 hover:bg-noche-soft hover:text-paper"
                }`
              }
            >
              <span className="text-base leading-none">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-noche-line">
          <button
            onClick={logout}
            className="w-full rounded-lg px-3 py-2.5 text-left text-sm text-paper/60 hover:bg-noche-soft hover:text-paper transition"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 shrink-0 border-b border-ink/10 bg-white/60 backdrop-blur px-8 flex items-center justify-between">
          <div className="text-sm text-ink-soft font-mono">postgres</div>
          {usuario && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-medium text-ink">{usuario.nombre_completo}</div>
                <div className="text-xs text-ink-soft">
                  {ROL_LABELS[usuario.rol_codigo] ?? usuario.rol_codigo}
                  {usuario.agencia ? ` · ${usuario.agencia}` : ""}
                </div>
              </div>
              <div className="h-9 w-9 rounded-full bg-terracota-dim text-terracota flex items-center justify-center font-medium font-[family-name:var(--font-display)]">
                {usuario.nombre_completo.charAt(0)}
              </div>
            </div>
          )}
        </header>

        <main className="flex-1 overflow-y-auto px-8 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
