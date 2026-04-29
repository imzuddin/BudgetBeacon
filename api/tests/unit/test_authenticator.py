from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from api.authenticator import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_token_expiry,
    hash_password,
    hash_refresh_token,
    is_ops_user,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)
from api.models.user import User
from config.settings import settings

PASSWORD = "TEstPassword1234"
INCORRECT_PASSWORD = "WrongPassword"

def encode_token(payload: dict) -> str:
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def test_hash_password_verifies_correct_password():
    password_hash = hash_password(PASSWORD)

    assert verify_password(PASSWORD, password_hash) is True 

def test_hash_password_rejects_wrong_password():
    password_hash = hash_password(PASSWORD)

    assert verify_password(INCORRECT_PASSWORD, password_hash) is False 

def test_unique_salting():
    first_hash = hash_password(PASSWORD)
    second_hash = hash_password(PASSWORD)

    assert first_hash != second_hash
    assert verify_password(PASSWORD, first_hash) is True 
    assert verify_password(PASSWORD, second_hash) is True 
    assert verify_password(INCORRECT_PASSWORD, first_hash) is False 
    assert verify_password(INCORRECT_PASSWORD, second_hash) is False 

def test_create_and_verify_access_token():
    token = create_access_token(user_id=123)

    assert verify_access_token(token) == 123

def test_create_and_verify_refresh_token():
    token = create_refresh_token(user_id=123)

    assert verify_refresh_token(token) == 123 

def test_reject_validating_refresh_token_as_access_token():
    token_refresh = create_refresh_token(user_id=123)
    token_access = create_access_token(user_id=123)

    with pytest.raises(InvalidTokenError, match="Invalid Token Type"):
        verify_access_token(token_refresh)
    
    with pytest.raises(InvalidTokenError, match="Invalid Token Type"):
        verify_refresh_token(token_access)

def test_reject_expired_token():
    access_token = encode_token(
        {
            "sub": "123",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
    )
    refresh_token = encode_token(
        {
            "sub": "123",
            "type": "refresh",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
    )
    

    with pytest.raises(InvalidTokenError):
        verify_access_token(access_token)

    with pytest.raises(InvalidTokenError):
        verify_access_token(refresh_token)

def test_get_current_user_returns_user(db_session):
    user = User(
        first_name="Jane",
        last_name="Doe",
        username="jane",
        password_hash="fake-hash",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(user.id)

    result = get_current_user(access_token=token, db=db_session)

    assert result.id == user.id

def test_get_current_user_raises_401_for_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(access_token="invalid-token", db=db_session)

    assert exc_info.value.status_code == 401

def test_is_ops_user_rejects_regular_user():
    user = User(
        first_name="Regular",
        last_name="User",
        username="regular",
        password_hash="fake-hash",
        role="user",
    )

    with pytest.raises(HTTPException) as exc_info:
        is_ops_user(current_user=user)

    assert exc_info.value.status_code == 403
