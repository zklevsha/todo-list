from fastapi import FastAPI, HTTPException
from db import connect, get_schema

app = FastAPI()


@app.get("/")
async def root_test():
    return {"message": "This is the root endpoint."}


@app.get("/test")
async def test_route():
    return {"message": "This is another test route."}


@app.get("/db_test_connection")
async def connect_test():
    result = connect()
    return result


@app.get("/db_schema_version")
async def get_schema_version():
    result = get_schema()
    return result