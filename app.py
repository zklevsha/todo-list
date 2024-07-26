"""
app.py
The main FastAPI application for the project. Here, the FastAPI instance is created, 
and routes are configured.
"""
from typing import Union
from fastapi import FastAPI
from crud import connect_test, get_schema, create_todo_task, \
    update_todo_task, get_all_todo_tasks, get_task_by_id
from schemas import ConnectionResponse, BasicResponse, Todo


app = FastAPI()

@app.get("/")
async def root_test() -> BasicResponse:
    """
    Root endpoint for testing the API.
    
    Returns:
        BasicResponse: Simple test message.
    """
    return BasicResponse(message="This is the root endpoint.")


@app.get("/test")
async def test_route() -> BasicResponse:
    """
    Another test route for the API.
    
    Returns:
        BasicResponse: Another simple test message.
    """
    return BasicResponse(message="This is another test route.")


@app.get("/db_test_connection", status_code=200)
async def testing_connection() -> ConnectionResponse:
    """
    Endpoint to test the DB connection.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the connection (status and message).
    """
    result = await connect_test()
    return ConnectionResponse(**result)


@app.get("/db_schema_version", status_code=200)
async def get_schema_version() -> str:
    """
    Endpoint to get the current database schema version (Alembic).
    
    Returns:
        str: The current database schema version.
    """
    result = await get_schema()
    return result


@app.post("/add_task", status_code=201)
async def add_todo(todo: Todo) -> ConnectionResponse:
    """
    Endpoint to add a new 'todo' task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (status and message).
    """
    todo_dump = todo.model_dump()
    result = await create_todo_task(todo_dump)
    return result


@app.put("/update_task/{task_id}", status_code=200)
async def update_todo(task_id: int, todo: Todo) -> ConnectionResponse:
    """
    Endpoint to add a update an existing 'todo' task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (status and message).
    """
    todo_dump = todo.model_dump()
    result = await update_todo_task(task_id, todo_dump)
    return result


@app.get("/get_all_tasks")
async def get_all_todos() -> Union[list, dict]:
    """
    Endpoint to get the list of all 'todos'.
    
    Returns:
       Returns the list of elements.
    """
    result = await get_all_todo_tasks()
    return result


@app.get("/get_task/{task_id}")
async def get_task_id(task_id: int) -> Union[list, dict]:
    """
    Endpoint to get a specific 'todo' by ID.
    
    Returns:
       Returns the a list with the info of the todo.
    """
    result = await get_task_by_id(task_id)
    return result
