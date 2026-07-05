import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { loginUser } from "../services/authService.js";
import { useAuth } from "../context/AuthContext.jsx";
import "./LoginPage.css";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const { access_token } = await loginUser(username, password);
      login(access_token, username);
      const redirectTo = location.state?.from ?? "/";
      navigate(redirectTo, { replace: true });
    } catch {
      setError("Неверный логин или пароль");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="auth-brand__mark">KBS</span>
          <span className="auth-brand__tag">база знаний университета</span>
        </div>
        <h1>Войти</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <label className="field">
            <span>Логин</span>
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              autoFocus
            />
          </label>
          <label className="field">
            <span>Пароль</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error && (
            <p className="field-error" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Выполняется вход…" : "Войти"}
          </button>
        </form>
        <p className="auth-switch">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}