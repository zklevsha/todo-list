"""
settigns.py
Module for getting all the required
connection details of the databases.
"""
from dotenv import dotenv_values

config = dotenv_values(".env")
host = config.get('db_host')
database = config.get('db_database')
user = config.get('db_user')
password = config.get('db_password')

test_database = config.get('test_db_database')
test_user = config.get('test_db_user')
test_password = config.get('test_db_password')

connection_string = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"
test_connection_string = (
    f"postgresql+asyncpg://{test_user}:{test_password}@{host}:5433/{test_database}"
)
