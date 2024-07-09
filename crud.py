from db import async_session, engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


async def connect_test():
    try:
        async with engine.connect() as connection:
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

async def get_schema():
    async with async_session() as session:
        query = text("SELECT version_num FROM alembic_version;")
        result = await session.execute(query)
        version_num = result.scalar()
        return version_num