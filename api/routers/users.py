from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.authenticator import get_current_user, hash_password, is_ops_user
from api.db_connecter import get_db
from api.models.user import User
from api.schemas.users import UserCreate, UserRead

users_router = APIRouter()


@users_router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_ops_user),
):
    user = db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=404, detail="unkown user")

    return user

@users_router.get("/users/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@users_router.get("/users", response_model=list[UserRead])
def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(is_ops_user)
):
    users = db.scalars(select(User).order_by(User.created_at)).all()

    return users

@users_router.post("/user", response_model=UserRead)
def create_user(user_input: UserCreate, db: Session = Depends(get_db)):
    user = User(
        first_name=user_input.first_name,
        last_name=user_input.last_name,
        username=user_input.username,
        password_hash=hash_password(user_input.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@users_router.delete("/user", status_code=204)
def delete_current_user(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    user = db.scalar(select(User).where(User.id == current_user.id))
    if user is None:
        raise HTTPException(status_code=404, detail="Unkown User")

    db.delete(user)
    db.commit()


@users_router.delete("/user/{user_id}", status_code=204)
def delete_user_by_id(
    user_id: int, db: Session = Depends(get_db), is_ops: User = Depends(is_ops_user)
):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Unkown User")

    db.delete(user)
    db.commit()



