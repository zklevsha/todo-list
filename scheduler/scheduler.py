"""
scheduler.py
Module to send the daily reminders using the scheduler.
"""
from datetime import timezone
import httpx
from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from oauth import create_access_token

ADMIN_TOKEN = create_access_token(data={"user_id": 1, "user_role": "admin"})
URL = "http://localhost:8000/api/v1/users/send_reminders"
HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}"
}
scheduler = AsyncIOScheduler()


async def send_reminders_to_users(client):
    """
    Function that performs a POST request to the
    'send_reminders' endpoint as the admin user.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(URL, headers=HEADERS)
            print(f"Reminders sent, status code: {response.status_code}")
        except HTTPException as e:
            print(f"Error while sending reminders: {e}")


async def scheduler_main(job, client):
    """
    Function to set up the scheduler to execute the
     send_reminders_to_users function.
    """
    # Running the jobs every day at 6AM.
    scheduler.add_job(job, 'cron', hour=6, minute=0, second=0, timezone=timezone.utc, args=[client])
    scheduler.start()
