import asyncpg
from settings import connection_string
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(connection_string)
async_session = async_sessionmaker(engine, expire_on_commit=False)   