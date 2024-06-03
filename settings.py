from dotenv import dotenv_values

config = dotenv_values(".env")
host = config.get('db_host')
database = config.get('db_name')
user = config.get('db_user')
password = config.get('db_password')
connection_string = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"