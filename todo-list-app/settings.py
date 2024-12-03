"""
settings.py
Module for parsing all required
details from the .env file
"""
from dotenv import dotenv_values
from crypto import hash_password, generate_random_string

config = dotenv_values(".env") or dotenv_values("../.env")
app_url = config.get('app_url') or 'localhost'
app_url = f'http://{app_url}'

HOST = 'localhost'
database = config.get('db_database')
user = config.get('db_user')
password = config.get('db_password')

test_database = config.get('test_db_database') or 'test_db'
test_user = config.get('test_db_user') or 'test_user'
test_password = config.get('test_db_password') or 'test_password'

admin_username = config.get('admin_username') or generate_random_string(10)
admin_email = config.get('admin_email') or f'{admin_username}@admin.com'
admin_password = config.get('admin_password') or generate_random_string(15)
admin_hashed_password = hash_password(admin_password)

connection_string = f"postgresql+asyncpg://{user}:{password}@{HOST}/{database}"
test_connection_string = (
    f"postgresql+asyncpg://{test_user}:{test_password}@{HOST}:5433/{test_database}"
)

SECRET_KEY = config.get('secret_key') or generate_random_string(50)

mail_from_address = config.get('mail_from_address')
mail_token = config.get('mail_token')
