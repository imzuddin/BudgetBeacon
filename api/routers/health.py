from fastapi import APIRouter
from fastapi.responses import HTTP_200_OK

health_router = APIRouter()

@health_router.get("/health")
def health_checkpoint():
    return {"status": "ok"}