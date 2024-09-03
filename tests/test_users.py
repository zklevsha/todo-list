"""
test_users.py
The module containing all user-related tests for the FastAPI application.
"""
from helpers import generate_creds, login, get_new_token, ADMIN_TOKEN
from schemas import UserOutput

BASE_URL = "/api/v1/users"
main_test_user = {}


async def test_get_user_by_id(test_client) -> None:
    """
    Testing getting a user by ID.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    auth_token = await get_new_token(test_client, base_url=BASE_URL, main_test_user=main_test_user)
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
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    new_username, new_email = generate_creds()
    new_data = {"username": new_username, "email": new_email}
    auth_token = await get_new_token(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=headers)
    returned_user: UserOutput = UserOutput.model_validate(response.json())
    assert response.status_code == 200
    assert isinstance(returned_user, UserOutput)

    no_auth_user = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data)
    assert no_auth_user.status_code == 401

    # Testing duplication
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=headers)
    assert response.status_code == 409


async def test_change_user_role(test_client) -> None:
    """
    Testing changing the role of a user.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    role_data = {"role": "admin"}
    auth_token = await get_new_token(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data, headers=headers)
    assert response.status_code == 403

    no_auth_user = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data)
    assert no_auth_user.status_code == 401

    # Testing non-existent
    response = await test_client.patch(f"{BASE_URL}/131313", json=role_data, headers=headers)
    assert response.status_code == 400

    # Testing with the admin user.
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    response = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data, headers=headers)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()


async def test_get_all_users(test_client) -> None:
    """
    Testing the endpoint to get all users (only admin can use it).
    """
    auth_token = await get_new_token(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/", headers=headers)
    assert response.status_code == 403

    no_auth_user = await test_client.get(f"{BASE_URL}/")
    assert no_auth_user.status_code == 401

    # Testing with the admin user.
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    response = await test_client.get(f"{BASE_URL}/", headers=headers)
    assert response.status_code == 200


async def test_delete_user(test_client) -> None:
    """
    Testing deleting a user.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    auth_token = await get_new_token(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.delete(f"{BASE_URL}/{user_id}", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    no_auth_user = await test_client.delete(f"{BASE_URL}/{user_id}")
    assert no_auth_user.status_code == 401

    # Testing non-existent
    response = await test_client.delete(f"{BASE_URL}/131313", headers=headers)
    assert response.status_code == 400
