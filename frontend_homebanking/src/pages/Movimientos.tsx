import { useMiCuenta } from "../lib/useMiCuenta";
import { FilaMovimiento } from "../components/FilaMovimiento";

export default function Movimientos() {
  const { data, isLoading } = useMiCuenta();
  const cuenta = data?.cuentas?.[0];

  return (
    <div>
      <h1 className="text-xl font-extrabold text-ink">Movimientos</h1>
      <p className="text-sm text-ink-soft mt-1">
        Cuenta {cuenta?.numero_cuenta ?? "—"}
      </p>

      {isLoading && <p className="mt-6 text-sm text-ink-soft">Cargando…</p>}

      <div className="mt-4 rounded-2xl bg-white border border-line px-4">
        {cuenta && cuenta.movimientos.length > 0 ? (
          cuenta.movimientos.map((m) => <FilaMovimiento key={m.id_movimiento} mov={m} />)
        ) : (
          <p className="py-8 text-center text-sm text-ink-soft">Sin movimientos todavía.</p>
        )}
      </div>
    </div>
  );
}
