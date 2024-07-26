# pylint: disable=E0401
# pylint: disable=W0621
"""
conftest.py
The main config file to set up sessions and other parameters for the test_app.py module.
"""
import os
import sys
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import engine, async_session, test_engine, test_async_session
from app import app

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Function to create a new event loop for each session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_session(event_loop):
    """Create a new database session for the test."""
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = test_async_session
            try:
                yield session
            finally:
                await transaction.rollback()
                await connection.close()

@pytest_asyncio.fixture(scope="session")
async def test_client(db_session):
    """A test client that overrides the async session with the test one."""

    def override_async_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[async_session] = override_async_session
    app.dependency_overrides[engine] = test_engine
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as test_clients:
        yield test_clients
