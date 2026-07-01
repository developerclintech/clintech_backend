from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    auth,
    documents,
    health,
    practices,
    task_categories,
    task_priorities,
    tasks,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(practices.router, prefix="/practices", tags=["practices"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(
    task_categories.router, prefix="/task-categories", tags=["task-categories"]
)
api_router.include_router(
    task_priorities.router, prefix="/task-priorities", tags=["task-priorities"]
)
