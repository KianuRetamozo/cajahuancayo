import { useState, useEffect } from 'react';

// Interfaces para TypeScript
interface Solicitud {
  id_solicitud: string;
  monto_solicitado: number;
  plazo_meses: number;
  estado: string;
  creado_en: string;
}

export default function Creditos() {
  const [solicitudes, setSolicitudes] = useState<Solicitud[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  // Nuevos estados para el Modal de Evaluación
  const [solicitudActiva, setSolicitudActiva] = useState<Solicitud | null>(null);
  const [decision, setDecision] = useState('');
  const [comentario, setComentario] = useState('');

  useEffect(() => {
    obtenerSolicitudes();
  }, []);

 const obtenerSolicitudes = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fíjate en la comilla invertida al inicio y al final de la URL
      const respuesta = await fetch(`${import.meta.env.VITE_API_URL}/solicitudes/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (respuesta.ok) {
        const data = await respuesta.json();
        setSolicitudes(data);
      } else {
        setError('No tienes permisos o la sesión expiró.');
      }
    } catch (err) {
      setError('Error de conexión con el servidor.');
    } finally {
      setCargando(false);
    }
  };

  // Función para enviar la decisión al backend
  const enviarEvaluacion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!solicitudActiva) return;

    try {
      const token = localStorage.getItem('token');
      
      const paqueteOpinion = {
        decision: decision,
        comentario: comentario || null
      };

      // Aquí sí va el ID dinámico y la palabra "opinar" al final
      const respuesta = await fetch(`${import.meta.env.VITE_API_URL}/solicitudes/${solicitudActiva.id_solicitud}/opinar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
         },
           body: JSON.stringify(paqueteOpinion)
      });

      if (respuesta.ok) {
        alert("¡Solicitud evaluada correctamente!");
        setSolicitudActiva(null); // Cerramos el modal
        setDecision('');
        setComentario('');
        obtenerSolicitudes(); // Recargamos la tabla para ver el nuevo estado
      } else {
        const errorData = await respuesta.json();
        alert(`Error al evaluar: ${errorData.detail}`);
      }
    } catch (error) {
      alert("Error de conexión al enviar la evaluación.");
    }
  };

  return (
    <div className="relative">
      <p className="text-sm uppercase tracking-wider text-[#D95A38] font-medium">Criterio 1 y 2</p>
      <h1 className="mt-1 text-3xl font-medium text-gray-900 mb-8">Gestión de Solicitudes</h1>
      
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {cargando ? (
          <div className="p-8 text-center text-gray-500">Cargando solicitudes...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">{error}</div>
        ) : solicitudes.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No hay solicitudes pendientes.</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-sm text-gray-500">
                <th className="p-4 font-medium">ID Solicitud</th>
                <th className="p-4 font-medium">Monto (S/)</th>
                <th className="p-4 font-medium">Plazo</th>
                <th className="p-4 font-medium">Estado</th>
                <th className="p-4 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody>
              {solicitudes.map((sol) => (
                <tr key={sol.id_solicitud} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="p-4 font-mono text-xs text-gray-500">{sol.id_solicitud.substring(0, 8)}...</td>
                  <td className="p-4 font-medium text-gray-900">S/ {sol.monto_solicitado.toFixed(2)}</td>
                  <td className="p-4 text-sm text-gray-900">{sol.plazo_meses} meses</td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded text-xs font-medium uppercase bg-yellow-100 text-yellow-800">
                      {sol.estado}
                    </span>
                  </td>
                  <td className="p-4">
                    <button 
                      onClick={() => setSolicitudActiva(sol)}
                      className="text-sm bg-[#D95A38]/10 text-[#D95A38] hover:bg-[#D95A38] hover:text-white px-3 py-1.5 rounded transition-colors"
                    >
                      Evaluar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* MODAL DE EVALUACIÓN */}
      {solicitudActiva && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
            <h2 className="text-xl font-medium mb-4 text-gray-900">Evaluar Solicitud</h2>
            <p className="text-sm text-gray-500 mb-6">
              Monto: <strong>S/ {solicitudActiva.monto_solicitado.toFixed(2)}</strong> a {solicitudActiva.plazo_meses} meses.
            </p>
            
            <form onSubmit={enviarEvaluacion} className="flex flex-col gap-4">
              <div>
                <label className="text-sm font-semibold text-gray-900 block mb-2">Decisión Final</label>
                <select 
                  value={decision} 
                  onChange={(e) => setDecision(e.target.value)}
                  className="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-[#D95A38] focus:border-[#D95A38] outline-none"
                  required
                >
                  <option value="">-- Selecciona --</option>
                  <option value="APROBADO">Aprobar Crédito</option>
                  <option value="RECHAZADO">Rechazar Crédito</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-900 block mb-2">Comentario (Opcional)</label>
                <textarea 
                  value={comentario} 
                  onChange={(e) => setComentario(e.target.value)}
                  className="w-full border border-gray-300 p-2.5 rounded-lg focus:ring-[#D95A38] focus:border-[#D95A38] outline-none resize-none"
                  rows={3}
                  placeholder="Justificación de la decisión..."
                />
              </div>

              <div className="flex gap-3 mt-4">
                <button 
                  type="button" 
                  onClick={() => setSolicitudActiva(null)}
                  className="flex-1 bg-gray-100 text-gray-700 py-2.5 rounded-lg font-medium hover:bg-gray-200"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="flex-1 bg-[#D95A38] text-white py-2.5 rounded-lg font-medium hover:bg-[#c24a2c]"
                >
                  Guardar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}