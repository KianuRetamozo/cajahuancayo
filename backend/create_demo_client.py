"""
Crea un cliente demo con acceso a Homebanking: usuario (rol CLIENTE),
registro de cliente, una cuenta de ahorros y algunos movimientos.
Contraseña: Andino2026!
Uso: python3 create_demo_client.py
"""
import sys
import uuid
from datetime import date, datetime, timedelta

sys.path.insert(0, ".")

from app.database import SessionLocal
from app.core.security import hash_password
from app.models.rbac import Usuario, Rol
from app.models.cuentas import Cliente, Cuenta, Movimiento

db = SessionLocal()

rol_cliente = db.query(Rol).filter(Rol.codigo == "CLIENTE").first()
if rol_cliente is None:
    raise SystemExit("No existe el rol CLIENTE. Corre primero 07_seed_data.sql")

correo_demo = "maria.cliente@correo.pe"
usuario_existente = db.query(Usuario).filter(Usuario.correo == correo_demo).first()
if usuario_existente:
    print("El cliente demo ya existe, no se duplica.")
    db.close()
    raise SystemExit(0)

usuario = Usuario(
    id_rol=rol_cliente.id_rol,
    nombre_completo="María Fernanda Quispe Rojas",
    correo=correo_demo,
    hash_password=hash_password("Andino2026!"),
    dni="45678912",
    activo=True,
)
db.add(usuario)
db.flush()

cliente = Cliente(
    id_usuario=usuario.id_usuario,
    tipo_documento="DNI",
    numero_documento="45678912",
    nombres="María Fernanda",
    apellidos="Quispe Rojas",
    fecha_nacimiento=date(1994, 3, 12),
    correo=correo_demo,
    telefono="987654321",
    direccion="Jr. Real 456, Huancayo",
    ingreso_mensual=2800.00,
    ocupacion="Comerciante independiente",
    es_sujeto_credito=True,
)
db.add(cliente)
db.flush()

cuenta = Cuenta(
    id_cliente=cliente.id_cliente,
    numero_cuenta="20112233445",
    tipo_cuenta="AHORROS",
    moneda="PEN",
    saldo_disponible=1845.50,
    estado="ACTIVA",
)
db.add(cuenta)
db.flush()

movimientos = [
    (350.00, "DEPOSITO", "CORE", "Depósito en agencia", 6),
    (250.00, "RETIRO", "HOMEBANKING", "Retiro por transferencia", 4),
    (1200.00, "DEPOSITO", "AGENCIA", "Abono de sueldo", 2),
    (545.50, "PAGO_CUOTA", "HOMEBANKING", "Pago de cuota adelantada", 0),
]

saldo_corriendo = 0.0
for monto, tipo, canal, desc, dias_atras in movimientos:
    saldo_corriendo += monto if tipo == "DEPOSITO" else -monto
    db.add(Movimiento(
        id_cuenta=cuenta.id_cuenta,
        tipo_movimiento=tipo,
        monto=monto,
        saldo_posterior=cuenta.saldo_disponible,
        canal_origen=canal,
        descripcion=desc,
        creado_en=datetime.utcnow() - timedelta(days=dias_atras),
    ))

db.commit()
print(f"Cliente demo creado: {correo_demo} / Andino2026!")
print(f"Cuenta {cuenta.numero_cuenta} con saldo S/ {cuenta.saldo_disponible}")
db.close()
