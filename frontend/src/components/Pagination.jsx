import "./Pagination.css";

/**
 */
function getPageWindow(current, total, windowSize = 3) {
  if (total <= windowSize + 4) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages = [1];
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  if (start > 2) pages.push("ellipsis-start");
  for (let page = start; page <= end; page += 1) pages.push(page);
  if (end < total - 1) pages.push("ellipsis-end");
  pages.push(total);

  return pages;
}

/**
 *
 * @param {number} page - Текущая страница.
 * @param {number} pageSize - Размер страницы.
 * @param {number} total - Общее количество результатов.
 * @param {(page: number) => void} onPageChange
 */
export default function Pagination({ page, pageSize, total, onPageChange }) {
  const totalPages = Math.max(Math.ceil(total / pageSize), 1);
  if (totalPages <= 1) return null;

  const pages = getPageWindow(page, totalPages);

  return (
    <nav className="pagination" aria-label="Страницы результатов">
      <button
        type="button"
        className="pagination__nav"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Предыдущая страница"
      >
        ‹
      </button>
      {pages.map((item) =>
        typeof item === "number" ? (
          <button
            key={item}
            type="button"
            className={`pagination__page ${item === page ? "pagination__page--active" : ""}`}
            onClick={() => onPageChange(item)}
            aria-current={item === page ? "page" : undefined}
          >
            {item}
          </button>
        ) : (
          <span key={item} className="pagination__ellipsis">
            …
          </span>
        )
      )}
      <button
        type="button"
        className="pagination__nav"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Следующая страница"
      >
        ›
      </button>
    </nav>
  );
}
