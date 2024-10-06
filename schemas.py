"""
schemas.py
This module defines the schemas used 
for data validation and serialization in the project.
"""
from typing import Optional, Union
from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from models import UserRole
from crypto import hash_password


class BasicResponse(BaseModel):
    """
    Model for a basic response containing a message.
    """
    message: str


class ConnectionResponse(BaseModel):
    """
    Model for a connection response containing status and message.
    """
    task_id: Optional[int] = None
    status: str
    message: str


class TodoData(BaseModel):
    """
    Model for a todo item containing title, description, 
    creation date, and completion status.
    """
    title: str
    description: str
    is_finished: bool = False


class IsFinished(BaseModel):
    """
    Model for a basic response containing true/false values.
    """
    is_finished: bool


class UserCreate(BaseModel):
    """
    Model for the user creation endpoint.
    """
    username: str
    email: EmailStr
    password: Union[str, bytes]

    @field_validator('password')
    def hashed_password(cls, value: str) -> bytes:  # pylint: disable=E0213 #"cls" already fulfills that role
        """
        Function to return a hashed password. 
        """
        return hash_password(value)

    model_config = ConfigDict(use_enum_values=True)


class UserUpdate(BaseModel):
    """
    Model for the modification of an existing user.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('password')
    def hashed_password(cls, value: Optional[str]) -> Optional[bytes]:  # pylint: disable=E0213
        """
        Function to return a hashed password, if one was supplied. 
        """
        if value is not None:
            return hash_password(value)
        return value


class UserRead(BaseModel):
    """
    Model for the output when requesting user info.
    """
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class UserOutput(BaseModel):
    """
    Model for the output when requesting user info with a message.
    """
    message: str
    user: UserRead


class Token(BaseModel):
    """
    Model for the access token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Model for the data contained within the access token
    """
    id: Optional[int] = None
    role: Optional[UserRole] = None


class NewRole(BaseModel):
    """
    Model to update the user role.
    """
    role: UserRole


class DailyReminder(BaseModel):
    """
    Model to enable/disable the daily reminders.
    """
    reminder: bool = False
