import "./RelevanceMeter.css";

const BAR_THRESHOLDS = [0.2, 0.4, 0.6, 0.8, 1];

/**
 *
 * @param {number} score - Оценка релевантности от Elasticsearch.
 * @param {number} maxScore - Максимальный score среди результатов текущей страницы.
 */
export default function RelevanceMeter({ score, maxScore }) {
  const ratio = maxScore > 0 ? Math.min(score / maxScore, 1) : 0;

  return (
    <div className="relevance" title={`Оценка релевантности: ${score.toFixed(2)}`}>
      <div className="relevance__bars" aria-hidden="true">
        {BAR_THRESHOLDS.map((threshold, index) => (
          <span
            key={threshold}
            className={`relevance__bar ${ratio >= threshold - 0.001 ? "relevance__bar--filled" : ""}`}
            style={{ height: `${6 + index * 4}px` }}
          />
        ))}
      </div>
      <span className="relevance__value">{score.toFixed(2)}</span>
    </div>
  );
}
