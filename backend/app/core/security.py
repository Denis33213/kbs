"""
Утилиты безопасности: хеширование паролей (bcrypt) и работа с JWT-токенами.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b",
)

if settings.secret_key == "dev-only-insecure-secret-key":
    logger.warning(
        "SECRET_KEY не задан через переменные окружения — используется небезопасное "
        "значение по умолчанию. Недопустимо для production (см. DO-04)."
    )


def _truncate_to_bcrypt_limit(password: str) -> str:
    """
    Безопасно обрезает пароль до 72 байт — ограничение алгоритма bcrypt.

    Обрезка выполняется по байтам UTF-8, а не по символам, чтобы не разорвать
    многобайтовый символ (например, кириллицу или эмодзи) посередине.

    :param password: Исходный пароль.
    :return: Пароль, безопасно обрезанный до 72 байт в UTF-8.
    """
    encoded = password.encode("utf-8")
    if len(encoded) <= 72:
        return password
    return encoded[:72].decode("utf-8", errors="ignore")


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.

    :param password: Пароль в открытом виде.
    :return: Хеш пароля для сохранения в базе данных.
    """
    return pwd_context.hash(_truncate_to_bcrypt_limit(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля в открытом виде сохранённому хешу.

    :param plain_password: Пароль в открытом виде, введённый пользователем.
    :param hashed_password: Хеш пароля из базы данных.
    :return: True, если пароль верный, иначе False.
    """
    return pwd_context.verify(_truncate_to_bcrypt_limit(plain_password), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT-токен доступа.

    :param data: Данные для включения в токен (например, {"sub": username}).
    :param expires_delta: Время жизни токена. По умолчанию берётся
        ACCESS_TOKEN_EXPIRE_MINUTES из настроек.
    :return: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    Декодирует и валидирует JWT-токен.

    :param token: JWT-токен.
    :return: Полезная нагрузка токена (payload).
    :raises jose.JWTError: Если токен недействителен, просрочен или подделан.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])