"""
test_tasks.py
The module containing all task-related tests for the FastAPI application.
"""
from fastapi.testclient import TestClient
from conftest import app, get_db, get_engine, generate_creds #pylint: disable=W0611
from test_users import get_new_token
#Both get_db and get_engine are referenced in the
#dependency injection, so they need to be imported.


sync_client = TestClient(app)
BASE_URL = "/api/v1/tasks"

async def get_a_task_id(test_client, todo_data):
    """
    Function to add a new task to the database and get its ID.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    put_response = await test_client.post(f"{BASE_URL}/", json=todo_data, headers=headers)
    task_id = put_response.json()['task_id']
    return task_id, auth_token


def test_root():
    """
    Testing the root endpoint of the app.
    """
    response = sync_client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the root endpoint."}


def test_test_route():
    """
    Testing the 'test route' endpoint of the app.
    """
    response = sync_client.get("/api/v1/test")
    assert response.status_code == 200
    assert response.json() == {"message": "This is another test route."}


async def test_db_test_connection(test_client) -> None:
    """
    Testing the testing of db connection for the app.
    """
    response = await test_client.get("/api/v1/db-connection")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()


async def test_db_schema_version(test_client) -> None:
    """
    Testing getting the db_schema_version from the test db.
    """
    response = await test_client.get("/api/v1/schema")
    assert response.status_code == 200
    assert isinstance(response.json(), str)


async def test_get_all_tasks(test_client) -> None:
    """
    Testing getting all tasks.
    """
    #Testing with an empty list
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/", headers=headers)
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
    task_id, auth_token = await get_a_task_id(test_client, todo_data)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/{task_id}", headers=headers)
    no_auth_response = await test_client.get(f"{BASE_URL}/{task_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert no_auth_response.status_code == 401


async def test_bad_get_task_by_id(test_client) -> None:
    """
    Testing getting a non-existent task by ID.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.get(f"{BASE_URL}/131313", headers=headers)
    no_auth_response = await test_client.get(f"{BASE_URL}/131313")
    assert response.status_code == 400
    assert response.json() == {"detail": "Task with ID 131313 does not exist."}
    assert no_auth_response.status_code == 401

async def test_add_task(test_client) -> None:
    """
    Testing adding a new task to the DB.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    todo_data = {"title": "Testing_add_todo",
    "description": "Description_add", "is_finished": False}
    response = await test_client.post(f"{BASE_URL}/", json=todo_data, headers=headers)
    no_auth_response = await test_client.post(f"{BASE_URL}/", json=todo_data)
    assert response.status_code == 201
    assert "status" in response.json()
    assert "message" in response.json()
    assert no_auth_response.status_code == 401


async def test_bad_add_task(test_client) -> None:
    """
    Testing adding a new incomplete task to the DB.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    todo_data = {"title": "Testing_add_todo", "is_finished": False}
    response = await test_client.post(f"{BASE_URL}/", json=todo_data, headers=headers)
    no_auth_response = await test_client.post(f"{BASE_URL}/", json=todo_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    expected_error = [
        {
            'input': {'is_finished': False, 'title': 'Testing_add_todo'}, 
            'loc': ['body', 'description'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert response.json()["detail"] == expected_error
    assert no_auth_response.status_code == 401


async def test_update_task(test_client) -> None:
    """
    Testing updating a task.
    """
    todo_data = {"title": "Task", "description": "Description_update", "is_finished": True}
    updated_todo_data = {"title": "Testing_update_task", "description": "Updated_description",
                        "is_finished": True}
    task_id, auth_token = await get_a_task_id(test_client, todo_data)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.put(f"{BASE_URL}/{task_id}",
                json=updated_todo_data, headers=headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}",
                json=updated_todo_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    assert no_auth_response.status_code == 401


async def test_bad_update_task(test_client) -> None:
    """
    Testing incorrectly updating a task.
    """
    todo_data = {"title": "Testing_bad_update_task", "description": "Description_bad_update",
                "is_finished": True}
    updated_todo_data = {"description": "Updated Description", "is_finished": True}
    task_id, auth_token = await get_a_task_id(test_client, todo_data)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.put(f"{BASE_URL}/{task_id}",
                json=updated_todo_data, headers=headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}",
                json=updated_todo_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    expected_error = [
        {
            'input': {'description': 'Updated Description', 'is_finished': True}, 
            'loc': ['body', 'title'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert response.json()["detail"] == expected_error
    assert no_auth_response.status_code == 401


async def test_delete_task(test_client) -> None:
    """
    Testing deleting a task.
    """
    todo_data = {"title": "Testing_delete_todo",
    "description": "Description_delete", "is_finished": False}
    task_id, auth_token = await get_a_task_id(test_client, todo_data)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.delete(f"{BASE_URL}/{task_id}", headers=headers)
    no_auth_response = await test_client.delete(f"{BASE_URL}/{task_id}")
    assert response.status_code == 200
    assert "message" in response.json()
    assert no_auth_response.status_code == 401


async def test_bad_delete_task(test_client) -> None:
    """
    Testing deleting a non-existent entry.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    response = await test_client.delete(f"{BASE_URL}/131313", headers=headers)
    no_auth_response = await test_client.delete(f"{BASE_URL}/131313")
    assert response.status_code == 400
    assert response.json() == {"detail": "Task with ID 131313 does not exist. Can\'t delete"}
    assert no_auth_response.status_code == 401


async def test_finish(test_client) -> None:
    """
    Testing the 'finish' endpoint.
    """
    todo_data = {"title": "Testing_is_finished",
    "description": "Description_mark_completed", "is_finished": False}
    task_id, auth_token = await get_a_task_id(test_client, todo_data)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    is_finished_data = {"is_finished": "true"}
    response = await test_client.put(f"{BASE_URL}/{task_id}/finish",
                json=is_finished_data, headers=headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/{task_id}/finish",
                json=is_finished_data)
    assert response.status_code == 200
    assert "message" in response.json()
    assert no_auth_response.status_code == 401


async def test_bad_finish(test_client) -> None:
    """
    Testing the finish endpoint with a non-existent record.
    """
    auth_token = await get_new_token(test_client=test_client)
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    is_finished_data = {"is_finished": "true"}
    response = await test_client.put(f"{BASE_URL}/131313/finish",
                json=is_finished_data, headers=headers)
    no_auth_response = await test_client.put(f"{BASE_URL}/131313/finish",
                json=is_finished_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Task with ID 131313 does not exist."}
    assert no_auth_response.status_code == 401
