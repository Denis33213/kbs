"""
Бизнес-логика регистрации и аутентификации пользователей.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User


def register_user(db: Session, username: str, password: str) -> User:
    """
    Регистрирует нового пользователя.

    :param db: Сессия базы данных.
    :param username: Желаемый логин пользователя.
    :param password: Пароль в открытом виде.
    :return: Созданный объект User.
    :raises ValueError: Если пользователь с таким username уже существует.
    """
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise ValueError("Пользователь уже существует")

    user = User(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Проверяет логин и пароль пользователя.

    :param db: Сессия базы данных.
    :param username: Логин пользователя.
    :param password: Пароль в открытом виде.
    :return: Объект User при успешной аутентификации, иначе None.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user