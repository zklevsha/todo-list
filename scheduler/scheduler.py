"""
scheduler.py
Module to send the daily reminders using the apscheduler.
"""
import httpx
from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from oauth import create_access_token
from settings import app_url
from scheduler.helpers import get_timezone, get_tz_list

ADMIN_TOKEN = create_access_token(data={"user_id": 1, "user_role": "admin"})
URL = f"{app_url}:8000/api/v1/users/send_reminders"
URL_TZ = f"{app_url}:8000/api/v1/users/get_tz_list/"
HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}"
}
scheduler = AsyncIOScheduler()
tz = get_timezone()


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


async def job_config_tz(job, client, timezones=None):
    """
    Function to add the jobs for the
     send_reminders_to_users function.
    """
    if timezones is None:
        timezones = await get_tz_list(url=URL_TZ, headers=HEADERS)
    for timezone in timezones:
        job_id = f"reminder_for_{timezone}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(job, 'cron', hour=9, minute=0, timezone=timezone,
                              args=[timezone, client], id=job_id)
    if not scheduler.running:
        scheduler.start()


async def scheduler_main(job, client):
    """
    Function to prepare the scheduler and run the
     job_config_tz function.
    """
    scheduler.add_job(job, 'cron', hour=0, minute=0, timezone=tz,
                      args=[send_reminders_to_users, client])
    scheduler.start()
