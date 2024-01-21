from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from modules.globals import config

engine = create_async_engine(
    f"{config.database.db_driver}://{config.database.connection_url}",
    echo=False,
    pool_size=10,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    async with SessionLocal() as session:
        yield session