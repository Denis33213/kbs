"""
Модуль извлечения текста из загруженных документов.

Поддерживаемые форматы: PDF (через pdfplumber) и DOCX (через python-docx),
как того требует BE-04. Каждая функция возвращает текст, разбитый по страницам
(для DOCX — условно единая "страница", так как формат не хранит разбиение
на страницы в структуре файла).
"""

import io
import logging
from typing import List, Dict

import pdfplumber
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> List[Dict]:
    """
    Извлекает текст из PDF-файла постранично.

    :param file_bytes: Содержимое PDF-файла в виде байтов.
    :return: Список словарей вида {"page_number": int, "text": str} для непустых страниц.
    :raises ValueError: Если файл повреждён или не может быть прочитан как PDF.
    """
    pages: List[Dict] = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({"page_number": i, "text": text.strip()})
    except Exception as exc:
        logger.error("Не удалось разобрать PDF-файл: %s", exc)
        raise ValueError("Не удалось прочитать PDF-файл: файл повреждён или имеет некорректный формат") from exc

    return pages


def extract_text_from_docx(file_bytes: bytes) -> List[Dict]:
    """
    Извлекает текст из DOCX-файла.

    DOCX не хранит явное разбиение на страницы, поэтому весь текст
    возвращается как единая условная "страница" с номером 1.

    :param file_bytes: Содержимое DOCX-файла в виде байтов.
    :return: Список из одного словаря {"page_number": 1, "text": str}, либо пустой список,
        если документ не содержит текста.
    :raises ValueError: Если файл повреждён или не может быть прочитан как DOCX.
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
    except PackageNotFoundError as exc:
        logger.error("Не удалось разобрать DOCX-файл: %s", exc)
        raise ValueError("Не удалось прочитать DOCX-файл: файл повреждён или имеет некорректный формат") from exc
    except Exception as exc:
        logger.error("Неожиданная ошибка при разборе DOCX-файла: %s", exc)
        raise ValueError("Не удалось прочитать DOCX-файл: файл повреждён или имеет некорректный формат") from exc

    full_text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())

    if not full_text:
        return []

    return [{"page_number": 1, "text": full_text}]