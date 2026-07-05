import { createContext, useCallback, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
const STORAGE_KEY = "kb_auth";

function readStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

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


export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth должен использоваться внутри AuthProvider");
  }
  return ctx;
}