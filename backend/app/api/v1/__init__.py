from fastapi import APIRouter
from .endpoints import auth, users, houses, admin, visits

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(houses.router)
api_router.include_router(admin.router)
api_router.include_router(visits.router)