"""
conftest.py
The main config file to set up sessions and other parameters for the test_app.py module.
"""
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from db import test_engine, test_async_session
from settings import generate_random_string
from app import app
from routers.db_functions import get_db, get_engine, AsyncEngine, AsyncSession

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

async def override_get_engine() -> AsyncEngine:
    """
    Returns the test db engine instance.
    """
    return test_engine

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
    app.dependency_overrides[get_engine] = override_get_engine
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as test_clients:
        yield test_clients

def generate_username():
    """
    Function to create a random 6-letter username.
    """
    return generate_random_string(6)

def generate_creds():
    """
    Function to create a pair of user/email.
    """
    user = generate_username()
    email = f"{user}@test.com"
    return user, email
