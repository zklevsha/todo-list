"""
crud.py
This module handles all the functions called by the app.py module, 
as well as managing the functionality of the DB operations.
"""
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import text
from models import Todo
from crud.users import handle_errors

NO_ACCESS = 'You do not have permission to access this task.'


@handle_errors
async def connect_test(engine: AsyncEngine, db):  # pylint: disable=W0613 # Required for the handle_errors function
    """
    Test the connection to the DB.
    
    Returns:
        Connection status.
    """
    async with engine.connect():
        return {'status': 'success', 'message': 'Successfully connected to the server.'}


@handle_errors
async def get_schema(db: AsyncSession):
    """
    Function to get the schema version.
    
    Returns:
        A string from the Alembic_version table.
    """
    query = text("SELECT version_num FROM alembic_version;")
    result = await db.execute(query)
    version_num = result.scalar()
    return version_num


@handle_errors
async def create_todo_task(todo: dict, user_id, db: AsyncSession):
    """
    Function to insert a new task into the "todos" table.
    
    Returns:
        Status code and message of the transaction. 
    """
    todo.update({"user_id": user_id})
    new_task = Todo(**todo)
    db.add(new_task)
    query = sa.select(Todo.id).order_by(Todo.id.desc()).limit(1)
    result = await db.execute(query)
    task_id = result.scalar()
    await db.commit()
    return {'task_id': task_id, 'status': 'success',
            'message': f'Task with ID {task_id} added successfully.'}


@handle_errors
async def update_todo_task(task_id: int, user_id, user_role, todo: dict, db: AsyncSession):
    """
    Function to update an existing task in the "todos" table.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    existing_task = result.scalar()

    if existing_task is None:
        raise HTTPException(
            status_code=400, detail=['Unable modify a resource that does not exist.']
        )
    if existing_task.user_id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NO_ACCESS)

    updated_task = (sa.update(Todo).where(Todo.id == task_id).values(**todo))
    await db.execute(updated_task)

    await db.commit()
    return {'status': 'success', 'message': f'Task {task_id} updated successfully.'}


@handle_errors
async def get_all_todo_tasks(user_id, user_role, db: AsyncSession):
    """
    Function to get all existing task in the "todos" table.
    
    Returns:
        A list of all todos. If error, returns status code and error message of the transaction.
    """
    if user_role == "admin":
        query = sa.select(Todo)
    else:
        query = sa.select(Todo).where(Todo.user_id == user_id)
    result = await db.execute(query)
    todos = result.scalars().all()
    if not todos:
        raise HTTPException(status_code=200, detail='The Todo list is empty.')
    formatted_output = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "is_finished": todo.is_finished,
            "creation_date": todo.creation_date
        }
        for todo in todos
    ]
    return formatted_output


@handle_errors
async def delete_todo_task(task_id, user_id, user_role, db: AsyncSession):
    """
    Function to delete an existing task in the "todos" table.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    task_to_delete = result.scalar()
    if not task_to_delete:
        raise HTTPException(status_code=400,
                            detail=f'Task with ID {task_id} does not exist. Can\'t delete')
    if task_to_delete.user_id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NO_ACCESS)

    await db.delete(task_to_delete)
    await db.commit()
    return {'status': 'success', 'message': f'Task {task_id} deleted successfully.'}


@handle_errors
async def get_todo_task_by_id(task_id, user_id, user_role, db: AsyncSession):
    """
    Function to get a "todo" matching the provided ID.
    
    Returns:
        The task. If error, returns status code and error message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    todo = result.scalar()
    if todo is None:
        raise HTTPException(status_code=400,
                            detail=f'Task with ID {task_id} does not exist.')

    if todo.user_id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NO_ACCESS)

    formatted_output = [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "is_finished": todo.is_finished,
            "creation_date": todo.creation_date
        }
    ]
    return formatted_output


@handle_errors
async def mark_todo_task_completed(task_id: int, user_id, user_role,
                                   finished: bool, db: AsyncSession):
    """
    Function to mark a matching "todo" as completed (or not).
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    todo = result.scalar()
    if todo is None:
        raise HTTPException(status_code=400,
                            detail=f'Task with ID {task_id} does not exist.')
    if todo.is_finished and finished:
        raise HTTPException(status_code=200,
                            detail=f'Task with ID {task_id} is already set to completed.')
    if not todo.is_finished and not finished:
        raise HTTPException(status_code=200,
                            detail=f'Task with ID {task_id} is already set to pending.')
    if todo.user_id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NO_ACCESS)

    completed_task = (
        sa.update(Todo).where(Todo.id == task_id).values(is_finished=finished)
    )
    await db.execute(completed_task)
    await db.commit()
    return {'status': 'success', 'message': f'Task {task_id} successfully set.'}
