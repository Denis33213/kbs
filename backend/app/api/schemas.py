"""
Pydantic-схемы для запросов и ответов API.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Тело запроса для регистрации пользователя."""

    username: str = Field(..., min_length=3, max_length=50, description="Логин пользователя")
    password: str = Field(..., min_length=6, description="Пароль пользователя")


class Token(BaseModel):
    """Ответ с JWT access-токеном."""

    access_token: str
    token_type: str = "bearer"


class DocumentUploadResponse(BaseModel):
    """Ответ после успешной загрузки и индексации документа."""

    document_id: str
    file_name: str
    chunks_count: int
    status: str


class DocumentInfo(BaseModel):
    """Информация об уже загруженном документе."""

    file_name: str
    document_id: Optional[str] = None
    chunks_count: int


class SearchResultItem(BaseModel):
    """Один результат поисковой выдачи."""

    chunk_id: str
    file_name: str
    page: int
    text: str
    highlighted_text: str
    score: float


class SearchResponse(BaseModel):
    """Ответ на поисковый запрос с пагинацией."""

    total: int
    page: int
    page_size: int
    results: List[SearchResultItem]