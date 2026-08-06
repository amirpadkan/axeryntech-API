from fastapi import APIRouter

from app.api.routes import (
    auth,
    users,
    profile,
    projects,
    tasks,
    comments,
    labels,
    notifications,
    activity,
    dashboard,
    exports,
    health,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/utils")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profile.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(notifications.router)
api_router.include_router(activity.router)
api_router.include_router(dashboard.router)
api_router.include_router(exports.router)
api_router.include_router(comments.router)
api_router.include_router(labels.router)
