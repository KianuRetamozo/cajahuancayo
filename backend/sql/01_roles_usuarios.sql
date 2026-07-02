-- ============================================================
-- 01_roles_usuarios.sql
-- RBAC: roles, permisos y usuarios (soporta Criterio 3)
-- ============================================================

CREATE TABLE roles (
    id_rol          SERIAL PRIMARY KEY,
    codigo          VARCHAR(30) NOT NULL UNIQUE,   -- ASESOR, ADMINISTRADOR, JEFE_REGIONAL, RIESGOS, COMITE, GERENCIA, CLIENTE
    nombre          VARCHAR(80) NOT NULL,
    descripcion     TEXT,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE permisos (
    id_permiso      SERIAL PRIMARY KEY,
    recurso         VARCHAR(60) NOT NULL,   -- ej: 'solicitudes_credito', 'comite', 'mora'
    accion          VARCHAR(30) NOT NULL,   -- ej: 'crear', 'leer', 'aprobar', 'derivar_judicial', 'castigar'
    descripcion     TEXT,
    UNIQUE (recurso, accion)
);

CREATE TABLE roles_permisos (
    id_rol          INTEGER NOT NULL REFERENCES roles(id_rol) ON DELETE CASCADE,
    id_permiso      INTEGER NOT NULL REFERENCES permisos(id_permiso) ON DELETE CASCADE,
    PRIMARY KEY (id_rol, id_permiso)
);

CREATE TABLE usuarios (
    id_usuario          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_rol              INTEGER NOT NULL REFERENCES roles(id_rol),
    nombre_completo     VARCHAR(150) NOT NULL,
    correo              VARCHAR(150) NOT NULL UNIQUE,
    hash_password       VARCHAR(255) NOT NULL,   -- bcrypt hash, nunca texto plano
    dni                 VARCHAR(15) UNIQUE,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    agencia             VARCHAR(80),              -- para asesores/administradores
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultimo_login        TIMESTAMPTZ
);

CREATE INDEX idx_usuarios_rol ON usuarios(id_rol);
CREATE INDEX idx_usuarios_correo ON usuarios(correo);

-- Tokens de refresco (para JWT refresh flow); opcional pero recomendado
CREATE TABLE refresh_tokens (
    id_token        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_usuario      UUID NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL,
    expira_en       TIMESTAMPTZ NOT NULL,
    revocado        BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_refresh_usuario ON refresh_tokens(id_usuario);
