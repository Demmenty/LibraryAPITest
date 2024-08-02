from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from app.config import settings

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",  # Индекс
    "uq": "%(table_name)s_%(column_0_name)s_key",  # Уникальный ключ
    "ck": "%(table_name)s_%(constraint_name)s_check",  # Проверка условия
    "fk": "%(table_name)s_%(column_0_name)s_fkey",  # Внешний ключ
    "pk": "%(table_name)s_pkey",  # Первичный ключ
}

# add echo=True for sqlalchemy logs
async_engine = create_async_engine(settings.DATABASE_URL)

async_session = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
Base: DeclarativeMeta = declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    async with async_session() as db:
        yield db
