"""SQLAlchemy-модель истории поисковых запросов."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.core.database import Base


class SearchHistory(Base):
    """
    Запись истории поискового запроса.

    :cvar query_text: Текст поискового запроса пользователя.
    :cvar created_at: Дата и время выполнения запроса (UTC).
    """

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)