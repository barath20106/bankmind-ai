from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.services.llm_provider import llm_provider

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint indicating database connectivity and LLM provider status."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    provider_info = llm_provider.provider_info

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "llm_provider": provider_info["provider"],
        "llm_model": provider_info["model"],
        "llm_mode": provider_info["mode"],
        "is_simulated_system": True,
        "version": "1.0.0"
    }
