import math
from datetime import date
from dateutil.relativedelta import relativedelta

def generar_cronograma(monto_prestamo, tea_porcentaje, plazo_meses, fecha_desembolso, dia_pago):
    """
    Genera el cronograma de pagos usando el sistema francés (cuotas fijas).
    """
    # 1. Convertir la TEA a decimal y calcular la TEM
    tea_decimal = tea_porcentaje / 100.0
    tem = math.pow(1 + tea_decimal, 1/12) - 1
    
    # 2. Calcular la cuota fija mensual
    # Fórmula: Cuota = P * [ i(1+i)^n / ((1+i)^n - 1) ]
    factor_anualidad = (tem * math.pow(1 + tem, plazo_meses)) / (math.pow(1 + tem, plazo_meses) - 1)
    cuota_mensual = round(monto_prestamo * factor_anualidad, 2)
    
    saldo_capital = monto_prestamo
    cronograma = []
    
    # Determinar el primer mes de pago
    fecha_pago_actual = fecha_desembolso + relativedelta(months=1)
    fecha_pago_actual = fecha_pago_actual.replace(day=dia_pago)

    # 3. Generar mes a mes
    for cuota_numero in range(1, plazo_meses + 1):
        # El interés siempre se calcula sobre el saldo restante
        interes_mes = round(saldo_capital * tem, 2)
        
        # En la última cuota, ajustamos los céntimos para que el saldo quede exactamente en 0.00
        if cuota_numero == plazo_meses:
            amortizacion_capital = saldo_capital
            cuota_final = amortizacion_capital + interes_mes
            saldo_capital = 0.00
            cuota_aplicada = cuota_final
        else:
            amortizacion_capital = round(cuota_mensual - interes_mes, 2)
            saldo_capital = round(saldo_capital - amortizacion_capital, 2)
            cuota_aplicada = cuota_mensual
            
        cronograma.append({
            "numero_cuota": cuota_numero,
            "fecha_pago": fecha_pago_actual.strftime("%d/%m/%Y"),
            "cuota": cuota_aplicada,
            "amortizacion_capital": amortizacion_capital,
            "interes": interes_mes,
            "saldo_restante": saldo_capital
        })
        
        # Avanzar al siguiente mes
        fecha_pago_actual = fecha_pago_actual + relativedelta(months=1)
        
    return cuota_mensual, cronograma

# ==========================================
# PRUEBA: Validando el CASO 1 del documento
# ==========================================
if __name__ == "__main__":
    # Datos del Caso 1: Castor Pérez
    monto = 1000.00
    tea = 43.92  # sin seguro de desgravamen
    plazo = 12
    desembolso = date(2026, 2, 2)
    dia_de_pago = 3
    
    cuota, tabla = generar_cronograma(monto, tea, plazo, desembolso, dia_de_pago)
    
    print(f"--- RESULTADO CASO 1 ---")
    print(f"Cuota calculada: S/ {cuota} (Esperado: S/ 100.95)")
    print("N° | Fecha Pago | Cuota  | Capital | Interés | Saldo")
    print("-" * 60)
    for fila in tabla:
        print(f"{fila['numero_cuota']:2} | {fila['fecha_pago']} | {fila['cuota']:6.2f} | {fila['amortizacion_capital']:7.2f} | {fila['interes']:7.2f} | {fila['saldo_restante']:7.2f}")