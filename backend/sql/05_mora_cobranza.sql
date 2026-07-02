-- ============================================================
-- 05_mora_cobranza.sql
-- R1 (consulta por bandas), R2 (gestión de cobranza),
-- R3 (transiciones a judicial/castigo) — Criterio 4
-- ============================================================

-- R2: cada gestión de cobranza registrada sobre un crédito en mora
CREATE TABLE gestiones_cobranza (
    id_gestion           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_credito           UUID NOT NULL REFERENCES creditos(id_credito) ON DELETE CASCADE,
    id_usuario           UUID NOT NULL REFERENCES usuarios(id_usuario),  -- gestor de cobranza
    tipo_gestion          tipo_gestion_cobranza NOT NULL,
    resultado             resultado_gestion NOT NULL,
    monto_prometido       NUMERIC(12,2),
    fecha_promesa         DATE,
    observacion            TEXT,
    creado_en              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_gestiones_credito ON gestiones_cobranza(id_credito);
CREATE INDEX idx_gestiones_fecha ON gestiones_cobranza(creado_en);

-- R3: historial de cada cambio de banda de mora, con quién y por qué lo autorizó
-- (relevante porque derivar a judicial o castigar son acciones críticas restringidas por rol, Criterio 3)
CREATE TABLE historial_transiciones_mora (
    id_transicion         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_credito             UUID NOT NULL REFERENCES creditos(id_credito) ON DELETE CASCADE,
    banda_anterior         banda_mora NOT NULL,
    banda_nueva             banda_mora NOT NULL,
    dias_atraso_al_cambio   INTEGER NOT NULL,
    id_usuario_autoriza     UUID REFERENCES usuarios(id_usuario),  -- NULL si fue automático por el sistema
    es_automatico            BOOLEAN NOT NULL DEFAULT TRUE,
    observacion              TEXT,
    creado_en                TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_transiciones_credito ON historial_transiciones_mora(id_credito);

-- R1: vista de apoyo para el tablero de KPIs por banda de mora.
-- El backend puede consultar esta vista directamente para el dashboard de Recuperaciones.
CREATE VIEW vista_kpis_mora AS
SELECT
    c.banda_mora_actual,
    COUNT(*)                              AS cantidad_creditos,
    SUM(c.monto_desembolsado)             AS monto_total_cartera,
    ROUND(AVG(c.dias_atraso), 1)          AS dias_atraso_promedio
FROM creditos c
WHERE c.estado IN ('EN_MORA', 'JUDICIAL', 'CASTIGADO')
GROUP BY c.banda_mora_actual;
