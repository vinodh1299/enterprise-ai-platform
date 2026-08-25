from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models in our application.
    """
    pass


# Create asynchronous database engine for PostgreSQL + asyncpg
engine = create_async_engine(
    settings.get_database_url(),
    echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
    future=True,
)

# Async session factory for managing database transactions
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency that yields an AsyncSession per request,
    ensuring proper session cleanup and database connection closing.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
