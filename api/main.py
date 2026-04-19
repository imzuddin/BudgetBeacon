from fastapi import FastAPI 
from routers import health, users
from settings import settings

app = FastAPI(
    title=settings.api_name,
    debug=settings.debug,
)

app.include_router(health.health_router)
app.include_router(users.users_router)