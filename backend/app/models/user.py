"""SQLAlchemy-модель пользователя системы."""

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class User(Base):
    """
    Пользователь системы.

    :cvar username: Уникальный логин пользователя.
    :cvar hashed_password: Хеш пароля (bcrypt), пароль в открытом виде не хранится.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)