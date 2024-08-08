"""
tasks.py
Routes are configured for the tasks endpoints.
"""
from typing import Union
from fastapi import APIRouter, Depends
from crud import create_todo_task, update_todo_task, get_all_todo_tasks, \
    get_todo_task_by_id, delete_todo_task, mark_todo_task_completed
from schemas import ConnectionResponse, TodoData, IsFinished
from routers.db_functions import get_db, AsyncSession


router = APIRouter()


@router.get("/")
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


@router.post("/", status_code=201)
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
