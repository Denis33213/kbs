"""
Эндпоинты авторизации: регистрация и получение JWT-токена.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.schemas import UserCreate, Token
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import register_user, authenticate_user

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового пользователя по логину и паролю.

    :raises HTTPException 400: Если пользователь с таким именем уже существует.
    """
    try:
        user = register_user(db, data.username, data.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"msg": "Пользователь создан", "username": user.username}


@router.post(
    "/login",
    response_model=Token,
    summary="Аутентификация пользователя",
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Аутентифицирует пользователя по логину/паролю (form-data) и выдаёт JWT access-токен.

    :raises HTTPException 401: Если логин или пароль неверны.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.username})
    return Token(access_token=token)