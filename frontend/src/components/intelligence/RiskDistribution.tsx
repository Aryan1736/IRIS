import React from "react";
import type { ScoreDistribution } from "@/types/risk.ts";

interface RiskDistributionProps {
  distribution?: ScoreDistribution;
  reportMonth: string;
}

export const RiskDistribution: React.FC<RiskDistributionProps> = ({
  distribution,
  reportMonth,
}) => {
  const min = distribution?.minimum ?? 0;
  const p25 = distribution?.p25 ?? 0;
  const median = distribution?.median ?? 0;
  const p75 = distribution?.p75 ?? 0;
  const p90 = distribution?.p90 ?? 0;
  const p95 = distribution?.p95 ?? 0;
  const max = distribution?.maximum ?? 1;
  const mean = distribution?.mean ?? 0;

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <h2 className="intelligence-section-title">03. Model Output Distribution</h2>
        <span className="intelligence-section-subtitle">
          EMPIRICAL QUANTILE SUMMARY ({reportMonth})
        </span>
      </div>

      <div className="intelligence-dist-card">
        {/* Quantile Metric Cells */}
        <div className="intelligence-dist-stats-grid">
          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">MINIMUM</span>
            <span className="intelligence-dist-stat-val">{(min * 100).toFixed(2)}%</span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">P25 (25TH)</span>
            <span className="intelligence-dist-stat-val">{(p25 * 100).toFixed(1)}%</span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">MEDIAN (P50)</span>
            <span className="intelligence-dist-stat-val" style={{ color: "#1A3C2B" }}>
              {(median * 100).toFixed(1)}%
            </span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">MEAN</span>
            <span className="intelligence-dist-stat-val">{(mean * 100).toFixed(1)}%</span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">P75 (75TH)</span>
            <span className="intelligence-dist-stat-val">{(p75 * 100).toFixed(1)}%</span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">P90 (90TH)</span>
            <span className="intelligence-dist-stat-val" style={{ color: "#BA1A1A" }}>
              {(p90 * 100).toFixed(1)}%
            </span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">P95 (95TH)</span>
            <span className="intelligence-dist-stat-val" style={{ color: "#BA1A1A" }}>
              {(p95 * 100).toFixed(1)}%
            </span>
          </div>

          <div className="intelligence-dist-stat-cell">
            <span className="intelligence-dist-stat-label">MAXIMUM</span>
            <span className="intelligence-dist-stat-val" style={{ color: "#BA1A1A" }}>
              {(max * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Quantile Visual Timeline Canvas */}
        <div className="intelligence-dist-canvas">
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
            <span className="intelligence-section-subtitle">0.0 (MIN PROBABILITY)</span>
            <span className="intelligence-section-subtitle">1.0 (MAX PROBABILITY)</span>
          </div>

          <svg
            style={{ width: "100%", height: "60px" }}
            viewBox="0 0 500 50"
            preserveAspectRatio="none"
          >
            {/* Base Scale Line */}
            <line x1="0" y1="25" x2="500" y2="25" stroke="#E2E3DF" strokeWidth="4" />

            {/* Interquartile Range (P25 to P75) */}
            <rect
              x={p25 * 500}
              y="15"
              width={Math.max(2, (p75 - p25) * 500)}
              height="20"
              fill="#C5ECD3"
              stroke="#1A3C2B"
              strokeWidth="1"
            />

            {/* Median Mark */}
            <line
              x1={median * 500}
              y1="10"
              x2={median * 500}
              y2="40"
              stroke="#022617"
              strokeWidth="2.5"
            />

            {/* P90 & P95 Upper Threshold Marks */}
            <line
              x1={p90 * 500}
              y1="12"
              x2={p90 * 500}
              y2="38"
              stroke="#BA1A1A"
              strokeWidth="1.5"
              strokeDasharray="2 2"
            />
            <line
              x1={p95 * 500}
              y1="10"
              x2={p95 * 500}
              y2="40"
              stroke="#BA1A1A"
              strokeWidth="2"
            />
          </svg>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px" }}>
            <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
              IQR: [{(p25 * 100).toFixed(0)}% — {(p75 * 100).toFixed(0)}%]
            </span>
            <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "#1A3C2B", fontWeight: 600 }}>
              MEDIAN: {(median * 100).toFixed(1)}%
            </span>
            <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "#BA1A1A", fontWeight: 600 }}>
              95TH PERCENTILE: {(p95 * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
