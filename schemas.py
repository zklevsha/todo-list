from datetime import datetime
from pydantic import BaseModel, Field

class BasicResponse(BaseModel):
    message: str

class ConnectionResponse(BaseModel):
    status: str
    message: str

class Todo(BaseModel):
    title: str
    description: str
    creation_date: datetime = Field(default_factory=datetime.now)
    is_finished: bool = False
