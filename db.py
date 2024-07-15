from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from settings import connection_string

engine = create_async_engine(connection_string)
async_session = async_sessionmaker(engine, expire_on_commit=False)
