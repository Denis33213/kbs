"""
Общая конфигурация pytest: подготавливает переменные окружения для тестов,
чтобы приложение не пыталось использовать production-значения по умолчанию.
"""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")

# Удаляем файл тестовой БД от предыдущих прогонов pytest. Без этого
# пользователи, зарегистрированные в прошлый запуск (alice_test, carol_test
# и т.д.), остаются в базе и тесты падают с "пользователь уже существует"
# или ошибочным паролем при повторном запуске.
_TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "test_ci.db")
if os.path.exists(_TEST_DB_PATH):
    os.remove(_TEST_DB_PATH)