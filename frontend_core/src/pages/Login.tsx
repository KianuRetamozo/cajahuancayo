import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setEnviando(true);
    try {
      await login(correo, password);
      navigate("/");
    } catch {
      // el mensaje de error ya se muestra vía contexto
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-[1.1fr_1fr]">
      {/* Panel de marca */}
      <div className="relative hidden lg:flex flex-col justify-between overflow-hidden bg-noche px-14 py-12 text-paper">
        <div className="absolute inset-0 opacity-[0.07]" style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
          backgroundSize: "28px 28px",
        }} />

        <div className="relative z-10">
          <div className="flex items-center gap-2 text-sm tracking-[0.2em] uppercase text-terracota-soft">
            <span className="h-2 w-2 rounded-full bg-terracota" />
            Sistema Core Financiero
          </div>
        </div>

        <div className="relative z-10 max-w-md">
          <h1 className="font-[family-name:var(--font-display)] text-5xl leading-[1.05] font-medium">
            Caja Huancayo
          </h1>
          <p className="mt-5 text-lg text-paper/70 leading-relaxed">
            Un solo sistema, de punta a punta: desde la solicitud del cliente
            hasta el desembolso y la gestión de cartera.
          </p>

          {/* Firma visual: el semáforo de riesgo como elemento ambiental */}
          <div className="mt-10 flex items-center gap-3">
            <div className="flex -space-x-1">
              <span className="h-3 w-3 rounded-full bg-verde ring-2 ring-noche" />
              <span className="h-3 w-3 rounded-full bg-ambar ring-2 ring-noche" />
              <span className="h-3 w-3 rounded-full bg-rojo ring-2 ring-noche" />
            </div>
            <p className="text-sm text-paper/60">
              Cada crédito, clasificado en tiempo real por su nivel de riesgo.
            </p>
          </div>
        </div>

        <p className="relative z-10 text-xs text-paper/40">
          postgres &middot; Core + Homebanking integrados
        </p>
      </div>

      {/* Panel de formulario */}
      <div className="flex items-center justify-center px-6 py-16 bg-paper">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-8">
            <h1 className="font-[family-name:var(--font-display)] text-3xl font-medium text-noche">
              Caja Huancayo
            </h1>
          </div>

          <h2 className="font-[family-name:var(--font-display)] text-2xl font-medium text-ink">
            Ingresar al sistema
          </h2>
          <p className="mt-1.5 text-sm text-ink-soft">
            Usa las credenciales de tu rol asignado.
          </p>

          <form onSubmit={onSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="correo" className="block text-sm font-medium text-ink mb-1.5">
                Correo institucional
              </label>
              <input
                id="correo"
                type="email"
                required
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                placeholder="nombre.rol@bancoandino.pe"
                className="w-full rounded-lg border border-ink/15 bg-white px-3.5 py-2.5 text-sm text-ink outline-none focus:border-terracota focus:ring-2 focus:ring-terracota/20 transition"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ink mb-1.5">
                Contraseña
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••"
                className="w-full rounded-lg border border-ink/15 bg-white px-3.5 py-2.5 text-sm text-ink outline-none focus:border-terracota focus:ring-2 focus:ring-terracota/20 transition"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-rojo-dim px-3.5 py-2.5 text-sm text-rojo">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded-lg bg-noche py-2.5 text-sm font-medium text-paper hover:bg-noche-soft disabled:opacity-60 transition"
            >
              {enviando ? "Verificando..." : "Ingresar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
