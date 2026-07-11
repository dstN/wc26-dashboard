import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.deps import get_db
from app.main import app
from app.models import Base


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(scope="session")
def db_url():
    import os

    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "wc26user")
    password = os.getenv("MYSQL_PASSWORD", "wc26pass")
    database = os.getenv("MYSQL_DATABASE", "wc26_test")
    return f"mysql+asyncmy://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture(scope="session")
def sync_db_url():
    import os

    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "wc26user")
    password = os.getenv("MYSQL_PASSWORD", "wc26pass")
    database = os.getenv("MYSQL_DATABASE", "wc26_test")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


@pytest.fixture(scope="session")
def create_tables(sync_db_url):
    sync_engine = create_engine(sync_db_url)
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_url, create_tables):
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
