"""
test_tasks.py
The module containing all task-related tests for the FastAPI application.
"""
import re
from fastapi.testclient import TestClient
from conftest import app
from helpers import get_new_token, Headers, ADMIN_TOKEN

sync_client = TestClient(app)
BASE_URL = "/api/v1/tasks"
USER_API_URL = "/api/v1/users"
main_test_user = {}
secondary_test_user = {}
header = Headers()


async def get_a_task_id(test_client, todo_data):
    """
    Function to add a new task to the database and get its ID.
    """
    header.auth_token = await get_new_token(test_client,
                                            base_url=USER_API_URL, main_test_user=main_test_user)
    put_response = await test_client.post(f"{BASE_URL}/", json=todo_data, headers=header.headers)
    match = re.search(r'Task (\d+) added successfully', put_response.json()['message'])
    task_id = match.group(1)
    return task_id


def test_root():
    """
    Testing the root endpoint of the app.
    """
    response = sync_client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {'message': 'This is the root endpoint.', 'status': 'Success'}


async def test_db_schema_version(test_client) -> None:
    """
    Testing getting the db_schema_version from the test db.
    """
    response = await test_client.get("/api/v1/schema")
    assert response.status_code == 200
    assert isinstance(response.json(), str)


async def test_get_all_todos(test_client) -> None:
    """
    Testing getting all tasks.
    """
    # Testing with an empty list
    header.auth_token = await get_new_token(test_client,
                                            base_url=USER_API_URL, main_test_user=main_test_user)
    response = await test_client.get(f"{BASE_URL}/", headers=header.headers)
    no_auth_response = await test_client.get(f"{BASE_URL}/")

    if isinstance(response.json(), dict):
        assert response.status_code == 200
        assert response.json() == {"detail": "The Todo list is empty."}
    else:
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    assert no_auth_response.status_code == 401


