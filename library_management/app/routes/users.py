from fastapi import APIRouter, HTTPException, status
from typing import List
from ..schemas import User
from ..data_store import users_db

router = APIRouter()

@router.get("/", response_model=List[User])
def get_all_users():
    return list(users_db.values())

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    if user.id in users_db:
        raise HTTPException(status_code=400, detail="User sudah ada.")
    users_db[user.id] = user
    return user
