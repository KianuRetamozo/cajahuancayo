-- ============================================================
-- 02_clientes_cuentas.sql
-- Clientes, cuentas y movimientos.
-- Estas tablas son el "puente" real entre Core y Homebanking:
-- ambos sistemas leen/escriben sobre las mismas filas (Criterio 1).
-- ============================================================

CREATE TABLE clientes (
    id_cliente          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_usuario          UUID UNIQUE REFERENCES usuarios(id_usuario), -- login del cliente en Homebanking
    tipo_documento      VARCHAR(10) NOT NULL DEFAULT 'DNI',
    numero_documento    VARCHAR(15) NOT NULL UNIQUE,
    nombres             VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL,
    fecha_nacimiento    DATE NOT NULL,
    correo              VARCHAR(150),
    telefono            VARCHAR(20),
    direccion           TEXT,
    ingreso_mensual     NUMERIC(12,2) NOT NULL CHECK (ingreso_mensual >= 0),
    ocupacion           VARCHAR(100),
    es_sujeto_credito    BOOLEAN NOT NULL DEFAULT FALSE, -- resultado de elegibilidad (Criterio 2)
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_clientes_documento ON clientes(numero_documento);

CREATE TABLE cuentas (
    id_cuenta           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_cliente          UUID NOT NULL REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    numero_cuenta       VARCHAR(20) NOT NULL UNIQUE,
    tipo_cuenta         VARCHAR(30) NOT NULL DEFAULT 'AHORROS',
    moneda              VARCHAR(3) NOT NULL DEFAULT 'PEN',
    saldo_disponible    NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (saldo_disponible >= 0),
    estado              VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_cuentas_cliente ON cuentas(id_cliente);

-- Todo movimiento (desembolso, pago de cuota, depósito) queda aquí.
-- Esto es lo que permite que el Homebanking "vea" en tiempo real lo que hace el Core.
CREATE TABLE movimientos (
    id_movimiento       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_cuenta           UUID NOT NULL REFERENCES cuentas(id_cuenta) ON DELETE CASCADE,
    tipo_movimiento     tipo_movimiento NOT NULL,
    monto               NUMERIC(14,2) NOT NULL,
    saldo_posterior     NUMERIC(14,2) NOT NULL,
    canal_origen        canal_origen NOT NULL,
    referencia          VARCHAR(100),   -- ej: id_credito o id_solicitud relacionado
    descripcion         TEXT,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_movimientos_cuenta ON movimientos(id_cuenta);
CREATE INDEX idx_movimientos_fecha ON movimientos(creado_en);
