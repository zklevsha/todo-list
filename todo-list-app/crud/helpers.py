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
from settings import mail_token, mail_from_address, app_url

tasks_url = app_url + ":8080/api/v1/tasks/"
env = Environment(loader=FileSystemLoader(
    searchpath=os.path.join(os.path.dirname(__file__), '..', 'templates')))
template = env.get_template('email.template')


def render_body(raw_tasks):
    """
    Helper function to properly render
    the email body.
    """
    tasks_dict = []
    for task_data in raw_tasks.split(","):
        sections = task_data.split(" ")
        tasks_dict.append({
            "title": sections[0],
            "description": sections[1],
            "link": f"{tasks_url}{sections[2]}"
        })

    return template.render(tasks=tasks_dict)


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
