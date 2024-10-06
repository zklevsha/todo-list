"""
helpers.py
A support module containing useful functions.
"""
import logging
from datetime import datetime
from functools import wraps
import mailtrap as mt
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from settings import mail_token, mail_from_address


def get_creation_date():
    """
    Simple function to get a timestamp of current unix time.
    """
    creation_date = int(datetime.now().timestamp())
    return creation_date


def handle_errors(func):
    """
    Decorator function to maintain consistent error handling.
    """

    @wraps(func)
    async def wrapper(*args, db, **kwargs):
        try:
            return await func(*args, db=db, **kwargs)
        except SQLAlchemyError as error:
            logging.error("SQLAlchemyError occurred: %s", error)
            raise HTTPException(
                status_code=500,
                detail='An internal server error occurred. Please try again later.'
            ) from error
        except HTTPException:
            # Raise the HTTPExceptions to avoid them for being
            # overwritten by the general Exception block
            raise
        except Exception as error:
            logging.error("An unexpected error occurred: %s", error)
            raise HTTPException(
                status_code=500,
                detail='An internal server error occurred. Please try again later.'
            ) from error
        finally:
            await db.close()

    return wrapper


def send_mail(to_address, subject, text):
    """
    Send emails using the Mailtrap service using the API token configured
    in `mail_token`.
    """
    mail = mt.Mail(
        sender=mt.Address(email=mail_from_address, name="Todo-app"),
        to=[mt.Address(email=to_address)],
        subject=subject,
        text=text
    )
    client = mt.MailtrapClient(token=mail_token)

    client.send(mail)
