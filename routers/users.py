"""
users.py
Routes are configured for the users endpoints.
"""
from fastapi import APIRouter, Depends
from users_crud import create_new_user, get_existing_user, update_existing_user, \
    delete_existing_user, get_all_existing_users, set_new_role
from schemas import UserOutput, UserCreate, UserUpdate, NewRole
from routers.db_functions import get_db, AsyncSession
from routers.tasks import get_user_id, get_user_role


router = APIRouter()

@router.post("/register", response_model=UserOutput)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to register a new user.
    
    Returns:
       Returns info about the newly created user.
    """
    new_user = await create_new_user(user=user, db=db)
    return {
        "message": "User created successfully.",
        "user": new_user
    }

@router.get("/{id_}", response_model=UserOutput)
async def get_user(id_: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to get info about user by ID.
    
    Returns:
       Returns info about the user (if it exists).
    """
    user = await get_existing_user(uid=id_, db=db)
    return {
        "message": "User was found.",
        "user": user
    }

@router.put("/{id_}", response_model=UserOutput)
async def update_user(id_: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db),
            user_id: int = Depends(get_user_id), user_role: str = Depends(get_user_role)):
    """
    Endpoint to update an existing user.
    
    Returns:
       Returns the new changes to the user.
    """
    user = await update_existing_user(uid=id_, user_id=user_id,
                user_role=user_role, user_data=user_data, db=db)
    return {
        "message": "User was updated.",
        "user": user
    }

@router.delete("/{id_}")
async def delete_user(id_: int, db: AsyncSession = Depends(get_db),
            user_id: int = Depends(get_user_id), user_role: str = Depends(get_user_role)):
    """
    Endpoint to delete an existing user.
    
    Returns:
       Returns info about the transaction.
    """
    deleted_user = await delete_existing_user(uid=id_, user_id=user_id, user_role=user_role, db=db)
    return deleted_user

@router.patch("/{id_}")
async def set_role(id_: int, new_role: NewRole, db: AsyncSession = Depends(get_db),
            user_role: str = Depends(get_user_role)):
    """
    Endpoint to change the role of an existing user.
    
    Returns:
       Returns info about the transaction.
    """
    user = await set_new_role(uid=id_, new_role=new_role, user_role=user_role, db=db)
    return user

@router.get("/")
async def get_all_users(db: AsyncSession = Depends(get_db),
            user_role: str = Depends(get_user_role)):
    """
    Endpoint to get all existing users.
    
    Returns:
       Returns all users from the Users table.
    """
    users = await get_all_existing_users(user_role=user_role, db=db)
    return users
