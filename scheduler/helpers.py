"""
helpers.py
Support functions for the scheduler module.
"""
import logging
from zoneinfo import ZoneInfo
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from models import User


async def get_timezones_list(db_session):
    """
    Function to get all timezones on the DB

    Returns:
        A list with the timezones.
    """
    try:
        async with db_session() as db:
            query = sa.select(User.timezone).where(User.id > 1).group_by(User.timezone)
            result = await db.execute(query)
            data = result.fetchall()

            timezones_list = [row.timezone for row in data]

        return timezones_list

    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError occurred: %s", error)
        return [ZoneInfo("UTC")]
