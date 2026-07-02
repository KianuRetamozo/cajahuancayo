import type { Movimiento } from "../lib/types";

const ES_INGRESO = new Set(["DEPOSITO", "DESEMBOLSO_CREDITO"]);

const ETIQUETAS: Record<string, string> = {
  DEPOSITO: "Depósito",
  RETIRO: "Retiro",
  DESEMBOLSO_CREDITO: "Desembolso de crédito",
  PAGO_CUOTA: "Pago de cuota",
  CARGO_MORA: "Cargo por mora",
  AJUSTE: "Ajuste",
};

export function FilaMovimiento({ mov }: { mov: Movimiento }) {
  const esIngreso = ES_INGRESO.has(mov.tipo_movimiento);
  const fecha = new Date(mov.creado_en).toLocaleDateString("es-PE", {
    day: "2-digit",
    month: "short",
  });

  return (
    <div className="flex items-center justify-between py-3 border-b border-line last:border-0">
      <div className="flex items-center gap-3 min-w-0">
        <div
          className={`h-9 w-9 shrink-0 rounded-full flex items-center justify-center text-sm font-bold ${
            esIngreso ? "bg-verde-tint text-verde" : "bg-rojo-tint text-rojo"
          }`}
        >
          {esIngreso ? "↓" : "↑"}
        </div>
        <div className="min-w-0">
          <div className="text-sm font-medium text-ink truncate">
            {mov.descripcion || ETIQUETAS[mov.tipo_movimiento] || mov.tipo_movimiento}
          </div>
          <div className="text-xs text-ink-soft">
            {fecha} · {mov.canal_origen === "HOMEBANKING" ? "Homebanking" : mov.canal_origen === "CORE" ? "Core" : "Agencia"}
          </div>
        </div>
      </div>
      <div className={`font-mono text-sm font-semibold shrink-0 ${esIngreso ? "text-verde" : "text-ink"}`}>
        {esIngreso ? "+" : "−"} S/ {mov.monto.toLocaleString("es-PE", { minimumFractionDigits: 2 })}
      </div>
    </div>
  );
}
