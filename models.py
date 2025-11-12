from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from database import Base
import enum

class UserRole(enum.Enum):
    doctor = "Дәрігер"
    student = "Студент"
    guest = "Қонақ"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
    SQLEnum(UserRole, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
    nullable=False,
    default=UserRole.guest
)

    