"""
misc_routes.py
Routes are configured for the test and db_schema endpoints.
"""
from fastapi import APIRouter, Depends
from tasks_crud import connect_test, get_schema
from schemas import ConnectionResponse, BasicResponse
from routers.db_functions import get_db, get_engine, AsyncEngine, AsyncSession

router = APIRouter()

@router.get("/")
async def root_test() -> BasicResponse:
    """
    Root endpoint for testing the API.
    
    Returns:
        BasicResponse: Simple test message.
    """
    return BasicResponse(message="This is the root endpoint.")


@router.get("/test")
async def test_route() -> BasicResponse:
    """
    Another test route for the API.
    
    Returns:
        BasicResponse: Another simple test message.
    """
    return BasicResponse(message="This is another test route.")


@router.get("/db-connection", status_code=200)
async def testing_connection(engine_main: AsyncEngine = Depends(get_engine),
            db: AsyncSession = Depends(get_db)) -> ConnectionResponse:
    """
    Endpoint to test the DB connection.
    
    Returns:
        ConnectionResponse: Indicates the success or failure \
            of the connection (status and message).
    """
    result = await connect_test(engine=engine_main, db=db)
    return ConnectionResponse(**result)


@router.get("/schema", status_code=200)
async def get_schema_version(db: AsyncSession = Depends(get_db)) -> str:
    """
    Endpoint to get the current database schema version (Alembic).
    
    Returns:
        str: The current database schema version.
    """
    result = await get_schema(db=db)
    return result
