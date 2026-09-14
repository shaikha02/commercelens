from fastapi import FastAPI

from app.api.routes import events, health, invoices, lineage
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Deterministic Phase-1 CommerceLens mock backend using local JSON fixtures.",
)

app.include_router(health.router)
app.include_router(invoices.router, prefix=settings.api_prefix)
app.include_router(lineage.router, prefix=settings.api_prefix)
app.include_router(events.router, prefix=settings.api_prefix)
