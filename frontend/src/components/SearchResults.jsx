import SearchResultCard from "./SearchResultCard.jsx";
import "./SearchResults.css";

/**
 * Отображает результаты поиска в виде списка карточек, либо сообщение
 * "ничего не найдено" (FE-08), если поиск выполнен, но результатов нет.
 * Ничего не рендерит, если поиск ещё не запускался.
 *
 * @param {Array} results - Результаты текущей страницы поиска.
 * @param {boolean} hasSearched - Был ли выполнен хотя бы один поиск.
 */
export default function SearchResults({ results, hasSearched }) {
  if (!hasSearched) return null;

  if (results.length === 0) {
    return (
      <p className="empty-hint empty-hint--results">
        По вашему запросу ничего не найдено. Попробуйте изменить формулировку.
      </p>
    );
  }

  const maxScore = Math.max(...results.map((result) => result.score), 0.0001);

  return (
    <ul className="results-list">
      {results.map((result) => (
        <SearchResultCard key={result.chunk_id} result={result} maxScore={maxScore} />
      ))}
    </ul>
  );
}
