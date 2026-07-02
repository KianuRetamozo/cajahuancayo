import { Link } from "react-router-dom";
import { useMiCuenta } from "../lib/useMiCuenta";
import { FilaMovimiento } from "../components/FilaMovimiento";

const ACCESOS_RAPIDOS = [
  { to: "/movimientos", label: "Transferir", icon: "⇄" },
  { to: "/movimientos", label: "Pagar servicios", icon: "▤" },
  { to: "/solicitar-credito", label: "Solicitar crédito", icon: "＄" },
  { to: "/movimientos", label: "Recargar celular", icon: "▭" },
];

export default function Inicio() {
  const { data, isLoading, isError } = useMiCuenta();
  const cuenta = data?.cuentas?.[0];

  return (
    <div>
      {isLoading && <p className="text-sm text-ink-soft">Cargando tu cuenta…</p>}

      {isError && (
        <div className="rounded-lg bg-rojo-tint px-4 py-3 text-sm text-rojo-deep">
          No pudimos cargar tu información. Intenta de nuevo en unos segundos.
        </div>
      )}

      {data && (
        <>
          <p className="text-sm text-ink-soft">Hola,</p>
          <h1 className="text-xl font-extrabold text-ink -mt-0.5">
            {data.nombres.split(" ")[0]} {data.apellidos.split(" ")[0]}
          </h1>

          {/* Tarjeta de saldo, degradado rojo institucional */}
          {cuenta && (
            <div className="mt-5 rounded-2xl bg-gradient-to-br from-rojo to-rojo-deep text-white p-6 shadow-lg shadow-rojo/20">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider text-white/70">
                  Cuenta de ahorros
                </span>
                <span className="text-xs font-mono text-white/70">
                  N° {cuenta.numero_cuenta}
                </span>
              </div>
              <div className="mt-4 font-mono text-3xl font-bold tracking-tight">
                S/ {cuenta.saldo_disponible.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
              </div>
              <div className="mt-1 text-xs text-white/60">Saldo disponible</div>
            </div>
          )}

          {/* Accesos rápidos: patrón estándar de apps de banca peruana */}
          <div className="mt-6 grid grid-cols-4 gap-3">
            {ACCESOS_RAPIDOS.map((a) => (
              <Link
                key={a.label}
                to={a.to}
                className="flex flex-col items-center gap-2 text-center group"
              >
                <div className="h-14 w-14 rounded-2xl bg-white border border-line flex items-center justify-center text-xl text-rojo group-hover:border-rojo/40 group-hover:bg-rojo-tint transition">
                  {a.icon}
                </div>
                <span className="text-[11px] leading-tight text-ink-soft">{a.label}</span>
              </Link>
            ))}
          </div>

          {/* Aviso de elegibilidad, conecta con el criterio de "sujeto de crédito" */}
          {data.es_sujeto_credito && (
            <Link
              to="/solicitar-credito"
              className="mt-6 flex items-center justify-between rounded-xl bg-oro-tint border border-oro/30 px-4 py-3.5"
            >
              <div>
                <div className="text-sm font-semibold text-ink">Tienes un crédito preaprobado</div>
                <div className="text-xs text-ink-soft mt-0.5">Revisa las condiciones y solicítalo</div>
              </div>
              <span className="text-rojo text-lg">→</span>
            </Link>
          )}

          <div className="mt-8 flex items-center justify-between">
            <h2 className="font-bold text-ink">Movimientos recientes</h2>
            <Link to="/movimientos" className="text-xs font-semibold text-rojo">
              Ver todos
            </Link>
          </div>

          <div className="mt-2 rounded-2xl bg-white border border-line px-4">
            {cuenta && cuenta.movimientos.length > 0 ? (
              cuenta.movimientos.slice(0, 4).map((m) => <FilaMovimiento key={m.id_movimiento} mov={m} />)
            ) : (
              <p className="py-6 text-center text-sm text-ink-soft">
                Aún no tienes movimientos.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
