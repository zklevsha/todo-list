"""
misc_routes.py
Routes are configured for the root and db_schema endpoints.
"""
from fastapi import APIRouter, Depends
from crud.tasks import get_schema
from schemas import BasicResponse
from routers.helpers import get_db, AsyncSession

router = APIRouter()


@router.get("/")
async def root_test() -> BasicResponse:
    """
    Root endpoint for testing the API.
    
    Returns:
        BasicResponse: Simple test message.
    """
    return BasicResponse(message="This is the root endpoint.")


@router.get("/schema", status_code=200)
async def get_schema_version(db: AsyncSession = Depends(get_db)) -> str:
    """
    Endpoint to get the current database schema version (Alembic).
    
    Returns:
        str: The current database schema version.
    """
    result = await get_schema(db=db)
    return result
