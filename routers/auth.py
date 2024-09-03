"""
auth.py
Routes are configured for the authentication endpoints.
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from crud.users import user_login
from schemas import Token
from routers.db_functions import get_db, AsyncSession

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Endpoint to login.
    
    Returns:
       Returns a new user token.
    """
    user_token = await user_login(user_credentials=user_credentials, db=db)
    return user_token
