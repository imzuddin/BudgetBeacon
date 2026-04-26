import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db_connecter import get_db
from api.models.user import User
from config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class InvalidTokenError(Exception):
    pass


def _pepper_password(password: str) -> bytes:
    return hmac.digest(
        settings.pepper_string.encode("utf-8"),
        password.encode("utf-8"),
        "sha256",
    )


def hash_password(password: str) -> str:
    peppered_password = _pepper_password(password)
    return bcrypt.hashpw(peppered_password, bcrypt.gensalt()).decode("utf-8")


def hash_refresh_token(refresh_token: str) -> str:
    return hmac.digest(
        settings.pepper_string.encode("utf-8"),
        refresh_token.encode("utf-8"),
        "sha256",
    ).hex()


def verify_password(password: str, password_hash: str) -> bool:
    peppered_password = _pepper_password(password)
    return bcrypt.checkpw(peppered_password, password_hash.encode("utf-8"))


def _create_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(user_id: int) -> str:
    return _create_token(
        user_id, "access", timedelta(minutes=settings.access_token_expires_minutes)
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        user_id, "refresh", timedelta(minutes=settings.refresh_token_expires_days)
    )


def verify_refresh_token(refresh_token: str) -> int:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except jwt.PyJWTError as e:
        raise InvalidTokenError("Invalid Refresh Token") from e

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid Token Type")

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidTokenError("Missing Token Subject")

    try:
        return int(user_id)
    except ValueError as e:
        raise InvalidTokenError("Invalid Token Subject") from e


def verify_access_token(access_token: str) -> int:
    try:
        payload = jwt.decode(
            access_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except jwt.PyJWTError as e:
        raise InvalidTokenError("Invalid Access Token") from e

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid Token Type")

    token_user_id = payload.get("sub")

    if token_user_id is None:
        raise InvalidTokenError("Missing Token Subject")

    try:
        return int(token_user_id)
    except ValueError as e:
        raise InvalidTokenError("Invalid Token Subject") from e


def get_token_expiry(token: str) -> datetime:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    if payload.get("type") not in ["refresh", "access"]:
        raise ValueError("Unsupported Token Type")

    expiry = payload["exp"]
    return datetime.fromtimestamp(expiry, tz=timezone.utc)


def get_current_user(
    access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = verify_access_token(access_token)
    except InvalidTokenError:
        raise credentials_exception

    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise credentials_exception

    return user


def is_ops_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ops":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Enough Permissions",
        )

    return current_user
