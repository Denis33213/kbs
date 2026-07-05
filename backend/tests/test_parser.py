"""Юнит-тесты для app.services.parser (BE-04, QA-01, QA-03)."""

import io

import pytest
from docx import Document

from app.services.parser import extract_text_from_docx, extract_text_from_pdf


def _make_docx_bytes(paragraphs):
    """Собирает валидный DOCX-файл в памяти из списка абзацев для тестов."""
    doc = Document()
    for paragraph_text in paragraphs:
        doc.add_paragraph(paragraph_text)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def test_extract_text_from_docx_valid_file():
    content = _make_docx_bytes(["Первый абзац", "Второй абзац"])
    pages = extract_text_from_docx(content)
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "Первый абзац" in pages[0]["text"]
    assert "Второй абзац" in pages[0]["text"]


def test_extract_text_from_docx_empty_document_returns_empty_list():
    content = _make_docx_bytes([])
    assert extract_text_from_docx(content) == []


def test_extract_text_from_docx_corrupted_file_raises_value_error():
    with pytest.raises(ValueError):
        extract_text_from_docx(b"this is not a valid docx binary content")


def test_extract_text_from_pdf_corrupted_file_raises_value_error():
    with pytest.raises(ValueError):
        extract_text_from_pdf(b"this is not a valid pdf binary content")


def test_extract_text_from_pdf_empty_bytes_raises_value_error():
    with pytest.raises(ValueError):
        extract_text_from_pdf(b"")