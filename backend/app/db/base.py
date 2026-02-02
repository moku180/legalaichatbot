"""Database configuration and session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


from sqlalchemy import text

# ... (imports)

async def init_db() -> None:
    """Initialize database - create tables and apply partial migrations"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Auto-migration: Ensure processing_status column exists
        # This fixes the "UndefinedColumnError" on existing databases (Production/Local)
        try:
            await conn.execute(text(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'queued'"
            ))
        except Exception as e:
            print(f"Migration warning: {e}")


async def close_db() -> None:
    """Close database connections"""
    await engine.dispose()
