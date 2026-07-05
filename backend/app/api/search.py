"""
Эндпоинт полнотекстового поиска по проиндексированным документам.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas import SearchResponse
from app.core.database import get_db
from app.models.search_history import SearchHistory
from app.models.user import User
from app.services.elasticsearch_service import search_chunks

router = APIRouter()


@router.get(
    "",
    response_model=SearchResponse,
    summary="Полнотекстовый поиск по документам",
)
def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    page: int = Query(1, ge=1, description="Номер страницы результатов"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Выполняет полнотекстовый поиск по чанкам документов в Elasticsearch
    и сохраняет запрос в историю поиска пользователя.
    """
    db.add(SearchHistory(query_text=q))
    db.commit()

    return search_chunks(q, page=page)