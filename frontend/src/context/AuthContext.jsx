import { createContext, useCallback, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
const STORAGE_KEY = "kb_auth";

/** Читает сохранённые данные авторизации из localStorage. */
function readStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Провайдер авторизации: хранит JWT-токен и логин пользователя,
 * сохраняет их в localStorage между перезагрузками страницы.
 *
 * Также слушает глобальное событие "auth:logout" — его генерирует
 * apiClient при получении 401 от сервера (например, если токен истёк),
 * чтобы принудительно разлогинить пользователя.
 */
export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(readStoredAuth);

  const login = useCallback((token, username) => {
    const value = { token, username };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    setAuth(value);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setAuth(null);
  }, []);

  useEffect(() => {
    function handleForcedLogout() {
      logout();
    }
    window.addEventListener("auth:logout", handleForcedLogout);
    return () => window.removeEventListener("auth:logout", handleForcedLogout);
  }, [logout]);

  const value = {
    token: auth?.token ?? null,
    username: auth?.username ?? null,
    isAuthenticated: Boolean(auth?.token),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/** Хук доступа к контексту авторизации. Должен использоваться внутри AuthProvider. */
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth должен использоваться внутри AuthProvider");
  }
  return ctx;
}