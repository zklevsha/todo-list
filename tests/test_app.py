# pylint: disable=E0401
# pylint: disable=W0621
"""
test_app.py
The main module containing all tests for the FastAPI application.
"""
import sys
import os
from fastapi.testclient import TestClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conftest import test_client
from app import app


sync_client = TestClient(app)

def test_root():
    """
    Testing the root endpoint of the app.
    """
    response = sync_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the root endpoint."}

def test_test_route():
    """
    Testing the 'test route' endpoint of the app.
    """
    response = sync_client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "This is another test route."}

async def test_db_test_connection(test_client) -> None:
    """
    Testing the testing of db connection for the app :).
    """
    response = await test_client.get("/db_test_connection")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()

async def test_db_schema_version(test_client) -> None:
    """
    Testing getting the db_schema_version from the test db.
    """
    response = await test_client.get("/db_schema_version")
    assert response.status_code == 200
    assert isinstance(response.json(), str)

async def test_add_task(test_client) -> None:
    """
    Testing adding a new task to the DB via the 'add_task' endpoint.
    """
    todo_data = {"title": "Test todo", "description": "Test todo", "is_finished": False}
    response = await test_client.post("/add_task", json=todo_data)
    assert response.status_code == 201
    assert "status" in response.json()
    assert "message" in response.json()

async def test_bad_add_task(test_client) -> None:
    """
    Testing adding a new incomplete task to the DB via the 'add_task' endpoint.
    """
    todo_data = {"title": "Test todo", "is_finished": False}
    response = await test_client.post("/add_task", json=todo_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    expected_error = [
        {
            'input': {'is_finished': False, 'title': 'Test todo'}, 
            'loc': ['body', 'description'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert response.json()["detail"] == expected_error

async def test_update_task(test_client) -> None:
    """
    Testing updating a task via the 'update_task' endpoint.
    """
    todo_data = {"title": "Updated Task", "description": "Updated Description", "is_finished": True}
    response = await test_client.put("/update_task/1", json=todo_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()

async def test_bad_data_update_task(test_client) -> None:
    """
    Testing incorrectly updating a task via the 'update_task' endpoint.
    """
    todo_data = {"description": "Updated Description", "is_finished": True}
    response = await test_client.put("/update_task/1", json=todo_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    expected_error = [
        {
            'input': {'description': 'Updated Description', 'is_finished': True}, 
            'loc': ['body', 'title'], 'msg': 'Field required', 'type': 'missing'
        }
    ]
    assert response.json()["detail"] == expected_error

async def test_get_all_tasks(test_client) -> None:
    """
    Testing getting all tasks via the 'get_all_tasks' endpoint.
    """
    response = await test_client.get("/get_all_tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_task_by_id(test_client) -> None:
    """
    Testing getting a task by ID via the 'get_task_by_id' endpoint.
    """
    response = await test_client.get("/get_task/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_bad_get_task_by_id(test_client) -> None:
    """
    Testing getting a non-existent task by ID via the 'get_task_by_id' endpoint.
    """
    response = await test_client.get("/get_task/111")
    assert response.status_code == 400
    assert response.json() == {"detail": "Task with ID 111 does not exist."}
