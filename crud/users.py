"""
users.py
This module handles all the functions called by the app.py module, 
but focused on user-related DB operations.
"""
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func, String, cast
from models import User, Todo
from schemas import UserUpdate, UserRole
from crypto import verify_password
from oauth import create_access_token
from crud.helpers import handle_errors, get_creation_date, send_mail
from settings import app_url

NOT_AUTHORIZED = 'You are not authorized to perform this action.'


@handle_errors
async def create_new_user(user_data: dict, db: AsyncSession):
    """
    Function to add a new user into the "users" table.
    
    Returns:
        The new_user info. 
    """
    creation_date = get_creation_date()
    user_data['creation_date'] = creation_date
    user_data['role'] = UserRole.USER
    new_user = User(**user_data)

    query = sa.select(User).where(
        or_(User.username == user_data['username'], User.email == user_data['email'])
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

    access_token = create_access_token(data={"user_id": user.id, "user_role": user.role})
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
                            detail=NOT_AUTHORIZED)

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
                            detail=NOT_AUTHORIZED)

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
                            detail=NOT_AUTHORIZED)
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
        Status and message of the transaction.
    """
    query = sa.select(User).where(User.id == uid)
    result = await db.execute(query)
    user = result.scalar()
    if user is None:
        raise HTTPException(status_code=400,
                            detail=f'User with ID {uid} does not exist.')
    if user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NOT_AUTHORIZED)
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


@handle_errors
async def set_reminder(user_id, reminder_set, db: AsyncSession):
    """
    Function to set the reminders on or off for the user.

    Returns:
        Message of the transaction.
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar()
    if user.daily_reminder == reminder_set and reminder_set is True:
        raise HTTPException(status_code=400,
                            detail='Reminders are already enabled for this user')
    if user.daily_reminder == reminder_set and reminder_set is False:
        raise HTTPException(status_code=400,
                            detail='Reminders are already disabled for this user')

    reminders_config = (
        sa.update(User).where(User.id == user_id).values(daily_reminder=reminder_set)
    )
    await db.execute(reminders_config)
    await db.commit()
    return {'status': 'success', 'message': 'Reminders successfully configured.'}


@handle_errors
async def send_reminders(timezone, user_role, db: AsyncSession):
    """
    Function to send the reminders to users with this function

    Returns:
        Message of the transaction.
    """
    if user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NOT_AUTHORIZED)
    tasks_url = app_url + ":8080/api/v1/tasks/"
    query = sa.select(User.email, func.string_agg(
        'Title: ' + Todo.title + '\nDescription: ' + Todo.description +
        '\nLink: ' + tasks_url + cast(Todo.id, String),
        '\n\n'
    ).label('tasks')).join(Todo, Todo.user_id == User.id).where(
        User.daily_reminder.is_(True), Todo.is_finished.is_(False),
        User.timezone == timezone).group_by(User.email)
    result = await db.execute(query)
    data = result.fetchall()

    for email, tasks in data:
        to_address = email
        subject = "Subject: Daily Reminder"
        email_body = (
            f"Dear User,\n\n"
            f"This is a daily reminder that there are incomplete tasks, please check them out:\n\n"
            f"{tasks}\n\n"
            f"Best regards,\n"
            f"The Team"
        )
        send_mail(to_address=to_address, subject=subject, text=email_body)

    return {'status': 'success', 'message': 'Reminders were sent.'}


@handle_errors
async def get_tz_list(db: AsyncSession, user_role):
    """
    Function to get all timezones on the DB

    Returns:
        A list with the timezones.
    """
    if user_role != 'admin':
        raise HTTPException(status_code=403,
                            detail=NOT_AUTHORIZED)
    query = sa.select(User.timezone).where(User.id > 1).group_by(User.timezone)
    result = await db.execute(query)
    data = result.fetchall()
    tz_dict = []

    for row in data:
        timezone = row.timezone
        tz_dict.append(timezone)

    return tz_dict
