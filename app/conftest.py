from typing import TYPE_CHECKING, AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import settings
from app.database import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture()
def engine() -> "AsyncEngine":
    return create_async_engine(settings.DATABASE_URL)


@pytest.fixture()
async def session(engine: "AsyncEngine") -> AsyncGenerator["AsyncSession", None]:
    async with AsyncSession(bind=engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(autouse=True)
async def _init_db(engine: "AsyncEngine") -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
