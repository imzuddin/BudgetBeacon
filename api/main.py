from fastapi import FastAPI 
from api.routers import health, users
from config.settings import settings

app = FastAPI(
    title=settings.api_name,
    debug=settings.debug,
)

app.include_router(health.health_router)
app.include_router(users.users_router)