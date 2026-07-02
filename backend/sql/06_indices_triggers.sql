-- ============================================================
-- 06_indices_triggers.sql
-- Triggers de auditoría (updated_at) y automatización de la
-- clasificación por banda de mora (soporta R3 del Criterio 4)
-- ============================================================

-- --- Trigger genérico para mantener actualizado_en ---
CREATE OR REPLACE FUNCTION fn_actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_clientes_updated_at
    BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_usuarios_updated_at
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_solicitudes_updated_at
    BEFORE UPDATE ON solicitudes_credito
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

CREATE TRIGGER trg_creditos_updated_at
    BEFORE UPDATE ON creditos
    FOR EACH ROW EXECUTE FUNCTION fn_actualizar_timestamp();

-- --- Función que recalcula días de atraso y banda de mora de un crédito ---
-- Se llama desde el backend (job diario o al consultar) para mantener
-- creditos.dias_atraso y banda_mora_actual sincronizados con el cronograma real.
CREATE OR REPLACE FUNCTION fn_recalcular_mora_credito(p_id_credito UUID)
RETURNS VOID AS $$
DECLARE
    v_dias_atraso INTEGER;
    v_banda_anterior banda_mora;
    v_banda_nueva banda_mora;
BEGIN
    SELECT COALESCE(MAX(CURRENT_DATE - fecha_vencimiento), 0)
    INTO v_dias_atraso
    FROM cronograma_pagos
    WHERE id_credito = p_id_credito AND pagado = FALSE AND fecha_vencimiento < CURRENT_DATE;

    SELECT banda_mora_actual INTO v_banda_anterior FROM creditos WHERE id_credito = p_id_credito;

    v_banda_nueva := CASE
        WHEN v_dias_atraso = 0 THEN 'VIGENTE'::banda_mora
        WHEN v_dias_atraso BETWEEN 1 AND 30 THEN 'PREVENTIVA'::banda_mora
        WHEN v_dias_atraso BETWEEN 31 AND 60 THEN 'TEMPRANA'::banda_mora
        WHEN v_dias_atraso BETWEEN 61 AND 120 THEN 'TARDIA'::banda_mora
        WHEN v_dias_atraso BETWEEN 121 AND 180 THEN 'JUDICIAL'::banda_mora
        ELSE 'CASTIGO'::banda_mora
    END;

    UPDATE creditos
    SET dias_atraso = v_dias_atraso,
        banda_mora_actual = v_banda_nueva,
        estado = CASE
            WHEN v_banda_nueva = 'VIGENTE' THEN 'VIGENTE'::estado_credito
            WHEN v_banda_nueva = 'JUDICIAL' THEN 'JUDICIAL'::estado_credito
            WHEN v_banda_nueva = 'CASTIGO' THEN 'CASTIGADO'::estado_credito
            ELSE 'EN_MORA'::estado_credito
        END
    WHERE id_credito = p_id_credito;

    IF v_banda_anterior IS DISTINCT FROM v_banda_nueva THEN
        INSERT INTO historial_transiciones_mora
            (id_credito, banda_anterior, banda_nueva, dias_atraso_al_cambio, es_automatico)
        VALUES
            (p_id_credito, v_banda_anterior, v_banda_nueva, v_dias_atraso, TRUE);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Nota: la transición a JUDICIAL (>=121 días) y CASTIGO (>180 días) que ejecuta
-- esta función es automática por umbral, tal como pide el Criterio 4. El backend
-- debe además exigir que solo RIESGOS/GERENCIA puedan *confirmar* la derivación
-- judicial o el castigo definitivo (eso se valida en la capa de permisos, no en la BD).
