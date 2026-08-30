import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface ActivityAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
}

export const ActivityAnalytics: React.FC<ActivityAnalyticsProps> = ({ datasetInfo }) => {
  const observations = datasetInfo?.row_count != null && datasetInfo.row_count > 0
    ? datasetInfo.row_count.toLocaleString()
    : "—";

  const projects = datasetInfo?.unique_projects_count != null
    ? datasetInfo.unique_projects_count.toLocaleString()
    : "—";

  const months: string[] = datasetInfo?.covered_months || [];
  const monitoredMonthsCount = months.length > 0 ? months.length : "—";
  const startMonth = months.length > 0 ? months[0] : "—";
  const endMonth = months.length > 0 ? months[months.length - 1] : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">01. Portfolio Activity Over Time</h2>
        <span className="analytics-section-subtitle">DATA COVERAGE & MONITORED PERIOD</span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Time Coverage Canvas */}
        <div className="analytics-canvas-box">
          <div className="analytics-canvas-empty">
            <svg
              className="w-full"
              style={{ width: "100%", height: "120px" }}
              viewBox="0 0 400 60"
              preserveAspectRatio="none"
            >
              {/* Baseline */}
              <line x1="0" y1="30" x2="400" y2="30" stroke="#1A3C2B" strokeWidth="1" opacity="0.3" />
              {/* Coverage tick marks */}
              {months.map((m: string, idx: number) => {
                const x = (idx / Math.max(months.length - 1, 1)) * 380 + 10;
                return (
                  <g key={m}>
                    <line x1={x} y1="22" x2={x} y2="38" stroke="#1A3C2B" strokeWidth="1.5" />
                    <circle cx={x} cy="30" r="2.5" fill="#1A3C2B" />
                  </g>
                );
              })}
            </svg>
            <div className="analytics-canvas-empty-label">
              CANONICAL DATASET TEMPORAL COVERAGE ({months.length} CADENCE POINTS)
            </div>
          </div>

          <div className="analytics-canvas-dates">
            <span>{startMonth}</span>
            <span>{endMonth}</span>
          </div>
        </div>

        {/* Right: Metrics Sidebar */}
        <div className="analytics-metrics-sidebar">
          <div className="analytics-metric-cell">
            <div className="analytics-metric-large-val">{observations}</div>
            <div className="analytics-metric-label">OBSERVATIONS</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-metric-large-val">{projects}</div>
            <div className="analytics-metric-label">PROJECTS</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-metric-medium-val">{monitoredMonthsCount}</div>
            <div className="analytics-metric-label">MONITORED MONTHS</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">COMPLETED PROJECTS</div>
          </div>
        </div>
      </div>
    </section>
  );
};
