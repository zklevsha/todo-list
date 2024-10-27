"""
users.py
Module to handle all CRUD operations related
to the users endpoints.
"""
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func, String, cast
from models import User, Todo
from schemas import UserUpdate, UserRole
from crypto import verify_password
from oauth import create_access_token
from crud.helpers import handle_errors, get_current_time, send_mail, raise_helper, template
from settings import app_url


@handle_errors
async def crud_create_new_user(user_data: dict, db: AsyncSession):
    """
    Function to add a new user into the "users" table.
    
    Returns:
        The new_user info. 
    """
    creation_date = get_current_time()
    user_data['creation_date'] = creation_date
    user_data['role'] = UserRole.USER
    new_user = User(**user_data)

    query = sa.select(User).where(
        or_(User.username == user_data['username'], User.email == user_data['email'])
    )
    result = await db.execute(query)
    user_exists = result.scalars().first()
    if user_exists:
        raise_helper(409)

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
    if user is None or not verify_password(user_credentials.password, user.password):
        raise_helper(403)

    access_token = create_access_token(data={"user_id": user.id, "user_role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@handle_errors
async def crud_get_existing_user(user_id: int, db: AsyncSession):
    """
    Function to get an existing user by ID.
    
    Returns:
        The user info (if it exists). 
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    existing_user = result.scalar()
    if existing_user is None:
        raise_helper(404, "User", user_id)

    return existing_user


@handle_errors
async def crud_update_user(user_id: int, requester_id, requester_role,
                           user_data: UserUpdate, db: AsyncSession):
    """
    Function to update an existing user by ID.
    
    Returns:
        The updated user info (if successful). 
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    modified_user = result.scalar()
    if modified_user is None:
        raise_helper(404, "User", user_id)
    if modified_user.id != requester_id and requester_role != 'admin':
        raise_helper(401)

    query_all = await db.execute(sa.select(User))
    existing = query_all.scalars().all()
    if any(user_data.username == user.username or
           user_data.email == user.email for user in existing):
        raise_helper(409)

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
async def crud_delete_user(user_id, requester_id, requester_role, db: AsyncSession):
    """
    Function to delete an existing user.
    
    Returns:
        Status code and message of the transaction.
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    user_to_delete = result.scalar()
    if not user_to_delete:
        raise_helper(404, "User", user_id)
    if user_to_delete.id != requester_id and requester_role != 'admin':
        raise_helper(401)

    await db.delete(user_to_delete)
    await db.commit()
    return {'status': 'success', 'message': f'User {user_id} deleted successfully.'}


@handle_errors
async def crud_get_all_users(user_role, db: AsyncSession):
    """
    Function to get all existing users (only for admin users).
    
    Returns:
        A list of all users. If error, 
        returns status code and error message of the transaction.
    """
    query = ""  # For pylint E0606: Possibly using variable 'query' before assignment
    if user_role == "admin":
        query = sa.select(User)
    else:
        raise_helper(401)

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
async def crud_set_role(user_id, new_role, requester_role, db: AsyncSession):
    """
    Function to change the role of an existing user (only for admin users).
    
    Returns:
        Status and message of the transaction.
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar()
    if user is None:
        raise_helper(404, "User", user_id)
    if requester_role != 'admin':
        raise_helper(401)
    if user.role == new_role.role:
        raise_helper(422, "User", new_role)

    set_role = (
        sa.update(User).where(User.id == user_id).values(role=new_role.role)
    )
    await db.execute(set_role)
    await db.commit()
    return {'status': 'success',
            'message': f'User {user_id} successfully changed to {new_role.role}.'}


@handle_errors
async def set_reminder(user_id, reminder_value, db: AsyncSession):
    """
    Function to set the reminders on or off for the user.

    Returns:
        Message of the transaction.
    """
    query = sa.select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar()

    if user.daily_reminder == reminder_value:
        status = "enabled" if reminder_value else "disabled"
        raise_helper(422, "Reminders", status)

    reminders_config = (
        sa.update(User).where(User.id == user_id).values(daily_reminder=reminder_value)
    )
    await db.execute(reminders_config)
    await db.commit()
    return {'status': 'success', 'message': 'Reminders successfully configured.'}


@handle_errors
async def crud_send_daily_reminder(timezone, user_role, db: AsyncSession):
    """
    Function to send the reminders to users with this function

    Returns:
        Message of the transaction.
    """
    if user_role != 'admin':
        raise_helper(401)
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
        email_body = template.render(tasks=tasks)

        send_mail(to_address=to_address, subject=subject, text=email_body)

    return {'status': 'success', 'message': 'Reminders were sent.'}
