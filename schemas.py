from pydantic import BaseModel

class BasicResponse(BaseModel):
    message: str

class ConnectionResponse(BaseModel):
    status: str
    message: str