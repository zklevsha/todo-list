"""
users.py
Routes are configured for the users endpoints.
"""
from fastapi import APIRouter, Depends
from crud.users import crud_create_new_user, crud_get_existing_user, crud_update_user, \
    crud_delete_user, crud_get_all_users, crud_set_role, \
    set_reminder, crud_send_daily_reminder
from schemas import UserDataOutput, UserCreate, UserUpdate, NewRole, \
    DailyReminder, TimeZoneInput, ConnectionResponse
from routers.helpers import get_db, AsyncSession
from routers.tasks import get_user_id, get_user_role

router = APIRouter()


@router.post("/register", response_model=UserDataOutput)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to register a new user.
    
    Returns:
       Returns info about the newly created user.
    """
    user_data = user.model_dump()
    new_user = await crud_create_new_user(user_data=user_data, db=db)
    result = UserDataOutput(message="User created successfully.", user=new_user)
    return result


@router.get("/{id_}", response_model=UserDataOutput)
async def get_existing_user(id_: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to get info about user by ID.
    
    Returns:
       Returns info about the user (if it exists).
    """
    user = await crud_get_existing_user(user_id=id_, db=db)
    result = UserDataOutput(message="User was found.", user=user)
    return result


@router.put("/{id_}", response_model=UserDataOutput)
async def update_user(id_: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db),
                      requester_id: int = Depends(get_user_id),
                      requester_role: str = Depends(get_user_role)):
    """
    Endpoint to update an existing user.
    
    Returns:
       Returns the new changes to the user.
    """
    user = await crud_update_user(user_id=id_, requester_id=requester_id,
                                  requester_role=requester_role, user_data=user_data, db=db)
    result = UserDataOutput(message="User was updated.", user=user)
    return result


@router.delete("/{id_}", response_model=ConnectionResponse)
async def delete_user(id_: int, db: AsyncSession = Depends(get_db),
                      requester_id: int = Depends(get_user_id),
                      requester_role: str = Depends(get_user_role)):
    """
    Endpoint to delete an existing user.
    
    Returns:
       Returns info about the transaction.
    """
    result = await crud_delete_user(user_id=id_, requester_id=requester_id,
                                    requester_role=requester_role, db=db)
    return result


@router.patch("/{id_}", response_model=ConnectionResponse)
async def set_role(id_: int, new_role: NewRole, db: AsyncSession = Depends(get_db),
                   requester_role: str = Depends(get_user_role)):
    """
    Endpoint to change the role of an existing user.
    
    Returns:
       Returns info about the transaction.
    """
    result = await crud_set_role(user_id=id_, new_role=new_role,
                                 requester_role=requester_role, db=db)
    return result


@router.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db),
                        user_role: str = Depends(get_user_role)) -> list:
    """
    Endpoint to get all existing users.
    
    Returns:
       Returns a list of all users from the Users table.
    """
    result = await crud_get_all_users(user_role=user_role, db=db)
    return result


@router.post("/reminders", status_code=200, response_model=ConnectionResponse)
async def set_daily_reminder(reminder: DailyReminder,
                             db: AsyncSession = Depends(get_db),
                             user_id: int = Depends(get_user_id)):
    """
    Endpoint to set the daily reminders.

    Returns:
        Returns info about the transaction.
    """
    reminder = reminder.model_dump()['reminder']
    result = await set_reminder(user_id=user_id, reminder_value=reminder, db=db)
    return result


@router.post("/send_reminders", status_code=200, response_model=ConnectionResponse)
async def send_daily_reminder(job_timezone: TimeZoneInput, db: AsyncSession = Depends(get_db),
                              user_role: str = Depends(get_user_role)):
    """
    Endpoint to send the daily reminders to all users with this option enabled.

    Returns:
        Returns info about the transaction.
    """
    timezone = job_timezone.model_dump()['timezone']
    result = await crud_send_daily_reminder(timezone=timezone, user_role=user_role, db=db)
    return result
