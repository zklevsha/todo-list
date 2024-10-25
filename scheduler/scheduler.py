"""
scheduler.py
Module to send the daily reminders using the apscheduler.
"""
import httpx
from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from oauth import create_access_token
from settings import app_url
from scheduler.helpers import get_tz_list

ADMIN_TOKEN = create_access_token(data={"user_id": 1, "user_role": "admin"})
URL = f"{app_url}:8000/api/v1/users/send_reminders"
HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}"
}
scheduler = AsyncIOScheduler()


async def send_reminders_to_users(timezone, client):
    """
    Function that performs a POST request to the
    'send_daily_reminder' endpoint as the admin user.
    """
    async with httpx.AsyncClient() as client:
        try:
            json_data = {"timezone": timezone}
            response = await client.post(URL, headers=HEADERS, json=json_data)
            print(f"Reminders sent, status code: {response.status_code}")
        except HTTPException as e:
            print(f"Error while sending reminders: {e}")


async def scheduler_main(job, client, db_session):
    """
    Function to set up the scheduler to execute the
     send_reminders_to_users function.
    """
    timezones = await get_tz_list(db_session)
    for timezone in timezones:
        job_id = f"reminder_for_{timezone}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(job, 'cron', hour=9, minute=0, timezone=timezone,
                              args=[timezone, client], id=job_id)

    scheduler.start()
