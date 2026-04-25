from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select 

from api.models.user import User 
from api.schemas.users import UserRead
from api.db_connecter import get_db
from api.authenticator import hash_password, verify_password


auth_router = APIRouter()

@auth_router.post("auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.name == username))

    if user is None and (user.password is None or verify_password(password, user.password)):
        raise HTTPException(status_code=404, detail="Username or Password is Incorrect")
    
    return "ok"

@auth_router.post("auth/logout")
def logout():
    pass 