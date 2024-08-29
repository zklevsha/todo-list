"""
settigns.py
Module for getting all the required
connection details of the databases.
"""
import random
import string
import bcrypt
from dotenv import dotenv_values

def generate_random_string(length):
    """
    Function to generate a random string.
    """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def hash_password(plain_password):
    """
    Function to hash the supplied password.
    """
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

def verify_password(plain_password, hashed_password):
    """
    Function to verify the password againts its hashed version.
    """
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)


config = dotenv_values(".env")
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
