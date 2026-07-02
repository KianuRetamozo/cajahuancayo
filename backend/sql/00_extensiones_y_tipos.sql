-- ============================================================
-- 00_extensiones_y_tipos.sql
-- Base de datos: bd_core_financiero
-- Extensiones y tipos enumerados usados en todo el esquema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Estados del flujo de solicitud de crédito (Criterio 2)
CREATE TYPE estado_solicitud AS ENUM (
    'PENDIENTE',
    'EN_EVALUACION',
    'OPINION_ADMINISTRADOR',
    'OPINION_JEFE_REGIONAL',
    'OPINION_RIESGOS',
    'COMITE',
    'APROBADA',
    'RECHAZADA',
    'DESEMBOLSADA',
    'ANULADA'
);

-- Semáforo del RDS (Ratio de Endeudamiento / Deuda-Ingreso)
CREATE TYPE semaforo_rds AS ENUM ('VERDE', 'AMARILLO', 'ROJO');

-- Bandas de mora (Criterio 4)
CREATE TYPE banda_mora AS ENUM (
    'VIGENTE',      -- 0 días
    'PREVENTIVA',   -- 1-30 días
    'TEMPRANA',     -- 31-60 días
    'TARDIA',       -- 61-120 días
    'JUDICIAL',     -- 121-180 días
    'CASTIGO'       -- >180 días
);

CREATE TYPE estado_credito AS ENUM (
    'VIGENTE', 'EN_MORA', 'JUDICIAL', 'CASTIGADO', 'CANCELADO'
);

-- Canal por el que se originó una acción (para trazar integración Core<->Homebanking, Criterio 1)
CREATE TYPE canal_origen AS ENUM ('HOMEBANKING', 'AGENCIA', 'CORE', 'SISTEMA');

CREATE TYPE tipo_movimiento AS ENUM (
    'DEPOSITO', 'RETIRO', 'DESEMBOLSO_CREDITO', 'PAGO_CUOTA', 'CARGO_MORA', 'AJUSTE'
);

CREATE TYPE tipo_gestion_cobranza AS ENUM (
    'LLAMADA', 'SMS', 'EMAIL', 'VISITA', 'CARTA_NOTARIAL', 'ACUERDO_PAGO'
);

CREATE TYPE resultado_gestion AS ENUM (
    'CONTACTADO', 'NO_CONTACTADO', 'PROMESA_PAGO', 'PAGO_REALIZADO', 'SE_NIEGA_PAGAR', 'NUMERO_INVALIDO'
);
