"""
crud.py
This module handles all the functions called by the app.py module, 
as well as managing the functionality of the DB operations for the to-do list.
"""
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db import async_session, engine
from models import Todos

async def connect_test():
    """
    Test the connection to the DB.
    
    Returns:
        Connection status.
    """
    try:
        async with engine.connect():
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

async def get_schema():
    """
    Function to get the schema version.
    
    Returns:
        A string from the Alembic_verstion table. 
    """
    async with async_session() as session:
        query = text("SELECT version_num FROM alembic_version;")
        result = await session.execute(query)
        version_num = result.scalar()
        return version_num


async def create_todo_task(todo: dict):
    """
    Function to insert a new task into the "todos" table.
    
    Returns:
        Status code and message of the transaction. 
    """
    async with async_session() as session:
        try:
            async with session.begin():
                new_task = Todos(**todo)
                session.add(new_task)
                await session.commit()
                return {'status': 'success', 'message': 'Task added successfully.'}
        except SQLAlchemyError as error:
            return {'status': 'error', 'message': str(error)}
        finally:
            await session.close()


async def update_todo_task(task_id: int, todo: dict):
    """
    Function to update an existing task in the "todos" table.
    
    Returns:
        Status code and message of the transaction.
    """
    async with async_session() as session:
        try:
            async with session.begin():
                s_query = sa.select(Todos).where(Todos.id == task_id)
                query = await session.execute(s_query)
                existing_task = query.scalar()
                if existing_task is None:
                    raise HTTPException(
                        400, detail=['Unable modify a resource that does not exist.']
                    )

                updated_task = (sa.update(Todos).where(Todos.id == task_id).values(**todo))
                await session.execute(updated_task)

                await session.commit()
                return {'status': 'success', 'message': 'Task updated successfully.'}
        except SQLAlchemyError as error:
            return {'status': 'error', 'message': str(error)}
        finally:
            await session.close()



async def get_all_todo_tasks():
    """
    Function to get all existing task in the "todos" table.
    
    Returns:
        A list of all todos. If error, returns status code and error message of the transaction.
    """
    async with async_session() as session:
        try:
            async with session.begin():
                query = sa.select(Todos)
                result = await session.execute(query)
                todos = result.scalars().all()
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
        except SQLAlchemyError as error:
            raise HTTPException(500, detail=[str(error)]) from error
        finally:
            await session.close()


async def get_task_by_id(task_id):
    """
    Function to get a "todo" matching the provided ID.
    
    Returns:
        A list of the task. If error, returns status code and error message of the transaction.
    """
    async with async_session() as session:
        try:
            async with session.begin():
                s_query = sa.select(Todos).where(Todos.id == task_id)
                query = await session.execute(s_query)
                todo = query.scalar()
                if todo is None:
                    raise HTTPException(400, detail=f'Task with ID {task_id} does not exist.')

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
        except SQLAlchemyError as error:
            raise HTTPException(500, detail=[str(error)]) from error
        finally:
            await session.close()
