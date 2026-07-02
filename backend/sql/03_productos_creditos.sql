-- ============================================================
-- 03_productos_creditos.sql
-- Productos de crédito, solicitudes, scoring y RDS (Criterio 2)
-- ============================================================

CREATE TABLE productos_credito (
    id_producto         SERIAL PRIMARY KEY,
    codigo              VARCHAR(20) NOT NULL UNIQUE,   -- ej: 'CONSUMO', 'MYPE'
    nombre              VARCHAR(100) NOT NULL,
    tasa_interes_anual  NUMERIC(5,2) NOT NULL,          -- TEA %
    monto_minimo        NUMERIC(12,2) NOT NULL,
    monto_maximo        NUMERIC(12,2) NOT NULL,
    plazo_min_meses     INTEGER NOT NULL,
    plazo_max_meses     INTEGER NOT NULL,
    activo              BOOLEAN NOT NULL DEFAULT TRUE
);

-- La solicitud nace en Homebanking (o Agencia) y "viaja" por todo el flujo del Core.
-- El campo canal_origen + estado son la evidencia de la integración (Criterio 1).
CREATE TABLE solicitudes_credito (
    id_solicitud        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_cliente          UUID NOT NULL REFERENCES clientes(id_cliente),
    id_producto         INTEGER NOT NULL REFERENCES productos_credito(id_producto),
    monto_solicitado    NUMERIC(12,2) NOT NULL,
    plazo_meses         INTEGER NOT NULL,
    canal_origen        canal_origen NOT NULL DEFAULT 'HOMEBANKING',
    estado              estado_solicitud NOT NULL DEFAULT 'PENDIENTE',
    id_asesor_asignado  UUID REFERENCES usuarios(id_usuario),
    motivo_rechazo      TEXT,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_solicitudes_cliente ON solicitudes_credito(id_cliente);
CREATE INDEX idx_solicitudes_estado ON solicitudes_credito(estado);

-- Scoring crediticio calculado para una solicitud
CREATE TABLE scoring_crediticio (
    id_scoring          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_solicitud        UUID NOT NULL UNIQUE REFERENCES solicitudes_credito(id_solicitud) ON DELETE CASCADE,
    puntaje             INTEGER NOT NULL CHECK (puntaje BETWEEN 0 AND 1000),
    historial_pagos     INTEGER NOT NULL DEFAULT 0,     -- sub-puntaje
    antiguedad_laboral  INTEGER NOT NULL DEFAULT 0,
    endeudamiento_actual NUMERIC(12,2) NOT NULL DEFAULT 0,
    calculado_en        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Evaluación RDS (Ratio Deuda/Ingreso) con semáforo — pieza clave del Criterio 2
CREATE TABLE evaluaciones_rds (
    id_evaluacion       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_solicitud        UUID NOT NULL UNIQUE REFERENCES solicitudes_credito(id_solicitud) ON DELETE CASCADE,
    ingreso_mensual     NUMERIC(12,2) NOT NULL,
    cuota_estimada      NUMERIC(12,2) NOT NULL,
    deuda_actual_mensual NUMERIC(12,2) NOT NULL DEFAULT 0,
    rds                 NUMERIC(5,2) NOT NULL,   -- (cuota_estimada + deuda_actual_mensual) / ingreso_mensual * 100
    semaforo            semaforo_rds NOT NULL,
    -- Regla normativa típica: RDS <= 30% VERDE, 30-40% AMARILLO, > 40% ROJO
    calculado_en         TIMESTAMPTZ NOT NULL DEFAULT now()
);
