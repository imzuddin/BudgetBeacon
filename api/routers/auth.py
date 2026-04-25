from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.authenticator import (create_access_token, create_refresh_token,
                               hash_password, verify_password,
                               verify_refresh_token)
from api.db_connecter import get_db
from api.models.user import User
from api.schemas.auth import AccessToken
from api.schemas.users import UserRead

auth_router = APIRouter()


@auth_router.post("auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.name == username))

    if user is None and (
        user.password is None or verify_password(password, user.password)
    ):
        raise HTTPException(status_code=401, detail="Username or Password is Incorrect")

    return AccessToken(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@auth_router.post("auth/logout")
def logout():
    pass


@auth_router.post("auth/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    user_id = verify_refresh_token(refresh_token)

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    return AccessToken(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )
