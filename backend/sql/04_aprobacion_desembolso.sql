-- ============================================================
-- 04_aprobacion_desembolso.sql
-- Ruta de aprobación por monto, historial de aprobaciones,
-- créditos otorgados y cronograma de pagos (Criterio 2 y 1)
-- ============================================================

-- Matriz que define, según el monto solicitado, qué roles deben opinar
-- antes de llegar (o no) a comité. Esto materializa "ruta de aprobación por montos".
CREATE TABLE matriz_aprobacion (
    id_regla            SERIAL PRIMARY KEY,
    monto_desde         NUMERIC(12,2) NOT NULL,
    monto_hasta         NUMERIC(12,2) NOT NULL,
    requiere_admin      BOOLEAN NOT NULL DEFAULT TRUE,
    requiere_jefe_regional BOOLEAN NOT NULL DEFAULT FALSE,
    requiere_riesgos    BOOLEAN NOT NULL DEFAULT FALSE,
    requiere_comite     BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (monto_hasta > monto_desde)
);

-- Cada opinión/decisión que se registra sobre una solicitud, en orden.
CREATE TABLE aprobaciones (
    id_aprobacion       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_solicitud        UUID NOT NULL REFERENCES solicitudes_credito(id_solicitud) ON DELETE CASCADE,
    id_usuario          UUID NOT NULL REFERENCES usuarios(id_usuario),
    nivel               VARCHAR(30) NOT NULL,   -- 'ADMINISTRADOR', 'JEFE_REGIONAL', 'RIESGOS', 'COMITE'
    decision            VARCHAR(20) NOT NULL,   -- 'APROBADO', 'RECHAZADO', 'OBSERVADO'
    comentario           TEXT,
    creado_en            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_aprobaciones_solicitud ON aprobaciones(id_solicitud);

-- Crédito ya otorgado y desembolsado. Nace cuando la solicitud pasa a DESEMBOLSADA.
CREATE TABLE creditos (
    id_credito           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_solicitud         UUID NOT NULL UNIQUE REFERENCES solicitudes_credito(id_solicitud),
    id_cliente           UUID NOT NULL REFERENCES clientes(id_cliente),
    id_cuenta_desembolso  UUID NOT NULL REFERENCES cuentas(id_cuenta),
    monto_desembolsado    NUMERIC(12,2) NOT NULL,
    tasa_interes_anual    NUMERIC(5,2) NOT NULL,
    plazo_meses           INTEGER NOT NULL,
    fecha_desembolso       DATE NOT NULL DEFAULT CURRENT_DATE,
    estado                estado_credito NOT NULL DEFAULT 'VIGENTE',
    banda_mora_actual      banda_mora NOT NULL DEFAULT 'VIGENTE',
    dias_atraso            INTEGER NOT NULL DEFAULT 0,
    creado_en              TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_creditos_cliente ON creditos(id_cliente);
CREATE INDEX idx_creditos_banda_mora ON creditos(banda_mora_actual);

CREATE TABLE cronograma_pagos (
    id_cuota             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_credito           UUID NOT NULL REFERENCES creditos(id_credito) ON DELETE CASCADE,
    numero_cuota         INTEGER NOT NULL,
    fecha_vencimiento    DATE NOT NULL,
    monto_cuota          NUMERIC(12,2) NOT NULL,
    monto_capital        NUMERIC(12,2) NOT NULL,
    monto_interes        NUMERIC(12,2) NOT NULL,
    pagado               BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_pago           DATE,
    UNIQUE (id_credito, numero_cuota)
);

CREATE INDEX idx_cronograma_credito ON cronograma_pagos(id_credito);
CREATE INDEX idx_cronograma_vencimiento ON cronograma_pagos(fecha_vencimiento) WHERE pagado = FALSE;
