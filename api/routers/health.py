from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

import db_connecter

health_router = APIRouter()

@health_router.get("/health")
def health_checkpoint():
    return {"status": "ok"}

@health_router.get("/db")
def db_health_check(db: Session = Depends(db_connecter.get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "ok",
            "database": "connected",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "database": "disconnected",
                "message": str(e),
            },
        )