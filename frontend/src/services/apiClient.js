import axios from "axios";

const STORAGE_KEY = "kb_auth";

/**
 * Единый экземпляр axios для всех запросов к бэкенду.
 * Базовый URL берётся из переменной окружения VITE_API_URL (см. .env.example).
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Автоматически прикрепляем JWT-токен из localStorage к каждому запросу,
// если пользователь авторизован.
apiClient.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const { token } = JSON.parse(raw);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch {
    // Повреждённые данные в localStorage игнорируем — запрос уйдёт без токена
  }
  return config;
});

// При получении 401 (токен истёк/недействителен) принудительно разлогиниваем
// пользователя через глобальное событие, которое слушает AuthContext.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  }
);

export default apiClient;