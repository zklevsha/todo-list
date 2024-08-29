"""
test_users.py
The module containing all user-related tests for the FastAPI application.
"""
from conftest import app, get_db, get_engine, generate_creds #pylint: disable=W0611
#Both get_db and get_engine are referenced in the
#dependency injection, so they need to be imported.
from oauth import create_access_token
from schemas import UserOutput

BASE_URL = "/api/v1/users"
main_test_user = {}

async def get_new_user_id(test_client) -> None:
    """
    Function to generate a new user for the tests.
    """
    user, email = generate_creds()
    user_data = {"username": user, "email": email, "password": "test"}
    response = await test_client.post(f"{BASE_URL}/register", json=user_data)
    parsed_response = UserOutput(**response.json())
    return parsed_response


async def log_user(test_client) -> None:
    """
    Function to log in as the previously created user.
    """
    if not main_test_user:
        new_user = await get_new_user_id(test_client=test_client)
        main_test_user.update(new_user.model_dump())
    return UserOutput(**main_test_user)


async def get_new_token(test_client) -> None:
    """
    Function to generate a token imitating the login function.
    """
    new_user = await log_user(test_client=test_client)
    access_token = create_access_token(data =
                    {"user_id": new_user.user.id, "user_role": new_user.user.role})
    return access_token


async def test_get_user_by_id(test_client) -> None:
    """
    Testing getting a user by ID.
    """
    user = await log_user(test_client)
    user_id = user.user.id
    auth_token = await get_new_token(test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/{user_id}", headers=headers)
    returned_user: UserOutput = UserOutput.model_validate(response.json())
    assert response.status_code == 200
    assert isinstance(returned_user, UserOutput)
    no_user = await test_client.get(f"{BASE_URL}/131313", headers=headers)
    assert no_user.status_code == 404


async def test_update_user(test_client) -> None:
    """
    Testing updating a user.
    """
    user = await log_user(test_client)
    user_id = user.user.id
    new_username, new_email = generate_creds()
    new_data = {"username": new_username, "email": new_email}
    auth_token = await get_new_token(test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=headers)
    returned_user: UserOutput = UserOutput.model_validate(response.json())
    assert response.status_code == 200
    assert isinstance(returned_user, UserOutput)

    no_auth_user = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data)
    assert no_auth_user.status_code == 401

    #Testing duplication
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=headers)
    assert response.status_code == 409


async def test_change_user_role(test_client) -> None:
    """
    Testing changing the role of a user.
    """
    user = await log_user(test_client)
    user_id = user.user.id
    role_data = {"role":"admin"}
    auth_token = await get_new_token(test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data, headers=headers)
    assert response.status_code == 403

    no_auth_user = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data)
    assert no_auth_user.status_code == 401

    #Testing non-existent
    response = await test_client.patch(f"{BASE_URL}/131313", json=role_data, headers=headers)
    assert response.status_code == 400

async def test_get_all_users(test_client) -> None:
    """
    Testing the endpoint to get all users (only admin can use it).
    """
    auth_token = await get_new_token(test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/", headers=headers)
    assert response.status_code == 403

    no_auth_user = await test_client.get(f"{BASE_URL}/")
    assert no_auth_user.status_code == 401


async def test_delete_user(test_client) -> None:
    """
    Testing deleting a user.
    """
    user = await log_user(test_client)
    user_id = user.user.id
    auth_token = await get_new_token(test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.delete(f"{BASE_URL}/{user_id}", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    no_auth_user = await test_client.delete(f"{BASE_URL}/{user_id}")
    assert no_auth_user.status_code == 401

    #Testing non-existent
    response = await test_client.delete(f"{BASE_URL}/131313", headers=headers)
    assert response.status_code == 400
