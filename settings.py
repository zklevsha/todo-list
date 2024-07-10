from dotenv import dotenv_values

config = dotenv_values(".env")
host = config.get('db_host')
database = config.get('db_database')
user = config.get('db_user')
password = config.get('db_password')
connection_string = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"
