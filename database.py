from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# SQLite база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./genetic_helper.db"

# Создаем движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

# Сессии для запросов
SessionLocal = sessionmaker(autoflush=False, bind=engine)

# Базовой класс моделей
Base = declarative_base()

# Зависимость для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    