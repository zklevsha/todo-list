import psycopg2
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

config = dotenv_values(".env")
host = config.get('host')
database = config.get('database')
user = config.get('user')
password = config.get('password')
schema_version_table = "schema_version"
connection_string = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"

engine = create_engine(connection_string)

def connect():
    try:
        with engine.connect() as connection:
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

def get_schema():
    query = text(f"SELECT version FROM {schema_version_table};")
    schema_v = engine.execute(query).fetchone()
    result = int(schema_v[0])
    return result
