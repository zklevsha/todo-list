"""
conftest.py
The main config file to set up sessions and other parameters for the test_app.py module.
"""
import asyncio
import pytest_asyncio
import sqlalchemy as sa
from httpx import AsyncClient, ASGITransport
from db import test_async_session
from app import app
from models import User
from routers.helpers import get_db, AsyncSession


async def override_get_db() -> AsyncSession:
    """
    Provides a new test db session to override
    the main one.
    """
    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Function to create a new event loop for each session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_client():
    """
    A test client that overrides the async session with the test one.
    """
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver"
    ) as _test_client:
        yield _test_client


@pytest_asyncio.fixture(name="db", scope="session")
async def fixture_db():
    """
    Provides a test database session as a fixture for the clean_test_db function.
    """
    async with test_async_session() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def clean_test_db(db: AsyncSession):
    """
    Function to clean the test DB before each test run.
    """
    query = sa.delete(User).where(User.id > 1)
    await db.execute(query)
    await db.commit()

    yield
