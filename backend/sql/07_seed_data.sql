-- ============================================================
-- 07_seed_data.sql
-- Datos semilla: roles, permisos, usuarios de prueba,
-- productos y matriz de aprobación.
-- (La carga masiva de clientes/créditos con mora ~13% se hace
-- con un script Python aparte para generar volumen realista,
-- ver backend/scripts/generar_datos_demo.py)
-- ============================================================

-- --- Roles ---
INSERT INTO roles (codigo, nombre, descripcion) VALUES
    ('ASESOR', 'Asesor de negocios', 'Atiende clientes y origina solicitudes'),
    ('ADMINISTRADOR', 'Administrador de agencia', 'Primera opinión sobre solicitudes'),
    ('JEFE_REGIONAL', 'Jefe Regional', 'Segunda opinión para montos medios/altos'),
    ('RIESGOS', 'Analista de Riesgos', 'Evalúa scoring y RDS, opina en solicitudes altas'),
    ('COMITE', 'Miembro de Comité de Créditos', 'Decisión final en montos altos'),
    ('GERENCIA', 'Gerencia', 'Supervisión general, autoriza castigos'),
    ('CLIENTE', 'Cliente Homebanking', 'Accede solo a su propia información');

-- --- Permisos (recurso, acción) ---
INSERT INTO permisos (recurso, accion, descripcion) VALUES
    ('solicitudes_credito', 'crear', 'Crear una solicitud de crédito'),
    ('solicitudes_credito', 'leer', 'Ver solicitudes de crédito'),
    ('solicitudes_credito', 'opinar', 'Emitir opinión (aprobar/rechazar) en una solicitud'),
    ('comite', 'resolver', 'Registrar decisión final del comité'),
    ('creditos', 'leer', 'Ver créditos otorgados'),
    ('creditos', 'desembolsar', 'Ejecutar el desembolso de un crédito aprobado'),
    ('mora', 'leer', 'Consultar cartera en mora (R1)'),
    ('mora', 'gestionar', 'Registrar gestiones de cobranza (R2)'),
    ('mora', 'derivar_judicial', 'Confirmar derivación a judicial (R3)'),
    ('mora', 'castigar', 'Confirmar castigo de un crédito (R3)'),
    ('usuarios', 'administrar', 'Crear/editar usuarios y roles');

-- --- Asignación de permisos por rol ---
INSERT INTO roles_permisos (id_rol, id_permiso)
SELECT r.id_rol, p.id_permiso FROM roles r, permisos p WHERE
    (r.codigo = 'CLIENTE' AND p.recurso = 'solicitudes_credito' AND p.accion IN ('crear','leer'))
 OR (r.codigo = 'ASESOR' AND p.recurso = 'solicitudes_credito' AND p.accion IN ('crear','leer'))
 OR (r.codigo = 'ADMINISTRADOR' AND p.recurso IN ('solicitudes_credito') AND p.accion IN ('leer','opinar'))
 OR (r.codigo = 'ADMINISTRADOR' AND p.recurso = 'creditos' AND p.accion = 'desembolsar')
 OR (r.codigo = 'JEFE_REGIONAL' AND p.recurso = 'solicitudes_credito' AND p.accion IN ('leer','opinar'))
 OR (r.codigo = 'RIESGOS' AND p.recurso = 'solicitudes_credito' AND p.accion IN ('leer','opinar'))
 OR (r.codigo = 'RIESGOS' AND p.recurso = 'mora' AND p.accion IN ('leer','derivar_judicial'))
 OR (r.codigo = 'COMITE' AND p.recurso = 'comite' AND p.accion = 'resolver')
 OR (r.codigo = 'COMITE' AND p.recurso = 'solicitudes_credito' AND p.accion = 'leer')
 OR (r.codigo = 'GERENCIA' AND p.recurso = 'mora' AND p.accion IN ('leer','castigar'))
 OR (r.codigo = 'GERENCIA' AND p.recurso = 'usuarios' AND p.accion = 'administrar')
 OR (r.codigo IN ('ASESOR','ADMINISTRADOR','JEFE_REGIONAL','RIESGOS','GERENCIA') AND p.recurso = 'mora' AND p.accion = 'gestionar')
 OR (r.codigo IN ('ASESOR','ADMINISTRADOR','JEFE_REGIONAL','RIESGOS','COMITE','GERENCIA') AND p.recurso = 'creditos' AND p.accion = 'leer')
 OR (r.codigo IN ('ASESOR','ADMINISTRADOR','JEFE_REGIONAL','RIESGOS','COMITE','GERENCIA') AND p.recurso = 'mora' AND p.accion = 'leer');

-- --- Usuarios de prueba (password: "Andino2026!" hasheado con bcrypt) ---
-- NOTA: reemplazar hash_password real generado por tu backend al hacer el seeding definitivo.
INSERT INTO usuarios (id_rol, nombre_completo, correo, hash_password, dni, agencia)
SELECT r.id_rol, v.nombre, v.correo, '$2b$12$REEMPLAZAR_CON_HASH_REAL', v.dni, v.agencia
FROM (VALUES
    ('ASESOR',        'Lucía Ramos Vega',      'lucia.asesor@bancoandino.pe',      '70011111', 'Huancayo Centro'),
    ('ADMINISTRADOR', 'Carlos Mendoza Ríos',   'carlos.admin@bancoandino.pe',      '70022222', 'Huancayo Centro'),
    ('JEFE_REGIONAL', 'Rosa Salas Quispe',     'rosa.jefe@bancoandino.pe',         '70033333', 'Regional Junín'),
    ('RIESGOS',       'Iván Torres Paredes',   'ivan.riesgos@bancoandino.pe',      '70044444', 'Sede Central'),
    ('COMITE',        'Comité de Créditos',    'comite@bancoandino.pe',            '70055555', 'Sede Central'),
    ('GERENCIA',      'Marisol Huamán Cueva',  'marisol.gerencia@bancoandino.pe',  '70066666', 'Sede Central')
) AS v(codigo_rol, nombre, correo, dni, agencia)
JOIN roles r ON r.codigo = v.codigo_rol;

-- --- Productos de crédito (2 productos, según Criterio 5) ---
INSERT INTO productos_credito (codigo, nombre, tasa_interes_anual, monto_minimo, monto_maximo, plazo_min_meses, plazo_max_meses) VALUES
    ('CONSUMO', 'Crédito de Consumo Personal', 28.50, 500.00, 20000.00, 6, 36),
    ('MYPE',    'Crédito MYPE Capital de Trabajo', 22.00, 1000.00, 50000.00, 6, 48);

-- --- Matriz de aprobación por monto (ruta de aprobación, Criterio 2) ---
INSERT INTO matriz_aprobacion (monto_desde, monto_hasta, requiere_admin, requiere_jefe_regional, requiere_riesgos, requiere_comite) VALUES
    (0.00,      5000.00,   TRUE,  FALSE, FALSE, FALSE),
    (5000.01,   15000.00,  TRUE,  TRUE,  FALSE, FALSE),
    (15000.01,  30000.00,  TRUE,  TRUE,  TRUE,  FALSE),
    (30000.01,  50000.00,  TRUE,  TRUE,  TRUE,  TRUE);
