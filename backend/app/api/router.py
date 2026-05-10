from fastapi import APIRouter

from app.api.routes import analytics, auth, movies, system

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.api_router)
api_router.include_router(system.router)
api_router.include_router(analytics.router)
api_router.include_router(movies.router)

auth_router = APIRouter()
auth_router.include_router(auth.callback_router)
