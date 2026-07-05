import "./UploadQueue.css";

const STATUS_LABEL = {
  uploading: "Загрузка…",
  indexing: "Индексация…",
  done: "Готово",
  error: "Ошибка",
};

/**
 *
 * @param {Array<{id: string, name: string, progress: number, status: string, errorMessage?: string}>} uploads
 */
export default function UploadQueue({ uploads }) {
  if (uploads.length === 0) return null;

  return (
    <ul className="upload-queue">
      {uploads.map((item) => (
        <li key={item.id} className={`upload-item upload-item--${item.status}`}>
          <div className="upload-item__row">
            <span className="upload-item__name" title={item.name}>
              {item.name}
            </span>
            <span className="upload-item__status">{STATUS_LABEL[item.status]}</span>
          </div>
          <div className="upload-item__bar" aria-hidden="true">
            <div
              className="upload-item__bar-fill"
              style={{ width: `${item.status === "error" ? 100 : item.progress}%` }}
            />
          </div>
          {item.status === "error" && item.errorMessage && (
            <p className="upload-item__error">{item.errorMessage}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