async def test_get_task_by_id(test_client) -> None:
    """
    Testing getting a task by ID.
    """
    todo_data = {"title": "Testing_get_task_by_id",
                 "description": "Description_get_by_id", "is_finished": True}
    task_id = await get_a_task_id(test_client, todo_data)
    response = await test_client.get(f"{BASE_URL}/{task_id}", headers=header.headers)
    no_auth_response = await test_client.get(f"{BASE_URL}/{task_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert no_auth_response.status_code == 401

    # Testing getting a non-existent task by ID.
    response_missing = await test_client.get(f"{BASE_URL}/131313", headers=header.headers)
    no_auth_response_missing = await test_client.get(f"{BASE_URL}/131313")
    assert response_missing.status_code == 404
    assert response_missing.json() == {"detail": "Task with ID 131313 not found."}
    assert no_auth_response_missing.status_code == 401


async def test_add_todo(test_client) -> None:
    """
    Testing adding a new task to the DB.
    """
    header.auth_token = await get_new_token(test_client,
                                            base_url=USER_API_URL, main_test_user=main_test_user)
    todo_data = {"title": "Testing_add_todo",
                 "description": "Description_add", "is_finished": False}
    response = await test_client.post(f"{BASE_URL}/", json=todo_data, headers=header.headers)
    no_auth_response = await test_client.post(f"{BASE_URL}/", json=todo_data)
    assert response.status_code == 201
    assert "status" in response.json()
    assert "message" in response.json()
    assert no_auth_response.status_code == 401

    # Testing adding a new incomplete task to the DB.
    bad_todo_data = {"title": "Testing_add_todo", "is_finished": False}
    bad_response = await test_client.post(f"{BASE_URL}/",
                                          json=bad_todo_data, headers=header.headers)
    bad_no_auth_response = await test_client.post(f"{BASE_URL}/", json=bad_todo_data)
    assert bad_response.status_code == 422
    assert "detail" in bad_response.json()
    expected_error = [
        {
            'input': {'is_finished': False, 'title': 'Testing_add_todo'},
            'loc': ['body', 'description'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert bad_response.json()["detail"] == expected_error
    assert bad_no_auth_response.status_code == 401


async def test_update_todo(test_client) -> None:
    """
    Testing updating a task.
    """
    todo_data = {"title": "Task", "description": "Description_update", "is_finished": True}
    updated_todo_data = {"title": "Testing_update_task", "description": "Updated_description",
                         "is_finished": True}
    task_id = await get_a_task_id(test_client, todo_data)
    response = await test_client.put(f"{BASE_URL}/{task_id}",
                                     json=updated_todo_data, headers=header.headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}",
                                             json=updated_todo_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    assert no_auth_response.status_code == 401

    # Testing incorrectly updating a task.
    bad_updated_todo_data = {"description": "Updated Description", "is_finished": True}
    bad_response = await test_client.put(f"{BASE_URL}/{task_id}",
                                         json=bad_updated_todo_data, headers=header.headers)
    bad_no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}",
                                                 json=bad_updated_todo_data)
    assert bad_response.status_code == 422
    assert "detail" in bad_response.json()
    expected_error = [
        {
            'input': {'description': 'Updated Description', 'is_finished': True},
            'loc': ['body', 'title'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert bad_response.json()["detail"] == expected_error
    assert bad_no_auth_response.status_code == 401

    # Testing the transaction with another user.
    header.auth_token = await get_new_token(test_client=test_client,
                                            base_url=USER_API_URL,
                                            main_test_user=secondary_test_user)
    response = await test_client.put(f"{BASE_URL}/{task_id}",
                                     json=updated_todo_data, headers=header.headers)
    assert response.status_code == 401
    assert "detail" in response.json()
    expected_error = 'You are not authorized to perform this action.'
    assert response.json()["detail"] == expected_error

    # Testing with the admin user.
    header.auth_token = ADMIN_TOKEN
    response = await test_client.put(f"{BASE_URL}/{task_id}",
                                     json=updated_todo_data, headers=header.headers)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()


async def test_delete_todo(test_client) -> None:
    """
    Testing deleting a task.
    """
    todo_data = {"title": "Testing_delete_todo",
                 "description": "Description_delete", "is_finished": False}
    task_id = await get_a_task_id(test_client, todo_data)
    response = await test_client.delete(f"{BASE_URL}/{task_id}", headers=header.headers)
    no_auth_response = await test_client.delete(f"{BASE_URL}/{task_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert no_auth_response.status_code == 401

    # Testing deleting a non-existent entry.
    missing_response = await test_client.delete(f"{BASE_URL}/131313", headers=header.headers)
    missing_no_auth_response = await test_client.delete(f"{BASE_URL}/131313")
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Task with ID 131313 not found."}
    assert missing_no_auth_response.status_code == 401

    # Testing the transaction with another user.
    task_id = await get_a_task_id(test_client, todo_data)
    header.auth_token = await get_new_token(test_client=test_client,
                                            base_url=USER_API_URL,
                                            main_test_user=secondary_test_user)
    response = await test_client.delete(f"{BASE_URL}/{task_id}", headers=header.headers)
    assert response.status_code == 401
    assert "detail" in response.json()
    expected_error = 'You are not authorized to perform this action.'
    assert response.json()["detail"] == expected_error


async def test_toggle_task_completion(test_client) -> None:
    """
    Testing the 'finish' endpoint.
    """
    todo_data = {"title": "Testing_is_finished",
                 "description": "Description_mark_completed", "is_finished": "false"}
    task_id = await get_a_task_id(test_client, todo_data)
    is_finished_data = {"is_finished": "true"}
    response = await test_client.put(f"{BASE_URL}/{task_id}/finish",
                                     json=is_finished_data, headers=header.headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}/finish",
                                             json=is_finished_data)
    assert response.status_code == 200
    assert "message" in response.json()
    assert no_auth_response.status_code == 401

    # Testing the finish endpoint with a non-existent record.
    missing_response = await test_client.put(f"{BASE_URL}/131313/finish",
                                             json=is_finished_data, headers=header.headers)
    missing_no_auth_response = await test_client.put(f"{BASE_URL}/131313/finish",
                                                     json=is_finished_data)
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Task with ID 131313 not found."}
    assert missing_no_auth_response.status_code == 401
