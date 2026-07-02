"""
Actualiza las contraseñas de los usuarios semilla con hashes bcrypt reales.
Uso: python3 set_passwords_demo.py
Contraseña para todos: Andino2026!
"""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.core.security import hash_password
from app.models.rbac import Usuario

PASSWORD_DEMO = "Andino2026!"

db = SessionLocal()
usuarios = db.query(Usuario).all()
for u in usuarios:
    u.hash_password = hash_password(PASSWORD_DEMO)
db.commit()
print(f"Actualizadas {len(usuarios)} contraseñas con hash real de '{PASSWORD_DEMO}'")
db.close()
