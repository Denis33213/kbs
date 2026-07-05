import RelevanceMeter from "./RelevanceMeter.jsx";
import "./SearchResultCard.css";

/**
 * Карточка одного результата поиска (FE-05): название файла, номер страницы,
 * найденный фрагмент текста с подсветкой совпадений и оценка релевантности.
 *
 * Подсветка (FE-06) приходит готовой с backend в поле highlighted_text —
 * Elasticsearch оборачивает совпавшие слова в <mark>, а стиль .result-card__text mark
 * в index.css задаёт жёлтый фон.
 *
 * @param {object} result - Один элемент из ответа /api/v1/search.
 * @param {number} maxScore - Максимальный score среди результатов текущей страницы.
 */
export default function SearchResultCard({ result, maxScore }) {
  return (
    <li className="result-card">
      <div className="result-card__header">
        <span className="result-card__file" title={result.file_name}>
          {result.file_name}
        </span>
        <span className="result-card__page">стр. {result.page}</span>
      </div>
      <p
        className="result-card__text"
        dangerouslySetInnerHTML={{ __html: result.highlighted_text || result.text }}
      />
      <RelevanceMeter score={result.score} maxScore={maxScore} />
    </li>
  );
}
