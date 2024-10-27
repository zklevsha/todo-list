"""
helpers.py
A support module containing useful functions.
"""
import logging
import os
from datetime import datetime
from functools import wraps
from jinja2 import Environment, FileSystemLoader
import mailtrap as mt
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from settings import mail_token, mail_from_address


env = Environment(loader=FileSystemLoader(
                  searchpath=os.path.join(os.path.dirname(__file__), '..', 'templates')))
template = env.get_template('email.template')


def get_current_time():
    """
    Simple function to get a timestamp of current unix time.
    """
    return int(datetime.now().timestamp())


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


def raise_helper(status_code, element=None, element_property=None):
    """
    Helper function to centralize and manage the raising of HTTP exceptions.
    """
    messages = {
        200: "The Todo list is empty.",
        401: "You are not authorized to perform this action.",
        403: "Invalid credentials.",
        404: f"{element} with ID {element_property} not found."
        if element and element_property else "Resource not found.",
        409: "That username or email is already in use.",
        422: f"{element} already set to {element_property}. No changes made."
        if element and element_property else "Unprocessable Content.",
    }
    detail = messages.get(status_code, "Unspecified error occurred.")

    raise HTTPException(status_code=status_code, detail=detail)
