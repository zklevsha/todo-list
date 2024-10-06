"""
helpers.py
Support functions for the scheduler module.
"""
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
