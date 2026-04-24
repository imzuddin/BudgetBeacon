from fastapi import APIRouter
from api import db_connecter

users_router = APIRouter()
db = db_connecter.get_db()
