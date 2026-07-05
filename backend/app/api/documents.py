"""
Эндпоинты загрузки документов и получения списка уже загруженных документов.
"""

import logging
import uuid
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status

from app.api.deps import get_current_user
from app.api.schemas import DocumentUploadResponse, DocumentInfo
from app.core.config import settings
from app.models.user import User
from app.services.chunker import split_text_into_chunks
from app.services.elasticsearch_service import document_exists, get_unique_documents, index_document_chunk
from app.services.parser import extract_text_from_docx, extract_text_from_pdf

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx"}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка и индексация документа",
)
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    Загружает документ (PDF или DOCX), извлекает из него текст, разбивает
    на чанки и индексирует их в Elasticsearch.

    :raises HTTPException 400: Неверный формат файла, превышен размер,
        файл пуст, повреждён или не содержит извлекаемого текста.
    """
    if not file.filename or "." not in file.filename:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Не указано имя файла")

    extension = file.filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Поддерживаются только файлы форматов PDF и DOCX")

    content = await file.read()

    if not content:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Файл пуст")

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Размер файла превышает допустимый лимит {settings.max_upload_size_mb} МБ",
        )

    try:
        pages = extract_text_from_pdf(content) if extension == "pdf" else extract_text_from_docx(content)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    if not pages:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Не удалось извлечь текст из документа")

    document_id = str(uuid.uuid4())
    total_chunks = 0

    for page in pages:
        chunks = split_text_into_chunks(
            page["text"], chunk_size=settings.chunk_size, overlap=settings.chunk_overlap
        )
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{document_id}_{page['page_number']}_{i}"
            index_document_chunk(
                chunk_id=chunk_id,
                file_name=file.filename,
                page_number=page["page_number"],
                text=chunk_text,
                document_id=document_id,
            )
            total_chunks += 1

    logger.info("Документ '%s' проиндексирован: %d чанков", file.filename, total_chunks)

    return DocumentUploadResponse(
        document_id=document_id,
        file_name=file.filename,
        chunks_count=total_chunks,
        status="indexed",
    )


@router.get(
    "",
    response_model=List[DocumentInfo],
    summary="Список загруженных документов",
)
def list_documents(current_user: User = Depends(get_current_user)):
    """Возвращает список уникальных документов, уже загруженных и проиндексированных в системе."""
    return get_unique_documents()


@router.get(
    "/{document_id}",
    summary="Проверка существования документа по ID",
)
def get_document(document_id: str, current_user: User = Depends(get_current_user)):
    """
    Проверяет, существует ли документ с указанным ID в системе.

    :raises HTTPException 404: Если документ с таким document_id не найден.
    """
    if not document_exists(document_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Документ с таким ID не найден")
    return {"document_id": document_id, "exists": True}