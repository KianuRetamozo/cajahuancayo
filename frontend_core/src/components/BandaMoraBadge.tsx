const ESTILOS: Record<string, { bg: string; fg: string; label: string }> = {
  VIGENTE: { bg: "bg-verde-dim", fg: "text-verde", label: "Vigente" },
  PREVENTIVA: { bg: "bg-ambar-dim", fg: "text-ambar", label: "Preventiva" },
  TEMPRANA: { bg: "bg-ambar-dim", fg: "text-[#B8791F]", label: "Temprana" },
  TARDIA: { bg: "bg-rojo-dim", fg: "text-rojo", label: "Tardía" },
  JUDICIAL: { bg: "bg-rojo-dim", fg: "text-rojo", label: "Judicial" },
  CASTIGO: { bg: "bg-noche", fg: "text-paper", label: "Castigo" },
};

export function BandaMoraBadge({ banda }: { banda: string }) {
  const estilo = ESTILOS[banda] ?? { bg: "bg-paper-dim", fg: "text-ink-soft", label: banda };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${estilo.bg} ${estilo.fg}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {estilo.label}
    </span>
  );
}
