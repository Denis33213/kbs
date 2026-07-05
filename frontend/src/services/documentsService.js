import apiClient from "./apiClient";

/**
 * Загружает документ на сервер с отслеживанием прогресса передачи байтов.
 *
 * Content-Type не задаётся вручную: axios сам формирует корректный
 * multipart/form-data заголовок с boundary при передаче FormData.
 *
 * @param {File} file - Файл для загрузки (PDF или DOCX).
 * @param {(percent: number) => void} [onProgress] - Вызывается с процентом загрузки (0-100).
 * @returns {Promise<{document_id: string, file_name: string, chunks_count: number, status: string}>}
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/api/v1/documents/upload", formData, {
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
  return data;
}

/**
 * Возвращает список уникальных документов, уже загруженных в систему.
 *
 * @returns {Promise<Array<{file_name: string, document_id: string|null, chunks_count: number}>>}
 */
export async function listDocuments() {
  const { data } = await apiClient.get("/api/v1/documents");
  return data;
}