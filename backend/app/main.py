from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.seed import seed_database
from app.api.routes import (
    health,
    dashboard,
    customers,
    accounts,
    transactions,
    fraud,
    loans,
    chat,
    agents,
    traces,
    audit
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bankmind.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database is initialized & seeded
    logger.info("Initializing BankMind AI simulated database...")
    db = SessionLocal()
    try:
        seed_res = seed_database(db=db, force_recreate=False)
        logger.info(f"Database seed status: {seed_res.get('message')}")
    except Exception as e:
        logger.error(f"Failed to auto-seed database: {e}")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("BankMind AI backend shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent Simulated Banking Architecture with Google Gemini & Deterministic Guardrails",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],  # Accommodate local dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal simulated banking service error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred. Please try again."
        }
    )

# Include API Routers under /api
api_prefix = "/api"
app.include_router(health.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(customers.router, prefix=api_prefix)
app.include_router(accounts.router, prefix=api_prefix)
app.include_router(transactions.router, prefix=api_prefix)
app.include_router(fraud.router, prefix=api_prefix)
app.include_router(loans.router, prefix=api_prefix)
app.include_router(chat.router, prefix=api_prefix)
app.include_router(agents.router, prefix=api_prefix)
app.include_router(traces.router, prefix=api_prefix)
app.include_router(audit.router, prefix=api_prefix)


@app.get("/")
def root():
    return {
        "name": "BankMind AI Backend",
        "status": "online",
        "documentation": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
