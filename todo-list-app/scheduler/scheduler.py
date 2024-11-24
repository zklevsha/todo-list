"""
scheduler.py
Module to send the daily reminders using the apscheduler.
"""
import logging
import httpx
from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from oauth import create_access_token
from settings import app_url
from scheduler.helpers import get_timezones_list, reminders_disabled_timezone

ADMIN_TOKEN = create_access_token(data={"user_id": 1, "user_role": "admin"})
URL = f"{app_url}:8000/api/v1/users/send_reminders"
HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}"
}
scheduler = AsyncIOScheduler()


async def send_reminders_to_users(timezone):
    """
    Function that performs a POST request to the
    'send_daily_reminder' endpoint as the admin user.
    """
    async with httpx.AsyncClient() as client:
        try:
            json_data = {"timezone": timezone}
            response = await client.post(URL, headers=HEADERS, json=json_data)
            logging.info("Reminders sent, status code: %s", response.status_code)
        except HTTPException as error:
            logging.error("Error while sending reminders: %s", error)


async def scheduler_main(job, db_session):
    """
    Function to set up the scheduler to execute the
    send_reminders_to_users function. The refresh_timezones_jobs
    function is triggered daily to add and remove timezones as needed
    after the app's initialization.
    """
    async def refresh_timezones_jobs():
        timezones = await get_timezones_list(db_session)
        for timezone in timezones:
            job_id = f"reminder_for_{timezone}"
            reminders_disabled_for_timezone = \
                await reminders_disabled_timezone(db_session, timezone)
            if reminders_disabled_for_timezone and scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            else:
                if not scheduler.get_job(job_id):
                    scheduler.add_job(job, 'cron', hour=9, minute=0, timezone=timezone,
                                      args=[timezone], id=job_id)

    await refresh_timezones_jobs()

    scheduler.add_job(refresh_timezones_jobs, 'interval', days=1, id="refresh_timezones_jobs")
    scheduler.start()
