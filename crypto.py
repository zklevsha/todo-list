"""
settings.py
Module with support functions for
crypt operations
"""
import random
import string
import bcrypt


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
    Function to verify the password against its hashed version.
    """
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)
