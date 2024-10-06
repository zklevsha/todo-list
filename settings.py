"""
settings.py
Module for parsing all required
details from the .env file
"""
from dotenv import dotenv_values
from crypto import hash_password, generate_random_string

config = dotenv_values(".env")
app_url = config.get('app_url') or 'localhost'
app_url = f'http://{app_url}'

host = config.get('db_host')
database = config.get('db_database')
user = config.get('db_user')
password = config.get('db_password')

test_database = config.get('test_db_database')
test_user = config.get('test_db_user')
test_password = config.get('test_db_password')

admin_username = config.get('admin_username') or 'admin'
admin_email = config.get('admin_email') or 'admin@admin.com'
admin_password = config.get('admin_password') or generate_random_string(10)
admin_hashed_password = hash_password(admin_password)

connection_string = f"postgresql+asyncpg://{user}:{password}@{host}/{database}"
test_connection_string = (
    f"postgresql+asyncpg://{test_user}:{test_password}@{host}:5433/{test_database}"
)

SECRET_KEY = config.get('secret_key')

mail_from_address = config.get('mail_from_address')
mail_token = config.get('mail_token')

TZ = config.get('TZ')
