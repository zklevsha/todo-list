"""
test_users.py
The module containing all user-related tests for the FastAPI application.
"""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import time_machine
from conftest import test_async_session as t_session
from helpers import generate_creds, login, get_new_token, \
    ADMIN_TOKEN, generate_new_user, TaskState, Headers
from schemas import UserOutput
from scheduler.scheduler import scheduler_main

BASE_URL = "/api/v1/users"
main_test_user = {}
header = Headers()
task_state = TaskState()
TZ = ZoneInfo("UTC")


async def test_register_user_admin(test_client) -> None:
    """
    Testing registering a new user with the "admin" role.
    """
    user, email = generate_creds()
    user_data = {"username": user, "email": email, "password": "test", "role": "admin"}
    response = await test_client.post(f"{BASE_URL}/register", json=user_data)
    parsed_response = response.json()

    # The user should be properly created, but the role will be forced to be "user".
    assert response.status_code == 200
    assert parsed_response['user']['role'] == "user"


async def test_get_user_by_id(test_client) -> None:
    """
    Testing getting a user by ID.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    response = await test_client.get(f"{BASE_URL}/{user_id}", headers=header.headers)
    returned_user: UserOutput = UserOutput.model_validate(response.json())
    assert response.status_code == 200
    assert isinstance(returned_user, UserOutput)
    no_user = await test_client.get(f"{BASE_URL}/131313", headers=header.headers)
    assert no_user.status_code == 404


async def test_update_user(test_client) -> None:
    """
    Testing updating a user.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    new_username, new_email = generate_creds()
    new_data = {"username": new_username, "email": new_email}
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=header.headers)
    returned_user: UserOutput = UserOutput.model_validate(response.json())
    assert response.status_code == 200
    assert isinstance(returned_user, UserOutput)

    no_auth_user = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data)
    assert no_auth_user.status_code == 401

    # Testing duplication
    response = await test_client.put(f"{BASE_URL}/{user_id}", json=new_data, headers=header.headers)
    assert response.status_code == 409


async def test_change_user_role(test_client) -> None:
    """
    Testing changing the role of a user.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id
    role_data = {"role": "admin"}
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    response = await test_client.patch(f"{BASE_URL}/{user_id}",
                                       json=role_data, headers=header.headers)
    assert response.status_code == 403

    no_auth_user = await test_client.patch(f"{BASE_URL}/{user_id}", json=role_data)
    assert no_auth_user.status_code == 401

    # Testing non-existent
    response = await test_client.patch(f"{BASE_URL}/131313",
                                       json=role_data, headers=header.headers)
    assert response.status_code == 400

    # Testing with the admin user.
    header.auth_token = ADMIN_TOKEN
    response = await test_client.patch(f"{BASE_URL}/{user_id}",
                                       json=role_data, headers=header.headers)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()


async def test_get_all_users(test_client) -> None:
    """
    Testing the endpoint to get all users (only admin can use it).
    """
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    response = await test_client.get(f"{BASE_URL}/", headers=header.headers)
    assert response.status_code == 403

    no_auth_user = await test_client.get(f"{BASE_URL}/")
    assert no_auth_user.status_code == 401

    # Testing with the admin user.
    header.auth_token = ADMIN_TOKEN
    response = await test_client.get(f"{BASE_URL}/", headers=header.headers)
    assert response.status_code == 200


async def test_set_reminders(test_client) -> None:
    """
    Testing the endpoint to set the daily reminders.
    """
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    json_data = {"reminder": "true"}
    response = await test_client.post(f"{BASE_URL}/reminders",
                                      json=json_data, headers=header.headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    # Testing when the reminders are already enabled
    response = await test_client.post(f"{BASE_URL}/reminders",
                                      json=json_data, headers=header.headers)
    assert response.status_code == 400
    assert isinstance(response.json(), dict)

    no_auth_user = await test_client.post(f"{BASE_URL}/reminders", json=json_data)
    assert no_auth_user.status_code == 401


async def test_send_reminders(test_client) -> None:
    """
    Testing the endpoint to set the daily reminders.
    """
    json_data = {"timezone": 'UTC'}
    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)
    response = await test_client.post(f"{BASE_URL}/send_reminders",
                                      json=json_data, headers=header.headers)
    assert response.status_code == 403

    no_auth_user = await test_client.post(f"{BASE_URL}/reminders", json=json_data)
    assert no_auth_user.status_code == 401

    header.auth_token = ADMIN_TOKEN
    response = await test_client.post(f"{BASE_URL}/send_reminders",
                                      json=json_data, headers=header.headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


async def test_delete_user(test_client) -> None:
    """
    Testing deleting a user.
    """
    user = await login(test_client, base_url=BASE_URL, main_test_user=main_test_user)
    user_id = user.user.id

    header.auth_token = await get_new_token(test_client,
                                            base_url=BASE_URL, main_test_user=main_test_user)

    no_auth_user = await test_client.delete(f"{BASE_URL}/{user_id}")
    assert no_auth_user.status_code == 401

    response = await test_client.delete(f"{BASE_URL}/{user_id}", headers=header.headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    # Testing non-existent
    response = await test_client.delete(f"{BASE_URL}/131313", headers=header.headers)
    assert response.status_code == 400

    # Testing deletion by an admin
    user = await generate_new_user(test_client, base_url=BASE_URL)
    user_id = user.user.id
    header.auth_token = ADMIN_TOKEN
    response = await test_client.delete(f"{BASE_URL}/{user_id}", headers=header.headers)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


async def support_scheduler(tz, test_client) -> None:
    """
    Function that substitutes 'send_reminders_to_users'
    to test the scheduler functionality.
    """
    json_data = {"timezone": tz}
    header.auth_token = ADMIN_TOKEN
    response = await test_client.post(f"{BASE_URL}/send_reminders",
                                      json=json_data, headers=header.headers)
    task_state.task_executed = True
    print(f"Reminders sent, status code: {response.status_code}")


@time_machine.travel(datetime(2024, 9, 21, 8, 59, 59, tzinfo=TZ))
async def test_scheduler_main(test_client) -> None:
    """
    Function to test the scheduler. Here, the time is modified
    with time_machine to trigger execution. A flag 'task_executed'
    is used to track the status of the task to be able to assert it.
    A brief timeout (2 s) is given before checking.
    """
    await scheduler_main(support_scheduler, test_client, t_session)
    await asyncio.sleep(2)
    assert task_state.task_executed, "Scheduler did not execute the task"
