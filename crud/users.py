"""
users.py
This module handles all the functions called by the app.py module, 
but focused on user-related DB operations.
"""
import logging
from functools import wraps
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from models import User
from schemas import UserCreate, UserUpdate
from crypto import verify_password
from oauth import create_access_token

def handle_errors(func):
    """
    Decorator function to maintain consistent error handling.
    """
    @wraps(func)
    async def wrapper(*args, db, **kwargs):
        try:
            return await func(*args, db=db, **kwargs)
        except SQLAlchemyError as error:
            logging.error("SQLAlchemyError occurred: %s", error)
            raise HTTPException(
                status_code=500,
                detail='An internal server error occurred. Please try again later.'
            ) from error
        except HTTPException:
            #Raise the HTTPExceptions to avoid them for being
            # overwritten by the general Exception block
            raise
        except Exception as error:
            logging.error("An unexpected error occurred: %s", error)
            raise HTTPException(
                status_code=500,
                detail='An internal server error occurred. Please try again later.'
            ) from error
        finally:
            await db.close()

    return wrapper


@handle_errors
async def create_new_user(user: UserCreate, db: AsyncSession):
    """
    Function to add a new user into the "users" table.
    
    Returns:
        The new_user info. 
    """
    new_user = User(**user.model_dump())
    query = sa.select(User).where(
        or_(User.username == user.username, User.email == user.email)
    )
    result = await db.execute(query)
    user_exists = result.scalars().first()
    if user_exists:
        raise HTTPException(status_code=400,
        detail='The username or email is already in use.')

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@handle_errors
async def user_login(user_credentials: dict, db: AsyncSession):
    """
    Function to authenticate the user.
    
    Returns:
        A unique token for the user (if auth is successful). 
    """
    query = sa.select(User).where(User.username == user_credentials.username)
    result = await db.execute(query)
    user = result.scalar()
    if user is None:
        raise HTTPException(status_code=403, detail='Invalid credentials.')

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=403, detail='Invalid credentials.')

    access_token = create_access_token(data = {"user_id": user.id, "user_role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@handle_errors
async def get_existing_user(uid: int, db: AsyncSession):
    """
    Function to get an existing user by ID.
    
    Returns:
        The user info (if it exists). 
    """
    query = sa.select(User).where(User.id == uid)
    result = await db.execute(query)
    existing_user = result.scalar()
    if existing_user is None:
        raise HTTPException(status_code=404,
        detail=f'User with ID {uid} not found.')

    return existing_user


@handle_errors
async def update_existing_user(uid: int, user_id, user_role,
                user_data: UserUpdate, db: AsyncSession):
    """
    Function to update an existing user by ID.
    
    Returns:
        The updated user info (if successful). 
    """
    query = sa.select(User).where(User.id == uid)
    result = await db.execute(query)
    modified_user = result.scalar()
    if modified_user is None:
        raise HTTPException(status_code=404,
        detail=f'User with ID {uid} not found.')
    if modified_user.id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
        detail='You are not authorized to perform this action.')

    query_all = await db.execute(sa.select(User))
    existing = query_all.scalars().all()
    if any(user_data.username == user.username or
            user_data.email == user.email for user in existing):
        raise HTTPException(status_code=409,
        detail='Username or email already in use.')

    if user_data.username is not None:
        modified_user.username = user_data.username
    if user_data.email is not None:
        modified_user.email = user_data.email
    if user_data.password is not None:
        modified_user.password = user_data.password

    await db.commit()
    await db.refresh(modified_user)
    return modified_user


@handle_errors
async def delete_existing_user(uid, user_id, user_role, db: AsyncSession):
    """
    Function to delete an existing user.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(User).where(User.id == uid)
    result = await db.execute(query)
    user_to_delete = result.scalar()
    if not user_to_delete:
        raise HTTPException(status_code=400,
        detail=f'User {uid} does not exist.')
    if user_to_delete.id != user_id and user_role != 'admin':
        raise HTTPException(status_code=403,
        detail='You are not authorized to perform this action.')

    await db.delete(user_to_delete)
    await db.commit()
    return {'status': 'success', 'message': f'User {uid} deleted successfully.'}


@handle_errors
async def get_all_existing_users(user_role, db: AsyncSession):
    """
    Function to get all existing users (only for admin users).
    
    Returns:
        A list of all users. If error, 
        returns status code and error message of the transaction.
    """
    if user_role == "admin":
        query = sa.select(User)
    else:
        raise HTTPException(status_code=403,
        detail='You are not authorized to perform this action.')
    result = await db.execute(query)
    users = result.scalars().all()
    formatted_output = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "creation_date": user.creation_date
        }
        for user in users
    ]
    return formatted_output


@handle_errors
async def set_new_role(uid, new_role, user_role, db: AsyncSession):
    """
    Function to change the role of an existing user (only for admin users).
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(User).where(User.id == uid)
    result = await db.execute(query)
    user = result.scalar()
    if user is None:
        raise HTTPException(status_code=400,
        detail=f'User with ID {uid} does not exist.')
    if user_role != 'admin':
        raise HTTPException(status_code=403,
        detail='You are not authorized to perform this action.')
    if user.role == new_role.role:
        raise HTTPException(status_code=200,
        detail=f'User already had role {new_role.role}. No changes made.')

    set_role = (
        sa.update(User).where(User.id == uid).values(role=new_role.role)
    )
    await db.execute(set_role)
    await db.commit()
    return {'status': 'success',
            'message': f'User {uid} successfully changed to {new_role.role}.'}
