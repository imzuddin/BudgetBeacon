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
    get_current_user,
)
from api.db_connecter import get_db
from api.models.auth import RefreshToken
from api.models.user import User
from api.models.spaces import SpaceRole, SpaceMember
from api.schemas.auth import AccessToken

space_router = APIRouter()


@space_router.post("/spaces")
def create_space(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    pass


@space_router.get("/spaces")
def get_spaces(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    pass


@space_router.get("/spaces/{space_id}")
def get_space_by_id(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    pass


@space_router.delete("/spaces/{space_id}")
def delete_space_by_id(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    pass
