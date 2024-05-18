from fastapi import FastAPI, HTTPException


app = FastAPI()


@app.get("/")
async def root_test():
    return {"message": "This is the root endpoint."}


@app.get("/test")
async def test_route():
    return {"message": "This is another test route."}
