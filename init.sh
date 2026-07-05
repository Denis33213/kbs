#!/usr/bin/env bash
#
# Скрипт инициализации (DO-07): ждёт готовности backend, создаёт тестового
# пользователя, скачивает 10 открытых PDF-документов и загружает их в
# систему через POST /api/v1/documents/upload.
#
# Использование:
#   ./init.sh
#
# Переменные окружения (необязательные):
#   API_URL        - адрес backend (по умолчанию http://localhost:8000)
#   INIT_USERNAME  - логин тестового пользователя (по умолчанию init_user)
#   INIT_PASSWORD  - пароль тестового пользователя (по умолчанию init_password123)

set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
INIT_USERNAME="${INIT_USERNAME:-init_user}"
INIT_PASSWORD="${INIT_PASSWORD:-init_password123}"
DOWNLOAD_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${DOWNLOAD_DIR}"
}
trap cleanup EXIT

echo "==> Ожидаем готовности backend по адресу ${API_URL}..."
attempt=0
until curl -sf "${API_URL}/health" > /dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ "${attempt}" -gt 30 ]; then
    echo "Backend не отвечает после 30 попыток. Прерываем." >&2
    exit 1
  fi
  sleep 2
done
echo "==> Backend готов."

echo "==> Регистрируем тестового пользователя '${INIT_USERNAME}' (если ещё не существует)..."
curl -sf -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${INIT_USERNAME}\", \"password\": \"${INIT_PASSWORD}\"}" \
  > /dev/null 2>&1 || echo "    Пользователь уже существует, продолжаем."

echo "==> Получаем токен доступа..."
LOGIN_RESPONSE=$(curl -sf -X POST "${API_URL}/api/v1/auth/login" \
  -d "username=${INIT_USERNAME}&password=${INIT_PASSWORD}")
TOKEN=$(echo "${LOGIN_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "${TOKEN}" ]; then
  echo "Не удалось получить токен доступа. Прерываем." >&2
  exit 1
fi
echo "==> Токен получен."

# 10 открытых научных PDF-документов с arXiv (свободный доступ, стабильные
# прямые ссылки на PDF) — используются как тестовые "лекции" для наполнения
# поиска содержательным текстом на английском языке.
declare -A LECTURES=(
  ["attention_is_all_you_need.pdf"]="https://arxiv.org/pdf/1706.03762"
  ["deep_residual_learning.pdf"]="https://arxiv.org/pdf/1512.03385"
  ["vgg_very_deep_convnets.pdf"]="https://arxiv.org/pdf/1409.1556"
  ["word2vec_efficient_estimation.pdf"]="https://arxiv.org/pdf/1301.3781"
  ["bert_pretraining.pdf"]="https://arxiv.org/pdf/1810.04805"
  ["generative_adversarial_networks.pdf"]="https://arxiv.org/pdf/1406.2661"
  ["auto_encoding_variational_bayes.pdf"]="https://arxiv.org/pdf/1312.6114"
  ["batch_normalization.pdf"]="https://arxiv.org/pdf/1502.03167"
  ["dropout_regularization.pdf"]="https://arxiv.org/pdf/1207.0580"
  ["neural_machine_translation_attention.pdf"]="https://arxiv.org/pdf/1409.0473"
)

echo "==> Скачиваем и загружаем ${#LECTURES[@]} тестовых документов..."
success_count=0
for filename in "${!LECTURES[@]}"; do
  url="${LECTURES[$filename]}"
  filepath="${DOWNLOAD_DIR}/${filename}"

  echo "    Скачиваем ${filename}..."
  if ! curl -sfL "${url}" -o "${filepath}"; then
    echo "    ПРОПУЩЕНО: не удалось скачать ${url}" >&2
    continue
  fi

  echo "    Загружаем ${filename} в систему..."
  if curl -sf -X POST "${API_URL}/api/v1/documents/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${filepath};type=application/pdf" > /dev/null; then
    success_count=$((success_count + 1))
    echo "    OK: ${filename} загружен и проиндексирован."
  else
    echo "    ПРОПУЩЕНО: ошибка загрузки ${filename}" >&2
  fi
done

echo "==> Готово: ${success_count} из ${#LECTURES[@]} документов успешно загружено."