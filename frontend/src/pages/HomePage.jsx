import { useCallback, useEffect, useRef, useState } from "react";
import Topbar from "../components/Topbar.jsx";
import DropZone from "../components/DropZone.jsx";
import UploadQueue from "../components/UploadQueue.jsx";
import DocumentsList from "../components/DocumentsList.jsx";
import SearchBar from "../components/SearchBar.jsx";
import SearchResults from "../components/SearchResults.jsx";
import Pagination from "../components/Pagination.jsx";
import { uploadDocument, listDocuments } from "../services/documentsService.js";
import { searchDocuments } from "../services/searchService.js";
import "./HomePage.css";

const ALLOWED_EXTENSIONS = ["pdf", "docx"];
const MAX_SIZE_BYTES = 20 * 1024 * 1024;

let uploadIdCounter = 0;

export default function HomePage() {
  const [documents, setDocuments] = useState([]);
  const [uploads, setUploads] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);

  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState({ total: 0, page: 1, page_size: 10, results: [] });
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState("");
  const uploadedAtRef = useRef(new Map());

  const refreshDocuments = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(
        data.map((doc) => ({
          ...doc,
          uploadedAt: uploadedAtRef.current.get(doc.file_name) ?? null,
        }))
      );
    } catch {
      // Не удалось обновить список — оставляем прежнее состояние, это не критично для остального интерфейса
    } finally {
      setIsLoadingDocuments(false);
    }
  }, []);

  useEffect(() => {
    refreshDocuments();
  }, [refreshDocuments]);

  const handleFilesSelected = useCallback(
    (files) => {
      files.forEach((file) => {
        const extension = file.name.split(".").pop()?.toLowerCase();
        const uploadId = `upload-${Date.now()}-${uploadIdCounter++}`;

        if (!ALLOWED_EXTENSIONS.includes(extension)) {
          setUploads((prev) => [
            ...prev,
            { id: uploadId, name: file.name, progress: 100, status: "error", errorMessage: "Поддерживаются только PDF и DOCX" },
          ]);
          return;
        }
        if (file.size > MAX_SIZE_BYTES) {
          setUploads((prev) => [
            ...prev,
            { id: uploadId, name: file.name, progress: 100, status: "error", errorMessage: "Файл больше 20 МБ" },
          ]);
          return;
        }

        setUploads((prev) => [...prev, { id: uploadId, name: file.name, progress: 0, status: "uploading", errorMessage: "" }]);

        uploadDocument(file, (percent) => {
          setUploads((prev) =>
            prev.map((item) =>
              item.id === uploadId
                ? { ...item, progress: percent, status: percent >= 100 ? "indexing" : "uploading" }
                : item
            )
          );
        })
          .then(() => {
            uploadedAtRef.current.set(file.name, new Date().toISOString());
            setUploads((prev) => prev.map((item) => (item.id === uploadId ? { ...item, status: "done", progress: 100 } : item)));
            refreshDocuments();
          })
          .catch((err) => {
            const detail = err.response?.data?.detail;
            setUploads((prev) =>
              prev.map((item) =>
                item.id === uploadId
                  ? { ...item, status: "error", errorMessage: typeof detail === "string" ? detail : "Не удалось загрузить файл" }
                  : item
              )
            );
          });
      });
    },
    [refreshDocuments]
  );

  const runSearch = useCallback(async (searchQuery, targetPage) => {
    setIsSearching(true);
    setSearchError("");
    try {
      const data = await searchDocuments(searchQuery, targetPage);
      setSearchResult(data);
      setHasSearched(true);
    } catch {
      setSearchError("Не удалось выполнить поиск. Попробуйте ещё раз.");
    } finally {
      setIsSearching(false);
    }
  }, []);

  function handleSearch(newQuery) {
    setQuery(newQuery);
    runSearch(newQuery, 1);
  }

  function handlePageChange(newPage) {
    runSearch(query, newPage);
  }

  return (
    <div className="app-shell">
      <Topbar />
      <main className="layout">
        <section className="panel panel--upload">
          <h2 className="panel__eyebrow">Загрузка</h2>
          <DropZone onFilesSelected={handleFilesSelected} />
          <UploadQueue uploads={uploads} />

          <h2 className="panel__eyebrow panel__eyebrow--spaced">
            Документы {documents.length > 0 && `(${documents.length})`}
          </h2>
          {isLoadingDocuments ? (
            <p className="empty-hint">Загрузка списка…</p>
          ) : (
            <DocumentsList documents={documents} />
          )}
        </section>

        <section className="panel panel--search">
          <h2 className="panel__eyebrow">Поиск</h2>
          <SearchBar onSearch={handleSearch} isSearching={isSearching} />
          {searchError && (
            <p className="field-error" role="alert">
              {searchError}
            </p>
          )}
          <SearchResults results={searchResult.results} hasSearched={hasSearched} />
          <Pagination
            page={searchResult.page}
            pageSize={searchResult.page_size}
            total={searchResult.total}
            onPageChange={handlePageChange}
          />
        </section>
      </main>
    </div>
  );
}