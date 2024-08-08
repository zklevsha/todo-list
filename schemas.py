"""
schemas.py
This module defines the schemas used 
for data validation and serialization in the project.
"""
from typing import Optional
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
    creation_date: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    is_finished: bool = False

class IsFinished(BaseModel):
    """
    Model for a basic response containing true/false values.
    """
    is_finished: bool
