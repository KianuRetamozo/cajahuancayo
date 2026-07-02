export interface Usuario {
  id_usuario: string;
  nombre_completo: string;
  correo: string;
  rol_codigo: string;
  agencia: string | null;
}

export type RolCodigo =
  | "ASESOR"
  | "ADMINISTRADOR"
  | "JEFE_REGIONAL"
  | "RIESGOS"
  | "COMITE"
  | "GERENCIA"
  | "CLIENTE";

export interface KpiMora {
  banda_mora_actual: string;
  cantidad_creditos: number;
  monto_total_cartera: number;
  dias_atraso_promedio: number;
}
