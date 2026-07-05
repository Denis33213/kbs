"""Юнит-тесты для app.services.chunker (BE-05, QA-01)."""

import pytest

from app.services.chunker import split_text_into_chunks


def test_empty_text_returns_empty_list():
    assert split_text_into_chunks("") == []


def test_chunk_size_and_overlap():
    text = "a" * 2500
    chunks = split_text_into_chunks(text, chunk_size=1000, overlap=100)
    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    # Проверяем, что перекрытие между соседними чанками действительно 100 символов
    assert chunks[0][-100:] == chunks[1][:100]


def test_short_text_returns_single_chunk():
    text = "короткий текст документа"
    chunks = split_text_into_chunks(text, chunk_size=1000, overlap=100)
    assert chunks == [text]


def test_default_parameters_match_requirements():
    text = "b" * 1500
    chunks = split_text_into_chunks(text)  # используем дефолты: 1000/100
    assert len(chunks[0]) == 1000


def test_overlap_equal_to_chunk_size_raises():
    with pytest.raises(ValueError):
        split_text_into_chunks("текст", chunk_size=100, overlap=100)


def test_negative_overlap_raises():
    with pytest.raises(ValueError):
        split_text_into_chunks("текст", chunk_size=100, overlap=-1)


def test_zero_chunk_size_raises():
    with pytest.raises(ValueError):
        split_text_into_chunks("текст", chunk_size=0, overlap=0)