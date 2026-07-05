import "./DocumentsList.css";

/**
 * @param {string|Date} value
 */
function formatDate(value) {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "дата неизвестна";
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 *
 * @param {Array<{file_name: string, document_id: string|null, chunks_count: number, uploadedAt?: string|Date|null}>} documents
 */
export default function DocumentsList({ documents }) {
  if (documents.length === 0) {
    return <p className="empty-hint">Пока нет загруженных документов.</p>;
  }

  return (
    <ul className="documents-list">
      {documents.map((doc) => (
        <li key={doc.document_id ?? doc.file_name} className="documents-list__item">
          <div className="documents-list__icon" aria-hidden="true">
            {doc.file_name.toLowerCase().endsWith(".pdf") ? "PDF" : "DOC"}
          </div>
          <div className="documents-list__meta">
            <span className="documents-list__name" title={doc.file_name}>
              {doc.file_name}
            </span>
            <span className="documents-list__sub">
              {doc.uploadedAt ? formatDate(doc.uploadedAt) : "дата неизвестна"} · {doc.chunks_count} фрагм.
            </span>
          </div>
          <span className="documents-list__status">Готово</span>
        </li>
      ))}
    </ul>
  );
}