import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from settings import connection_string

engine = create_engine(connection_string)
schema_version_table = "schema_version"

def connect_test():
    try:
        with engine.connect() as connection:
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

async def connect():
    try:
        connection = engine.connect()
        return connection
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

def get_schema():
    query = text(f"SELECT version FROM {schema_version_table};")
    schema_v = engine.execute(query).fetchone()
    result = int(schema_v[0])
    return result
