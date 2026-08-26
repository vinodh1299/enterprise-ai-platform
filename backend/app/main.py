from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import (
    health, auth, ai, documents, rag, agent, sql_agent,
    approval, conversation, bi, report, evaluation, observability, security, recruitment
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Automatically creates database tables on startup if they do not exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise AI Operations Platform Backend API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router Endpoints
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(sql_agent.router, prefix="/api")
app.include_router(approval.router, prefix="/api")
app.include_router(conversation.router, prefix="/api")
app.include_router(bi.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(observability.router, prefix="/api")
app.include_router(security.router, prefix="/api")
app.include_router(recruitment.router, prefix="/api")


@app.get("/")
async def root():
    """
    Root endpoint redirecting users to API documentation.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} Backend",
        "documentation": "/docs",
        "health_check": "/api/health",
    }
