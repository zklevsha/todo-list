import sys
import os
from typing import AsyncIterator
import pytest
from fastapi.testclient import TestClient
import httpx
import pytest_asyncio
from httpx import ASGITransport
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from db import engine


sync_client = TestClient(app)

def test_root():
    response = sync_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the root endpoint."}

def test_test_route():
    response = sync_client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "This is another test route."}

@pytest.mark.asyncio
async def test_db_test_connection():
    response = sync_client.get("/db_test_connection")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

@pytest.mark.asyncio
async def test_db_schema_version(client: httpx.AsyncClient) -> None:
    response = await client.get("/db_schema_version")
    assert response.status_code == 200
    assert isinstance(response.json(), str)
    await engine.dispose()

@pytest.mark.asyncio
async def test_add_task(client: httpx.AsyncClient) -> None:
    todo_data = {"title": "Test todo", "description": "Test todo", "is_finished": False}
    response = await client.post("/add_task", json=todo_data)
    assert response.status_code == 201
    assert "status" in response.json()
    assert "message" in response.json()
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_all_tasks(client: httpx.AsyncClient) -> None:
    response = await client.get("/get_all_tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    await engine.dispose()

@pytest.mark.asyncio
async def test_get_task_by_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/get_task/13")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    await engine.dispose()

@pytest.mark.asyncio
async def test_update_task(client: httpx.AsyncClient) -> None:
    todo_data = {"title": "Updated Task", "description": "Updated Description", "is_finished": True}
    response = await client.put("/update_task/13", json=todo_data)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    await engine.dispose()
