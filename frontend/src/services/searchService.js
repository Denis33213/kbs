import apiClient from "./apiClient";

/**
 * Выполняет полнотекстовый поиск по документам с пагинацией.
 *
 * @param {string} query - Поисковый запрос.
 * @param {number} [page=1] - Номер страницы результатов (нумерация с 1).
 * @returns {Promise<{total: number, page: number, page_size: number, results: Array}>}
 */
export async function searchDocuments(query, page = 1) {
  const { data } = await apiClient.get("/api/v1/search", { params: { q: query, page } });
  return data;
}