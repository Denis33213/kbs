import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser, loginUser } from "../services/authService";
import { useAuth } from "../context/AuthContext.jsx";
import "./RegisterPage.css";

/**
 * Страница регистрации. После успешной регистрации автоматически
 * выполняет вход (backend не возвращает токен при регистрации,
 * поэтому логин выполняется отдельным запросом с теми же данными)
 * и перенаправляет на главную страницу.
 */
export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (password.length < 6) {
      setError("Пароль должен содержать не менее 6 символов");
      return;
    }
    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    setIsSubmitting(true);
    try {
      await registerUser(username, password);
      const { access_token } = await loginUser(username, password);
      login(access_token, username);
      navigate("/", { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Не удалось зарегистрироваться. Попробуйте другой логин.");
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
        <h1>Создать аккаунт</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <label className="field">
            <span>Логин</span>
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              minLength={3}
              maxLength={50}
              required
              autoFocus
              placeholder=""
            />
          </label>
          <label className="field">
            <span>Пароль</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={6}
              required
              placeholder="не менее 6 символов"
            />
          </label>
          <label className="field">
            <span>Повторите пароль</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={6}
              required
            />
          </label>
          {error && (
            <p className="field-error" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? "Создаём аккаунт…" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
}