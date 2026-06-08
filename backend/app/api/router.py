from fastapi import APIRouter

from app.api.routes import ai_requests, health, projects, usage, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(ai_requests.router, prefix="/ai", tags=["ai requests"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
