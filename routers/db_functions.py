"""
db_functions.py
DB functions to get sessions and engine instances. 
"""
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from db import async_session, engine


async def get_db() -> AsyncSession:
    """
    Provides a new database session for each request.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_engine() -> AsyncEngine:
    """
    Returns the database engine instance.
    """
    return engine
