"""
app.py
The main FastAPI application for the project. Here, the FastAPI instance is created.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.main_router import api_v1_router
from db import async_session
from scheduler.scheduler import scheduler_main, send_reminders_to_users


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0621,W0613
    # Required as per docs https://tinyurl.com/eksmrvf4
    """
    Function to start the scheduler for daily reminders.
    """
    await scheduler_main(job=send_reminders_to_users, db_session=async_session)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")
