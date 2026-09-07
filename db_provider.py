# db_provider.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import settings

async_engine = create_async_engine(
    url = f"{settings.DATABASE_DRIVER}://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DATABASE_URL}/{settings.POSTGRES_DB}",
    pool_size=10,
    max_overflow=5,
    pool_timeout=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False
)

# Фабрика асинхронных сессий
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Для FastAPI (Dependency Injection)
async def get_db():
    async with async_session() as session:
        yield session
