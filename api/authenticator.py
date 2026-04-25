import bcrypt
import hmac
import jwt
from datetime import datetime, timedelta, timezone

from config.settings import settings

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

def verify_password(password: str, password_hash: str) -> str:
    _pepper_password = _pepper_password(password)
    return bcrypt.checkpw(_pepper_password, password_hash.encode("utf-8"))

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

def create_access_token(user_id: int):
    return _create_token(user_id, "access", timedelta(minutes=settings.access_token_expires_minutes))
    

def create_refresh_token(user_id: int):
    return _create_token(user_id, "refresh", timedelta(minutes=settings.refresh_token_expires_days))

def verify_refresh_token(refresh_token: str) -> str:
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
    