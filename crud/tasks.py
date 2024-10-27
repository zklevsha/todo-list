"""
crud.py
Module to handle all CRUD operations related
to the tasks endpoints.
"""
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from models import Todo
from crud.helpers import handle_errors, get_current_time, raise_helper


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
async def crud_add_todo(todo: dict, user_id, db: AsyncSession):
    """
    Function to insert a new task into the "todos" table.
    
    Returns:
        Status code and message of the transaction. 
    """
    creation_date = get_current_time()
    todo.update({"user_id": user_id})
    todo.update({"creation_date": creation_date})

    new_task = Todo(**todo)
    db.add(new_task)
    query = sa.select(Todo.id).order_by(Todo.id.desc()).limit(1)
    result = await db.execute(query)
    task_id = result.scalar()
    await db.commit()
    return {'status': 'success',
            'message': f'Task {task_id} added successfully.'}


@handle_errors
async def crud_update_todo(task_id: int, user_id, user_role, todo: dict, db: AsyncSession):
    """
    Function to update an existing task in the "todos" table.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    existing_task = result.scalar()

    if existing_task is None:
        raise_helper(404, "Task", task_id)
    if existing_task.user_id != user_id and user_role != 'admin':
        raise_helper(401)

    updated_task = (sa.update(Todo).where(Todo.id == task_id).values(**todo))
    await db.execute(updated_task)

    await db.commit()
    return {'status': 'success', 'message': 'Task updated successfully.'}


@handle_errors
async def crud_get_all_todos(user_id, user_role, db: AsyncSession):
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
        raise_helper(200)
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
async def crud_delete_todo(task_id, user_id, db: AsyncSession):
    """
    Function to delete an existing task in the "todos" table.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    task_to_delete = result.scalar()
    if not task_to_delete:
        raise_helper(404, "Task", task_id)
    if task_to_delete.user_id != user_id:
        raise_helper(401)

    await db.delete(task_to_delete)
    await db.commit()
    return {'status': 'success', 'message': 'Task deleted successfully.'}


@handle_errors
async def crud_get_task_by_id(task_id, user_id, user_role, db: AsyncSession):
    """
    Function to get a "todo" matching the provided ID.
    
    Returns:
        The task. If error, returns status code and error message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    todo = result.scalar()
    if todo is None:
        raise_helper(404, "Task", task_id)

    if todo.user_id != user_id and user_role != 'admin':
        raise_helper(401)

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
async def crud_toggle_task_completion(task_id: int, user_id, user_role,
                                      is_finished: bool, db: AsyncSession):
    """
    Function to mark a matching "todo" as completed (or not).
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(Todo).where(Todo.id == task_id)
    result = await db.execute(query)
    todo = result.scalar()
    if todo is None:
        raise_helper(404, "Task", task_id)

    if todo.is_finished == is_finished:
        status = "completed" if is_finished else "pending"
        raise_helper(422, "Task", status)

    if todo.user_id != user_id and user_role != 'admin':
        raise_helper(401)

    completed_task = (
        sa.update(Todo).where(Todo.id == task_id).values(is_finished=is_finished)
    )
    await db.execute(completed_task)
    await db.commit()
    return {'status': 'success', 'message': f'Task {task_id} successfully set.'}
