from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

Base = declarative_base()

_engine = None
_async_session_maker = None


def get_engine():
    """Get async engine with lazy initialization."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    return _engine


def get_async_session_maker():
    """Get async session maker with lazy initialization."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _async_session_maker


async_session_maker = get_async_session_maker


async def get_async_session() -> AsyncSession:
    """Get async database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session 