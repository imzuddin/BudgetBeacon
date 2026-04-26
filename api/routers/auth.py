from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.authenticator import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    get_token_expiry,
    hash_refresh_token,
    verify_password,
    verify_refresh_token,
)
from api.db_connecter import get_db
from api.models.auth import RefreshToken
from api.models.user import User
from api.schemas.auth import AccessToken

auth_router = APIRouter()


@auth_router.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == username))

    if user is None or (
        user.password_hash is None or not verify_password(password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Username or Password is Incorrect")

    jwt_token = AccessToken(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )

    refresh_token_entry = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(jwt_token.refresh_token),
        expires_at=get_token_expiry(jwt_token.refresh_token),
        revoked_at=None,
    )

    db.add(refresh_token_entry)
    db.commit()
    db.refresh(refresh_token_entry)

    return jwt_token


@auth_router.post("/auth/logout", status_code=204)
def logout(refresh_token: str, db: Session = Depends(get_db)):

    try:
        verify_refresh_token(refresh_token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    token_hash = hash_refresh_token(refresh_token)

    db_refresh_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )

    if db_refresh_token is None:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    if db_refresh_token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Token Expired")

    db_refresh_token.revoked_at = datetime.now(timezone.utc)
    db.commit()


@auth_router.post("/auth/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    try:
        user_id = verify_refresh_token(refresh_token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    old_token_hash = hash_refresh_token(refresh_token)

    old_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == old_token_hash)
    )

    if old_token is None:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    if old_token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh Token already Used")

    expires_at = old_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        raise HTTPException(status_code=401, detail="Refresh Token Expired")

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")

    old_token.revoked_at = now

    new_refresh_token = create_refresh_token(user.id)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            expires_at=get_token_expiry(new_refresh_token),
        )
    )

    db.commit()

    return AccessToken(
        access_token=create_access_token(user.id),
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
