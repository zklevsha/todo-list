"""
tasks.py
Routes are configured for the tasks endpoints.
"""
from typing import Union
from fastapi import APIRouter, Depends
from crud.tasks import create_todo_task, update_todo_task, get_all_todo_tasks, \
    get_todo_task_by_id, delete_todo_task, mark_todo_task_completed
from schemas import ConnectionResponse, TodoData, IsFinished
from routers.db_functions import get_db, AsyncSession
from oauth import get_current_user

router = APIRouter()


async def get_user_id(user_data: tuple = Depends(get_current_user)) -> int:
    """
    Function to get the ID of the user making the request.
    
    Returns:
       Returns the user ID.
    """
    user_id, _ = user_data
    return user_id


async def get_user_role(user_data: tuple = Depends(get_current_user)) -> str:
    """
    Function to get the role of the user making the request.
    
    Returns:
       Returns the user role.
    """
    _, user_role = user_data
    return user_role


@router.get("/")
async def get_all_todos(db: AsyncSession = Depends(get_db),
                        user_id: int = Depends(get_user_id),
                        user_role: str = Depends(get_user_role)) -> Union[list, dict]:
    """
    Endpoint to get the list of all todos.
    
    Returns:
       Returns the list of elements.
    """
    result = await get_all_todo_tasks(user_id=user_id, user_role=user_role, db=db)
    return result


@router.get("/{task_id}")
async def get_task_id(task_id: int, db: AsyncSession = Depends(get_db),
                      user_id: int = Depends(get_user_id),
                      user_role: str = Depends(get_user_role)) -> Union[list, dict]:
    """
    Endpoint to get a specific todo by ID.
    
    Returns:
       Returns the a list with the info of the todo.
    """
    result = await get_todo_task_by_id(task_id=task_id, user_id=user_id, user_role=user_role, db=db)
    return result


@router.post("/", status_code=201)
async def add_todo(todo: TodoData, db: AsyncSession = Depends(get_db),
                   user_id: int = Depends(get_user_id)) -> ConnectionResponse:
    """
    Endpoint to add a new todo task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    todo_dump = todo.model_dump()
    result = await create_todo_task(todo=todo_dump, user_id=user_id, db=db)
    return result


@router.put("/{task_id}", status_code=200)
async def update_todo(task_id: int, todo: TodoData,
                      db: AsyncSession = Depends(get_db), user_id: int = Depends(get_user_id),
                      user_role: str = Depends(get_user_role)) -> ConnectionResponse:
    """
    Endpoint to update an existing todo task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    todo_dump = todo.model_dump()
    result = await update_todo_task(task_id=task_id, user_id=user_id,
                                    user_role=user_role, todo=todo_dump, db=db)
    return result


@router.delete("/{task_id}", status_code=200)
async def delete_todo(task_id: int,
                      db: AsyncSession = Depends(get_db), user_id: int = Depends(get_user_id),
                      user_role: str = Depends(get_user_role)) -> ConnectionResponse:
    """
    Endpoint to remove an existing todo task.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    result = await delete_todo_task(task_id=task_id, user_id=user_id, user_role=user_role, db=db)
    return result


@router.put("/{task_id}/finish", status_code=200)
async def mark_completed(task_id: int, finished: IsFinished,
                         db: AsyncSession = Depends(get_db), user_id: int = Depends(get_user_id),
                         user_role: str = Depends(get_user_role)) -> ConnectionResponse:
    """
    Endpoint to mark an existing todo task as completed, or not.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the transaction (id, status and message).
    """
    is_finished = finished.model_dump()['is_finished']
    result = await mark_todo_task_completed(task_id=task_id, user_id=user_id,
                                            user_role=user_role, finished=is_finished, db=db)
    return result
