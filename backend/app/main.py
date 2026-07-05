"""
Точка входа FastAPI-приложения "Интеллектуальная поисковая система
по внутренней базе знаний университета".
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, documents, search
from app.core.database import Base, engine
from app.services.elasticsearch_service import init_elasticsearch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge Base Search API",
    description="Интеллектуальная поисковая система по внутренней базе знаний университета",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём таблицы БД (users, search_history), если их ещё нет
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])


@app.on_event("startup")
async def startup_event() -> None:
    """Инициализирует индекс Elasticsearch при старте приложения."""
    try:
        init_elasticsearch()
    except Exception as exc:
        logger.error("Не удалось инициализировать Elasticsearch при старте: %s", exc)


@app.get("/health", tags=["Health"], summary="Проверка работоспособности сервиса")
def health_check():
    """Простой health-check эндпоинт для мониторинга и Docker healthcheck."""
    return {"status": "ok"}