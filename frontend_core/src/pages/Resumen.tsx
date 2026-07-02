import { useAuth } from "../context/AuthContext";

export default function Resumen() {
  const { usuario } = useAuth();

  return (
    <div className="max-w-3xl">
      <p className="text-sm uppercase tracking-wider text-terracota font-medium">
        Bienvenido
      </p>
      <h1 className="mt-1 font-[family-name:var(--font-display)] text-3xl font-medium text-ink">
        {usuario?.nombre_completo}
      </h1>
      <p className="mt-3 text-ink-soft leading-relaxed">
        Este panel opera sobre la misma base de datos que el Homebanking:
        cualquier solicitud de crédito que un cliente inicie ahí, aparece
        aquí lista para evaluación.
      </p>

      <div className="mt-8 grid sm:grid-cols-2 gap-4">
        <a
          href="/creditos"
          className="block rounded-xl border border-ink/10 bg-white p-5 hover:border-terracota/40 transition"
        >
          <div className="text-terracota text-lg">▤</div>
          <div className="mt-2 font-medium text-ink">Solicitudes de crédito</div>
          <p className="mt-1 text-sm text-ink-soft">
            Revisa el flujo desde elegibilidad hasta desembolso.
          </p>
        </a>
        <a
          href="/mora"
          className="block rounded-xl border border-ink/10 bg-white p-5 hover:border-terracota/40 transition"
        >
          <div className="text-terracota text-lg">◔</div>
          <div className="mt-2 font-medium text-ink">Recuperaciones / Mora</div>
          <p className="mt-1 text-sm text-ink-soft">
            Cartera clasificada por banda, con gestiones de cobranza.
          </p>
        </a>
      </div>
    </div>
  );
}
