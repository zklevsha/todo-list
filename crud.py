from db import async_session, engine
from sqlalchemy import select, MetaData
from sqlalchemy.exc import SQLAlchemyError


metadata = MetaData()

async def connect_test():
    try:
        async with engine.connect() as connection:
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

async def get_schema():
    async with async_session() as session:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.reflect, only=['alembic_version'])
        alembic_table = metadata.tables['alembic_version']
        query = await session.execute(select(alembic_table))
        result = query.scalars().all()[0]
        await session.commit()
        return result