"""
Настройка подключения к базе данных через SQLAlchemy.

Предоставляет engine, фабрику сессий SessionLocal, базовый класс Base для
моделей и FastAPI-зависимость get_db для внедрения сессии в эндпоинты.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI-зависимость: предоставляет сессию БД на время обработки запроса
    и гарантированно закрывает её по завершении.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()