"""
app.py
The main FastAPI application for the project. Here, the FastAPI instance is created, 
and routes are configured.
"""
from typing import Union
from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from db import async_session, engine
from crud import connect_test, get_schema, create_todo_task, \
    update_todo_task, get_all_todo_tasks, get_todo_task_by_id, delete_todo_task, \
    mark_todo_task_completed
from schemas import ConnectionResponse, BasicResponse, TodoData, IsFinished


async def get_db() -> AsyncSession:
    """
    Provides a new database session for each request.
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_engine() -> AsyncEngine:
    """
    Returns the database engine instance.
    """
    return engine

app = FastAPI()
router = APIRouter(prefix="/api/v1/tasks")

@app.get("/api/v1/")
async def root_test() -> BasicResponse:
    """
    Root endpoint for testing the API.
    
    Returns:
        BasicResponse: Simple test message.
    """
    return BasicResponse(message="This is the root endpoint.")


@app.get("/api/v1/test")
async def test_route() -> BasicResponse:
    """
    Another test route for the API.
    
    Returns:
        BasicResponse: Another simple test message.
    """
    return BasicResponse(message="This is another test route.")


@app.get("/api/v1/db-connection", status_code=200)
async def testing_connection(engine_main: AsyncEngine = Depends(get_engine)) -> ConnectionResponse:
    """
    Endpoint to test the DB connection.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the connection (status and message).
    """
    result = await connect_test(engine_main)
    return ConnectionResponse(**result)


@app.get("/api/v1/schema", status_code=200)
async def get_schema_version(db: AsyncSession = Depends(get_db)) -> str:
    """
    Endpoint to get the current database schema version (Alembic).
    
    Returns:
        str: The current database schema version.
    """
    result = await get_schema(db)
    return result


@router.get("")
async def get_all_todos(db: AsyncSession = Depends(get_db)) -> Union[list, dict]:
    """
    Endpoint to get the list of all 'todos'.
    
    Returns:
       Returns the list of elements.
    """
    result = await get_all_todo_tasks(db)
    return result


@router.get("/{task_id}")
async def get_task_id(task_id: int, db: AsyncSession = Depends(get_db)) -> Union[list, dict]:
    """
    Endpoint to get a specific 'todo' by ID.
    
    Returns:
       Returns the a list with the info of the todo.
    """
    result = await get_todo_task_by_id(task_id, db)
    return result


@router.post("", status_code=201)
async def add_todo(todo: TodoData, db: AsyncSession = Depends(get_db)) -> ConnectionResponse:
    """
    Endpoint to add a new 'todo' task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    todo_dump = todo.model_dump()
    result = await create_todo_task(todo_dump, db)
    return result


@router.put("/{task_id}", status_code=200)
async def update_todo(task_id: int, todo: TodoData, \
    db: AsyncSession = Depends(get_db)) -> ConnectionResponse:
    """
    Endpoint to update an existing 'todo' task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    todo_dump = todo.model_dump()
    result = await update_todo_task(task_id, todo_dump, db)
    return result


@router.delete("/{task_id}", status_code=200)
async def delete_todo(task_id: int,
    db: AsyncSession = Depends(get_db)) -> ConnectionResponse:
    """
    Endpoint to remove an existing 'todo' task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    result = await delete_todo_task(task_id, db)
    return result


@router.put("/{task_id}/finish", status_code=200)
async def mark_completed(task_id: int, finished: IsFinished,
    db: AsyncSession = Depends(get_db)) -> ConnectionResponse:
    """
    Endpoint to mark an existing 'todo' task as completed, or not.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    is_finished = finished.model_dump()['is_finished']
    result = await mark_todo_task_completed(task_id, is_finished, db)
    return result


app.include_router(router)
