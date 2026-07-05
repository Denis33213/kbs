"""
Модуль разбиения извлечённого текста документа на чанки (сегменты).

Используется перед индексацией текста в Elasticsearch: длинный текст страницы
режется на перекрывающиеся фрагменты фиксированного размера, чтобы
полнотекстовый поиск и подсветка совпадений работали на компактных участках
текста, а не на целых страницах.
"""

from typing import List


def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Разбивает текст на чанки фиксированной длины с перекрытием между соседними чанками.

    :param text: Исходный текст для разбиения (например, текст одной страницы документа).
    :param chunk_size: Размер одного чанка в символах. По умолчанию 1000 (BE-05).
    :param overlap: Количество символов перекрытия между соседними чанками. По умолчанию 100 (BE-05).
    :return: Список текстовых чанков. Пустой список, если исходный текст пуст.
    :raises ValueError: Если overlap больше или равен chunk_size (иначе разбиение не продвигается вперёд).
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть положительным числом")
    if overlap < 0:
        raise ValueError("overlap не может быть отрицательным")
    if overlap >= chunk_size:
        raise ValueError("overlap должен быть меньше chunk_size, иначе разбиение зациклится")

    if not text:
        return []

    chunks: List[str] = []
    step = chunk_size - overlap
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks