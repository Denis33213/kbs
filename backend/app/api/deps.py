"""
Общие FastAPI-зависимости для эндпоинтов API.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Извлекает и валидирует текущего пользователя из JWT-токена, переданного в заголовке Authorization.

    :param token: JWT-токен, извлечённый OAuth2PasswordBearer из заголовка Authorization.
    :param db: Сессия базы данных.
    :return: Объект аутентифицированного пользователя.
    :raises HTTPException 401: Если токен недействителен, просрочен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user