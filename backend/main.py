"""
FastAPI application entry point.

Run with:
    uvicorn backend.main:app --reload --port 8000

API Documentation (auto-generated):
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routers import health, ingestion, analysis, segments, recommendations

settings = get_settings()

app = FastAPI(
    title="AI Customer Segmentation & WhatsApp Marketing API",
    description=(
        "Backend API for RFM-based customer segmentation, "
        "explainable marketing-fatigue rules, and campaign recommendations. "
        "\n\n**Note:** WhatsApp live sending is disabled by default. "
        "Set WHATSAPP_LIVE_MODE=true and provide credentials to enable."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(segments.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")


# ─── Root redirect ────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "AI Customer Segmentation API",
        "docs": "/docs",
        "health": "/health",
    }
