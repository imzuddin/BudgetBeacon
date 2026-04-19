from fastapi import FastAPI 
from routers import health

app = FastAPI(
    title="Budget Beacon API"
    debug=True
)

app.include_router(health.health_router)