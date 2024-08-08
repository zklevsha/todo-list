"""
api_v1.py
The main config file for defining and including routes. 
"""
from fastapi import APIRouter
from routers.tasks import router as tasks_router
from routers.misc_routes import router as misc_router


api_v1_router = APIRouter()

api_v1_router.include_router(misc_router, tags=["misc_routes"])
api_v1_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
