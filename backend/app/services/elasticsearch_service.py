"""
Модуль интеграции с Elasticsearch и Redis.

Отвечает за:
  - создание индекса `documents` с русскоязычным анализатором (BE-06),
  - индексацию чанков документов (BE-07),
  - полнотекстовый поиск по чанкам через multi_match (BE-08, BE-09),
  - кеширование частых поисковых запросов в Redis с TTL = 5 минут (BE-10).
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from elasticsearch import Elasticsearch, NotFoundError
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

INDEX_NAME = "documents"
DEFAULT_PAGE_SIZE = 10

es_client = Elasticsearch(settings.elasticsearch_url)

try:
    redis_client: Optional[redis.Redis] = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    redis_client.ping()
except Exception as exc:
    logger.warning("Redis недоступен, кеширование поиска отключено: %s", exc)
    redis_client = None


# ===================== Инициализация индекса =====================

def init_elasticsearch() -> None:
    """
    Создаёт индекс `documents` с русскоязычным анализатором, если он ещё не существует.

    Анализатор `analysis-ru` использует стандартный токенайзер, приведение к нижнему
    регистру, русские стоп-слова и русский стеммер — это требуется по BE-06 для
    корректного полнотекстового поиска на русском языке.
    """
    if es_client.indices.exists(index=INDEX_NAME):
        logger.info("Индекс '%s' уже существует, пропускаем создание", INDEX_NAME)
        return

    index_body = {
        "settings": {
            "analysis": {
                "filter": {
                    "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                },
                "analyzer": {
                    "analysis-ru": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "russian_stop", "russian_stemmer"],
                    }
                },
            }
        },
        "mappings": {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "file_name": {"type": "keyword"},
                "page_number": {"type": "integer"},
                "text": {"type": "text", "analyzer": "analysis-ru"},
                "indexed_at": {"type": "date"},
            }
        },
    }

    es_client.indices.create(index=INDEX_NAME, body=index_body)
    logger.info("Индекс '%s' успешно создан", INDEX_NAME)


# ===================== Индексация =====================

def index_document_chunk(
    chunk_id: str,
    file_name: str,
    page_number: int,
    text: str,
    document_id: Optional[str] = None,
) -> None:
    """
    Индексирует один чанк документа в Elasticsearch.

    :param chunk_id: Уникальный идентификатор чанка (используется как _id документа в ES).
    :param file_name: Имя исходного файла.
    :param page_number: Номер страницы, к которой относится чанк.
    :param text: Текст чанка.
    :param document_id: UUID документа, к которому относится чанк (для группировки чанков).
    """
    body = {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "file_name": file_name,
        "page_number": page_number,
        "text": text,
        "indexed_at": datetime.utcnow().isoformat(),
    }
    es_client.index(index=INDEX_NAME, id=chunk_id, document=body)


# ===================== Список документов =====================

def get_unique_documents() -> List[Dict]:
    """
    Возвращает список уникальных документов, уже загруженных и проиндексированных в системе.

    :return: Список словарей с полями file_name, document_id, chunks_count.
        Пустой список, если индекс ещё не создан или пуст.
    """
    aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_documents": {
                "terms": {"field": "file_name", "size": 1000},
                "aggs": {
                    "document_ids": {"terms": {"field": "document_id", "size": 1}},
                },
            }
        },
    }

    try:
        response = es_client.search(index=INDEX_NAME, body=aggregation_query)
    except NotFoundError:
        logger.info("Индекс '%s' ещё не создан, документов нет", INDEX_NAME)
        return []

    buckets = response["aggregations"]["unique_documents"]["buckets"]
    result: List[Dict] = []
    for bucket in buckets:
        id_buckets = bucket["document_ids"]["buckets"]
        document_id = id_buckets[0]["key"] if id_buckets else None
        result.append(
            {
                "file_name": bucket["key"],
                "document_id": document_id,
                "chunks_count": bucket["doc_count"],
            }
        )
    return result


# ===================== Поиск =====================

def search_chunks(query: str, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> Dict:
    """
    Выполняет полнотекстовый поиск по чанкам документов с пагинацией и кешированием в Redis.

    Запрос выполняется через multi_match по полю `text` (BE-08). Результаты
    кешируются в Redis на settings.search_cache_ttl_seconds (по умолчанию 5 минут,
    BE-10): повторный идентичный запрос отдаётся из кеша без обращения к Elasticsearch.

    :param query: Поисковый запрос пользователя.
    :param page: Номер страницы результатов, нумерация с 1.
    :param page_size: Количество результатов на странице (для пагинации FE-07).
    :return: Словарь {"total": int, "page": int, "page_size": int, "results": [...]}.
        Каждый элемент results содержит chunk_id, file_name, page, text,
        highlighted_text и score, как того требует BE-09.
    """
    normalized_query = query.strip().lower()
    cache_key = f"search:{normalized_query}:{page}:{page_size}"

    cached_result = _get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result

    from_offset = (page - 1) * page_size

    search_body = {
        "from": from_offset,
        "size": page_size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["text"],
            }
        },
        "highlight": {
            "fields": {
                "text": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]}
            }
        },
    }

    try:
        response = es_client.search(index=INDEX_NAME, body=search_body)
    except NotFoundError:
        return {"total": 0, "page": page, "page_size": page_size, "results": []}

    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]

    results = []
    for hit in hits:
        source = hit["_source"]
        highlight_snippets = hit.get("highlight", {}).get("text")
        highlighted_text = highlight_snippets[0] if highlight_snippets else source["text"]
        results.append(
            {
                "chunk_id": source["chunk_id"],
                "file_name": source["file_name"],
                "page": source["page_number"],
                "text": source["text"],
                "highlighted_text": highlighted_text,
                "score": hit["_score"],
            }
        )

    result = {"total": total, "page": page, "page_size": page_size, "results": results}
    _set_cache(cache_key, result)
    return result


# ===================== Redis-кеш =====================

def _get_from_cache(cache_key: str) -> Optional[Dict]:
    """
    Пытается получить результат поиска из кеша Redis.

    :param cache_key: Ключ кеша.
    :return: Закешированный результат, либо None, если кеш недоступен или пуст.
    """
    if redis_client is None:
        return None
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as exc:
        logger.warning("Ошибка чтения из кеша Redis (%s): %s", cache_key, exc)
    return None


def _set_cache(cache_key: str, value: Dict) -> None:
    """
    Сохраняет результат поиска в кеш Redis с TTL = settings.search_cache_ttl_seconds.

    :param cache_key: Ключ кеша.
    :param value: Значение для сохранения (результат поиска).
    """
    if redis_client is None:
        return
    try:
        redis_client.setex(cache_key, settings.search_cache_ttl_seconds, json.dumps(value))
    except Exception as exc:
        logger.warning("Ошибка записи в кеш Redis (%s): %s", cache_key, exc)