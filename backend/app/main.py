from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, mora, homebanking, solicitudes

app = FastAPI(
    title="Caja Huancayo - Core Financiero API",
    description="API única que sirve tanto al Core como al Homebanking sobre postgres.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mora.router)
app.include_router(homebanking.router)
app.include_router(solicitudes.router)


@app.get("/health")
def health():
    return {"status": "ok"}
