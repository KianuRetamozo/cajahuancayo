import { useState, type FormEvent } from "react";

export default function SolicitarCredito() {
  const [enviado, setEnviado] = useState(false);
  const [monto, setMonto] = useState("");
  const [plazo, setPlazo] = useState("12");

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    // Cuando el backend exponga POST /solicitudes, esto llamará a la API real
    // con canal_origen: "HOMEBANKING" — la pieza que cierra el Criterio 1.
    setEnviado(true);
  }

  if (enviado) {
    return (
      <div className="text-center py-10">
        <div className="mx-auto h-14 w-14 rounded-full bg-verde-tint text-verde flex items-center justify-center text-2xl">
          ✓
        </div>
        <h1 className="mt-4 text-lg font-extrabold text-ink">Solicitud enviada</h1>
        <p className="mt-1.5 text-sm text-ink-soft max-w-xs mx-auto">
          Tu asesor evaluará la solicitud de S/ {monto || "0"} a {plazo} meses.
          Te avisaremos aquí cuando haya una decisión.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-xl font-extrabold text-ink">Solicitar crédito</h1>
      <p className="text-sm text-ink-soft mt-1">
        Cuéntanos cuánto necesitas y en cuántos meses quieres pagarlo.
      </p>

      <form onSubmit={onSubmit} className="mt-6 space-y-5">
        <div>
          <label className="block text-sm font-semibold text-ink mb-1.5">
            Monto solicitado
          </label>
          <div className="relative">
            <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-soft text-sm">
              S/
            </span>
            <input
              type="number"
              required
              min={500}
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              placeholder="5,000"
              className="w-full rounded-lg border border-line bg-white pl-9 pr-3.5 py-3 text-sm outline-none focus:border-rojo focus:ring-2 focus:ring-rojo/15 transition"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-ink mb-1.5">
            Plazo
          </label>
          <select
            value={plazo}
            onChange={(e) => setPlazo(e.target.value)}
            className="w-full rounded-lg border border-line bg-white px-3.5 py-3 text-sm outline-none focus:border-rojo focus:ring-2 focus:ring-rojo/15 transition"
          >
            <option value="6">6 meses</option>
            <option value="12">12 meses</option>
            <option value="24">24 meses</option>
            <option value="36">36 meses</option>
          </select>
        </div>

        <button
          type="submit"
          className="w-full rounded-lg bg-rojo py-3 text-sm font-bold text-white hover:bg-rojo-dark transition"
        >
          Enviar solicitud
        </button>
      </form>
    </div>
  );
}
