import { useCallback, useRef, useState } from "react";
import "./DropZone.css";

const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];

/**
 * Область для перетаскивания файлов с поддержкой множественной загрузки (FE-01).
 * Также поддерживает выбор файлов кликом (открывает системный диалог).
 *
 * @param {(files: File[]) => void} onFilesSelected - Вызывается с массивом выбранных файлов.
 * @param {boolean} [disabled] - Блокирует зону на время активных операций.
 */
export default function DropZone({ onFilesSelected, disabled }) {
  const inputRef = useRef(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleFiles = useCallback(
    (fileList) => {
      const files = Array.from(fileList || []);
      if (files.length > 0) {
        onFilesSelected(files);
      }
    },
    [onFilesSelected]
  );

  function handleDrop(event) {
    event.preventDefault();
    setIsDragActive(false);
    if (disabled) return;
    handleFiles(event.dataTransfer.files);
  }

  function handleDragOver(event) {
    event.preventDefault();
    if (!disabled) setIsDragActive(true);
  }

  function handleDragLeave() {
    setIsDragActive(false);
  }

  function handleInputChange(event) {
    handleFiles(event.target.files);
    event.target.value = "";
  }

  function handleKeyDown(event) {
    if ((event.key === "Enter" || event.key === " ") && !disabled) {
      event.preventDefault();
      inputRef.current?.click();
    }
  }

  return (
    <div
      className={`dropzone ${isDragActive ? "dropzone--active" : ""} ${
        disabled ? "dropzone--disabled" : ""
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label="Загрузить документы"
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS.join(",")}
        multiple
        hidden
        onChange={handleInputChange}
        disabled={disabled}
      />
      <svg className="dropzone__icon" width="32" height="32" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 3v12m0-12 4 4m-4-4-4 4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <p className="dropzone__title">Перетащите файлы сюда</p>
      <p className="dropzone__hint">или нажмите, чтобы выбрать · PDF, DOCX · до 20 МБ</p>
    </div>
  );
}
