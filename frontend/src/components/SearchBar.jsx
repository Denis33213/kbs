import { useState } from "react";
import "./SearchBar.css";

/**
 *
 * @param {(query: string) => void} onSearch
 * @param {boolean} isSearching
 */
export default function SearchBar({ onSearch, isSearching }) {
  const [query, setQuery] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      onSearch(trimmed);
    }
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Например: линейная алгебра, лекция 3…"
        aria-label="Поисковый запрос"
      />
      <button type="submit" className="btn btn-primary" disabled={isSearching || !query.trim()}>
        {isSearching ? "Ищем…" : "Найти"}
      </button>
    </form>
  );
}
