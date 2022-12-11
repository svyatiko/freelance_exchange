from webapps.auth import route_login
from webapps.tasks import route_tasks
from webapps.users import route_users

from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(route_tasks.router, prefix="", tags=["job-webapp"])
api_router.include_router(route_users.router, prefix="", tags=["users-webapp"])
api_router.include_router(route_login.router, prefix="", tags=["auth-webapp"])
