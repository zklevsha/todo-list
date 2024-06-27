from fastapi import FastAPI, HTTPException
from crud import connect_test, get_schema
from schemas import ConnectionResponse, BasicResponse


app = FastAPI()

@app.get("/")
async def root_test() -> BasicResponse:
    """
    Root endpoint for testing the API.
    
    Returns:
        BasicResponse: Simple test message.
    """
    return BasicResponse(message="This is the root endpoint.")


@app.get("/test")
async def test_route() -> BasicResponse:
    """
    Another test route for the API.
    
    Returns:
        BasicResponse: Another simple test message.
    """
    return BasicResponse(message="This is another test route.")


@app.get("/db_test_connection")
async def testing_connection() -> ConnectionResponse:
    """
    Endpoint to test the DB connection.
    
    Returns:
        ConnectionResponse: Indicates the success or failure of the connection (status and message).
    """
    result = await connect_test()
    return ConnectionResponse(**result)


@app.get("/db_schema_version")
async def get_schema_version() -> str:
    """
    Endpoint to get the current database schema version (Alembic).
    
    Returns:
        str: The current database schema version.
    """
    result = await get_schema()
    return result
