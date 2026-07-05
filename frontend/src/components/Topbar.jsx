import { useAuth } from "../context/AuthContext.jsx";
import "./Topbar.css";

/** Верхняя панель приложения: логотип, имя пользователя, кнопка выхода. */
export default function Topbar() {
  const { username, logout } = useAuth();

  return (
    <header className="topbar">
      <div className="topbar__brand">
        <span className="topbar__mark">KBS</span>
        <span className="topbar__tag">база знаний университета</span>
      </div>
      <div className="topbar__user">
        <span className="topbar__username">{username}</span>
        <button type="button" className="btn btn-ghost" onClick={logout}>
          Выйти
        </button>
      </div>
    </header>
  );
}
