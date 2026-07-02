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
      // el error ya se muestra vía contexto
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="min-h-screen bg-paper flex flex-col">
      {/* Barra superior roja, patrón típico de banca municipal peruana */}
      <div className="bg-rojo text-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-white/15 flex items-center justify-center font-bold">
              BA
            </div>
            <span className="font-bold tracking-tight text-lg">Caja Huancayo</span>
          </div>
          <span className="hidden sm:block text-sm text-white/80">
            Central de ayuda &middot; 0800-10064
          </span>
        </div>
      </div>

      {/* Franja degradada roja -> oro, referencia al estilo cálido andino */}
      <div className="h-1.5 w-full bg-gradient-to-r from-rojo via-rojo-dark to-oro" />

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-6">
            <p className="text-sm font-semibold text-rojo uppercase tracking-wide">
              Banca por Internet
            </p>
            <h1 className="mt-1 text-2xl font-extrabold text-ink">
              Ingresa a tu cuenta
            </h1>
          </div>

          <div className="bg-white rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.06),0_8px_24px_rgba(0,0,0,0.05)] border border-line p-7">
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <label htmlFor="correo" className="block text-sm font-semibold text-ink mb-1.5">
                  Usuario / correo
                </label>
                <input
                  id="correo"
                  type="email"
                  required
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  placeholder="tucorreo@ejemplo.com"
                  className="w-full rounded-lg border border-line bg-paper px-3.5 py-3 text-sm outline-none focus:border-rojo focus:ring-2 focus:ring-rojo/15 transition"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-ink mb-1.5">
                  Clave de acceso
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••"
                  className="w-full rounded-lg border border-line bg-paper px-3.5 py-3 text-sm outline-none focus:border-rojo focus:ring-2 focus:ring-rojo/15 transition"
                />
              </div>

              {error && (
                <div className="rounded-lg bg-rojo-tint px-3.5 py-2.5 text-sm text-rojo-deep">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={enviando}
                className="w-full rounded-lg bg-rojo py-3 text-sm font-bold text-white hover:bg-rojo-dark disabled:opacity-60 transition"
              >
                {enviando ? "Verificando..." : "Ingresar"}
              </button>

              <p className="text-center text-xs text-ink-soft pt-1">
                ¿Olvidaste tu clave? Acércate a cualquier agencia con tu DNI.
              </p>
            </form>
          </div>

          <p className="mt-6 text-center text-xs text-ink-soft">
            Conexión segura &middot; Tus datos viajan cifrados
          </p>
        </div>
      </div>
    </div>
  );
}
