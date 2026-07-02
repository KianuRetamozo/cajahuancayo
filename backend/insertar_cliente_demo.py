import sys, uuid
from datetime import date
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.core.security import hash_password
from app.models.rbac import Usuario, Rol
from app.models.cuentas import Cliente, Cuenta

db = SessionLocal()

rol_cliente = db.query(Rol).filter(Rol.codigo == "CLIENTE").first()

usuario_cliente = Usuario(
    id_rol=rol_cliente.id_rol,
    nombre_completo="Pedro Quispe Mamani",
    correo="pedro.cliente@demo.pe",
    hash_password=hash_password("Cliente2026!"),
    dni="80099999",
)
db.add(usuario_cliente)
db.flush()

cliente = Cliente(
    id_usuario=usuario_cliente.id_usuario,
    numero_documento="80099999",
    nombres="Pedro",
    apellidos="Quispe Mamani",
    fecha_nacimiento=date(1990, 5, 12),
    correo="pedro.cliente@demo.pe",
    telefono="987654321",
    ingreso_mensual=3500.00,
    ocupacion="Comerciante",
)
db.add(cliente)
db.flush()

cuenta = Cuenta(
    id_cliente=cliente.id_cliente,
    numero_cuenta="191-" + str(uuid.uuid4().int)[:10],
    saldo_disponible=100.00,
)
db.add(cuenta)
db.commit()

print("id_cliente:", cliente.id_cliente)
print("correo login:", usuario_cliente.correo, "password: Cliente2026!")
db.close()
