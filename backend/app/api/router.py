from fastapi import APIRouter

from app.api.routes import admin_command, customers, early_warnings, health, internal_telegram, internal_whatsapp

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(customers.router)
api_router.include_router(internal_telegram.router)
api_router.include_router(internal_whatsapp.router)
api_router.include_router(admin_command.router)
api_router.include_router(early_warnings.router)
