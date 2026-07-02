export interface Movimiento {
  id_movimiento: string;
  tipo_movimiento: string;
  monto: number;
  saldo_posterior: number;
  canal_origen: string;
  descripcion: string | null;
  creado_en: string;
}

export interface Cuenta {
  id_cuenta: string;
  numero_cuenta: string;
  tipo_cuenta: string;
  moneda: string;
  saldo_disponible: number;
  estado: string;
  movimientos: Movimiento[];
}

export interface MiCuenta {
  nombres: string;
  apellidos: string;
  numero_documento: string;
  es_sujeto_credito: boolean;
  cuentas: Cuenta[];
}
