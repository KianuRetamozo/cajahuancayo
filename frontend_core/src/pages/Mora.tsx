import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import type { KpiMora } from "../lib/types";
import { BandaMoraBadge } from "../components/BandaMoraBadge";

const ORDEN_BANDAS = ["PREVENTIVA", "TEMPRANA", "TARDIA", "JUDICIAL", "CASTIGO"];

export default function Mora() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["mora-kpis"],
    queryFn: async () => {
      const { data } = await api.get<KpiMora[]>("/mora/kpis");
      return data;
    },
  });

  return (
    <div>
      <p className="text-sm uppercase tracking-wider text-terracota font-medium">
        R1 · Consulta por bandas
      </p>
      <h1 className="mt-1 font-[family-name:var(--font-display)] text-3xl font-medium text-ink">
        Recuperaciones / Mora
      </h1>

      {isLoading && (
        <p className="mt-8 text-sm text-ink-soft">Cargando cartera…</p>
      )}

      {isError && (
        <div className="mt-8 rounded-lg bg-rojo-dim px-4 py-3 text-sm text-rojo">
          No se pudo cargar la cartera. {(error as any)?.response?.data?.detail ?? ""}
        </div>
      )}

      {data && data.length === 0 && (
        <div className="mt-8 rounded-xl border border-dashed border-ink/15 bg-white px-6 py-10 text-center">
          <p className="text-ink font-medium">Todavía no hay créditos en mora</p>
          <p className="mt-1 text-sm text-ink-soft">
            En cuanto existan créditos desembolsados con cuotas vencidas,
            aparecerán aquí clasificados por banda.
          </p>
        </div>
      )}

      {data && data.length > 0 && (
        <div className="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ORDEN_BANDAS.map((banda) => {
            const kpi = data.find((d) => d.banda_mora_actual === banda);
            return (
              <div
                key={banda}
                className="rounded-xl border border-ink/10 bg-white p-5"
              >
                <BandaMoraBadge banda={banda} />
                <div className="mt-3 font-mono text-2xl text-ink">
                  {kpi?.cantidad_creditos ?? 0}
                </div>
                <div className="text-xs text-ink-soft">créditos en esta banda</div>

                <div className="mt-4 pt-4 border-t border-ink/10 space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-soft">Cartera</span>
                    <span className="font-mono text-ink">
                      S/ {(kpi?.monto_total_cartera ?? 0).toLocaleString("es-PE")}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ink-soft">Atraso promedio</span>
                    <span className="font-mono text-ink">
                      {kpi?.dias_atraso_promedio ?? 0} días
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
