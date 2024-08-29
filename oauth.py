"""
oauth.py
Handles token creation and verification. 
"""
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from settings import SECRET_KEY
from schemas import TokenData, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

def create_access_token(data: dict):
    """
    Function to create a new access token.
    """
    to_encode = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration})

    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token

def verify_access_token(access_token, credentials_exception):
    """
    Function to verify the access token.
    """
    try:
        payload = jwt.decode(key=SECRET_KEY, token=access_token, algorithms=[ALGORITHM])
        uid: int = payload.get("user_id")
        role: UserRole = payload.get("user_role")

        if uid is None:
            raise credentials_exception
        token_data = TokenData(id=uid, role=role)

    except JWTError as e:
        raise credentials_exception from e

    return token_data.id, token_data.role

def get_current_user(access_token: str = Depends(oauth2_scheme)):
    """
    Function to identify the current user.
    """
    credentials_exception = HTTPException(status_code=401,
            detail='Could not validate credentials.', headers={"WWW-Authenticate": "Bearer"})

    user_id, user_role = verify_access_token(access_token,
            credentials_exception=credentials_exception)
    return user_id, user_role
