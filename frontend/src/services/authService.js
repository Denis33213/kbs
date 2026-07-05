import apiClient from "./apiClient";

/**
 * Регистрирует нового пользователя.
 *
 * @param {string} username - Логин пользователя.
 * @param {string} password - Пароль пользователя.
 * @returns {Promise<object>} Ответ сервера ({ msg, username }).
 */
export async function registerUser(username, password) {
  const { data } = await apiClient.post("/api/v1/auth/register", { username, password });
  return data;
}

/**
 * Аутентифицирует пользователя и получает JWT access-токен.
 *
 * Backend ожидает form-urlencoded тело (OAuth2PasswordRequestForm),
 * поэтому данные отправляются как URLSearchParams, а не JSON.
 *
 * @param {string} username - Логин пользователя.
 * @param {string} password - Пароль пользователя.
 * @returns {Promise<{access_token: string, token_type: string}>}
 */
export async function loginUser(username, password) {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);

  const { data } = await apiClient.post("/api/v1/auth/login", params);
  return data;
}