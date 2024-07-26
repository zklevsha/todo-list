"""
schemas.py
This module defines the schemas used 
for data validation and serialization in the project.
"""
from datetime import datetime
from pydantic import BaseModel, Field

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

class Todo(BaseModel):
    """
    Model for a todo item containing title, description, 
    creation date, and completion status.
    """
    title: str
    description: str
    creation_date: datetime = Field(default_factory=datetime.now)
    is_finished: bool = False
