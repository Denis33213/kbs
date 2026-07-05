# Тестовые документы (QA-03)

Набор файлов для проверки загрузки, парсинга и обработки ошибок.

| Файл | Назначение |
|---|---|
| `valid_document.pdf` | Корректный PDF, 2 страницы — проверка успешной загрузки и постраничного парсинга |
| `valid_document.docx` | Корректный DOCX — проверка успешной загрузки и извлечения текста |
| `empty_file.pdf` | Файл 0 байт с правильным расширением — должен вернуть 400 «Файл пуст» |
| `corrupted_file.pdf` | Файл с расширением `.pdf`, но без валидной структуры PDF внутри — должен вернуть 400 (парсинг падает контролируемо, не 500) |
| `unusual_font.docx` | DOCX с нестандартными шрифтами (Courier New, Comic Sans MS) — проверка, что извлечение текста не зависит от шрифта |

## Как использовать

Через Swagger UI (`/docs`) или curl:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <ваш_токен>" \
  -F "file=@backend/tests/fixtures/valid_document.pdf;type=application/pdf"
```

Ожидаемое поведение:
- `valid_document.pdf`, `valid_document.docx`, `unusual_font.docx` → `201 Created`
- `empty_file.pdf` → `400 Bad Request`
- `corrupted_file.pdf` → `400 Bad Request` (не `500` — это ключевая проверка обработки ошибок)
