"""
Configuración centralizada. Todo lo sensible sale de variables de entorno,
nunca hardcodeado, para que el mismo código funcione en local, Railway/Render
y con la BD en Neon/Supabase.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # BD
    database_url: str = "postgresql+psycopg://postgres:test@localhost:5432/dbcajahuancayo"

    # JWT
    jwt_secret_key: str = "CAMBIAR_ESTE_SECRETO_EN_PRODUCCION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS - dominios del frontend (Core y Homebanking) que pueden llamar al API
    # Se puede sobreescribir con la variable de entorno CORS_ORIGINS (formato JSON),
    # por ejemplo en Render:
    # CORS_ORIGINS=["https://cajahuancayo-frontend-core.onrender.com"]
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://cajahuancayo-frontend-core.onrender.com",
    ]


settings = Settings()
