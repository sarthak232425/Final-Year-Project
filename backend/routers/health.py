"""Health check router."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Basic liveness check. Returns 200 if the API is running."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "AI Customer Segmentation API",
        "version": "0.1.0",
    }
