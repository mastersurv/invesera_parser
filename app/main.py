from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.containers import Container
from app.api.endpoints import router
from app.database import Base, get_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    yield


app = FastAPI(
    title="InvestEra Wikipedia Parser",
    description="API для парсинга статей Википедии и генерации их краткого содержания",
    version="1.0.0",
    lifespan=lifespan
)

container = Container()
container.config.from_dict(settings.__dict__)
container.wire(modules=["app.api.endpoints"])

app.container = container

app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "InvestEra Wikipedia Parser API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/init-db")
async def init_database():
    """Initialize database tables."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return {"message": "✅ Database initialized successfully"}
    except Exception as e:
        return {"error": f"❌ Database initialization failed: {str(e)}"}


@app.get("/test-db")
async def test_database():
    """Test database connection."""
    try:
        engine = get_engine()
        from sqlalchemy import text
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
        return {"status": "✅ Database connection successful", "test_result": row[0]}
    except Exception as e:
        return {"error": f"❌ Database connection failed: {str(e)}"} 