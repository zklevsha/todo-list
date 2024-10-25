"""
schemas.py
This module defines the schemas used 
for data validation and serialization in the project.
"""
from typing import Optional, Union
from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
import pytz
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
    status: str
    message: str


class TodoData(BaseModel):
    """
    Model for a todo item containing title, description, 
    and completion status.
    """
    title: str
    description: str
    is_finished: bool = False


class IsFinished(BaseModel):
    """
    Model for a basic response containing true/false values.
    """
    is_finished: bool


class UserBase(BaseModel):
    """
    Shared base model for user creation and updates.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[Union[str, bytes]] = None
    timezone: Optional[str] = 'UTC'

    @field_validator('password', mode='before')
    def hashed_password(cls, value: Optional[str]) \
            -> Optional[bytes]: # pylint: disable=E0213 #"cls" already fulfills that role
        """
        Hash the password if provided.
        """
        if value is not None:
            return hash_password(value)
        return value

    @field_validator('timezone')
    def validate_timezone(cls, value): # pylint: disable=E0213 #"cls" already fulfills that role
        """
        Validate the timezone.
        """
        if value not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {value}")
        return value

    model_config = ConfigDict(use_enum_values=True)


class UserCreate(UserBase):
    """
    Model for the user creation endpoint.
    """
    username: str
    email: EmailStr
    password: Union[str, bytes]


class UserUpdate(UserBase):
    """
    Model for modifying an existing user.
    """


class UserRead(BaseModel):
    """
    Base model for user info.
    """
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class UserOutput(BaseModel):
    """
    Model for user info with a message.
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


class TzInput(BaseModel):
    """
    Model to send the timezone.
    """
    timezone: str
