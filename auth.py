# app/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole

import os
from dotenv import load_dotenv

load_dotenv()

# ===== JWT конфигурация =====
SECRET_KEY = os.getenv("SECRET_KEY")  # ⚠️ замени на безопасный
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ===== Хэширование =====
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Auth"])

# ===== Модели =====
class UserRegister(BaseModel):
    name: str
    phone: str
    password: str
    role: Optional[str] = UserRole.guest

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ===== Вспомогательные =====
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===== Регистрация =====
@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.phone == user.phone).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_password = get_password_hash(user.password)
    
    try:
        user_role = UserRole(user.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Недопустимая роль пользователя")

    
    new_user = User(
        name=user.name, 
        phone=user.phone, 
        hashed_password=hashed_password,
        role=user_role.value)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Регистрация успешна", "user": {"name": new_user.name, "phone": new_user.phone}}

# ===== Логин =====
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone == user.phone).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный номер телефона или пароль")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={
            "sub": db_user.phone, 
            "name": db_user.name,
            "role": db_user.role.value},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}