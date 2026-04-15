import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.config import get_settings
from app.database import Base, engine
from app.routers.documents import router as documents_router
from app.routers.query import router as query_router

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title="PageIndex Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.CLIENT_URL,
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="")
app.include_router(documents_router, prefix="/api")
app.include_router(query_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
