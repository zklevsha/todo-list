"""
helpers.py
Support functions for the scheduler module.
"""
import httpx
from fastapi import HTTPException
from pytz import timezone, UnknownTimeZoneError
from settings import TZ


def get_timezone():
    """
    Function to get the timezone from the .env file
    and set it for the reminders.
    """
    try:
        tz = timezone(TZ)
    except UnknownTimeZoneError:
        print(f"Invalid timezone: {TZ}, falling back to UTC")
        tz = timezone("UTC")
    return tz


async def get_tz_list(url, headers):
    """
    Function to get all the timezones of registered users.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
        except HTTPException as e:
            print(f"Not found: {e}")
    response = response.json()
    return response
