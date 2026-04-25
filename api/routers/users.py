from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.authenticator import hash_password
from api.db_connecter import get_db
from api.models.user import User
from api.schemas.users import UserCreate, UserRead

users_router = APIRouter()


@users_router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=404, detail="unkown user")

    return user


@users_router.get("/users", response_model=list[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at)).all()

    return users


@users_router.post("/user")
def create_user(user_input: UserCreate, db: Session = Depends(get_db)):
    user = User(
        first_name=user_input.first_name,
        last_name=user_input.last_name,
        username=user_input.username,
        password_hash=user_input.hash_password(user_input.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@users_router.delete("/user/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=404, detail="Unkown User")

    db.delete(user)
    db.commit()
