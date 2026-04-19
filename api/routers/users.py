from fastapi import APIRouter
import db_connecter

users_router = APIRouter()
db = db_connecter.get_db()
