# app/main.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
import json
import asyncio

from sqlalchemy.orm import Session


from external.pipeline import translate_symptoms, analyze_pipeline
from auth import router as auth_router
from database import Base, engine, get_db
from models import User

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Genetic Helper MVP")

# Подключаем роуты авторизации
app.include_router(auth_router)

@app.get("/database")
def get_database(db: Session = Depends(get_db)):
    """
    Возвращает всех пользователей из базы данных.
    Только для просмотра (read-only).
    """
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "role": user.role
            }
            for user in users
        ]
    }