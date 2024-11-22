"""
helpers.py
Support functions for the scheduler module.
"""
import logging
from zoneinfo import ZoneInfo
import sqlalchemy as sa
from sqlalchemy import func
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


async def reminders_disabled_timezone(db_session, timezone) -> bool:
    """
    Function to check if there are no users with reminders enabled for a
    particular timezone

    Returns:
        True/False
    """
    try:
        async with db_session() as db:
            query = sa.select(func.count()).select_from(User).where(User.timezone == timezone,  # pylint: disable=E1102
                                                                    User.daily_reminder.is_(True))
            # Context for disabling pylint check:
            # https://github.com/pylint-dev/pylint/issues/8138#issuecomment-2210372652
            result = await db.execute(query)
            count = result.scalar()

            return count == 0

    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError occurred: %s", error)
