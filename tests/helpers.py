"""
crypto.py
A support module containing useful functions.
"""
from schemas import UserOutput
from crypto import generate_random_string
from oauth import create_access_token


def generate_username():
    """
    Function to create a random 6-letter username.
    """
    return generate_random_string(6)


def generate_creds():
    """
    Function to create a pair of user/email.
    """
    user = generate_username()
    email = f"{user}@test.com"
    return user, email


async def get_new_user_id(test_client, base_url) -> None:
    """
    Function to generate a new user for the tests.
    """
    user, email = generate_creds()
    user_data = {"username": user, "email": email, "password": "test"}
    response = await test_client.post(f"{base_url}/register", json=user_data)
    parsed_response = UserOutput(**response.json())
    return parsed_response


async def login(test_client, base_url, main_test_user) -> None:
    """
    Function to log in as the previously created user.
    """
    if not main_test_user:
        new_user = await get_new_user_id(test_client=test_client, base_url=base_url)
        main_test_user.update(new_user.model_dump())
    return UserOutput(**main_test_user)


async def get_new_token(test_client, base_url, main_test_user) -> None:
    """
    Function to generate a token imitating the login function.
    """
    new_user = await login(test_client=test_client,
                           base_url=base_url, main_test_user=main_test_user)
    access_token = create_access_token(data={"user_id": new_user.user.id,
                                             "user_role": new_user.user.role})
    return access_token

ADMIN_TOKEN = create_access_token(data={"user_id": 1, "user_role": "admin"})
