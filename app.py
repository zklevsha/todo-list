from fastapi import FastAPI, HTTPException
from db import connect, connect_test, get_schema
from typing import Dict

app = FastAPI()


@app.get("/")
async def root_test() -> Dict[str, str]:
    """
    Root endpoint for testing the API.
    
    Returns:
        Dict[str, str]: Simple test message.
    """
    return {"message": "This is the root endpoint."}


@app.get("/test")
async def test_route() -> Dict[str, str]:
    """
    Another test route for the API.
    
    Returns:
        Dict[str, str]: Another simple test message.
    """
    return {"message": "This is another test route."}


@app.get("/db_test_connection")
async def testing_connection() -> Dict[str, str]:
    """
    Endpoint to test the DB connection.
    
    Returns:
        Dict[str, str]: Indicates the success or failure of the connection.
    """
    result = connect_test()
    return result


@app.get("/db_schema_version")
async def get_schema_version() -> int:
    """
    Endpoint to get the current database schema version.
    
    Returns:
        int: The current database schema version.
    """
    result = get_schema()
    return result