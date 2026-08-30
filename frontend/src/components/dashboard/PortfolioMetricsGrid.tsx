import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface PortfolioMetricsGridProps {
  systemInfo?: DatasetInfoResponse;
}

export const PortfolioMetricsGrid: React.FC<PortfolioMetricsGridProps> = ({
  systemInfo,
}) => {
  const uniqueProjects = systemInfo?.unique_projects_count
    ? systemInfo.unique_projects_count.toLocaleString()
    : "—";

  const totalObservations = systemInfo?.row_count
    ? systemInfo.row_count.toLocaleString()
    : "—";

  const coveredMonthsCount = systemInfo?.covered_months && systemInfo.covered_months.length > 0
    ? `${systemInfo.covered_months.length} MOS`
    : "—";

  const coverageRange = () => {
    if (!systemInfo?.covered_months || systemInfo.covered_months.length === 0) return "—";
    const sorted = [...systemInfo.covered_months].sort();
    return `${sorted[0]} → ${sorted[sorted.length - 1]}`;
  };

  return (
    <section className="dashboard-metrics-grid">
      <div className="metric-cell">
        <span className="metric-cell-label">01 / ACTIVE PROJECTS</span>
        <span className="metric-cell-value">{uniqueProjects}</span>
      </div>

      <div className="metric-cell">
        <span className="metric-cell-label">02 / OBSERVATIONS</span>
        <span className="metric-cell-value">{totalObservations}</span>
      </div>

      <div className="metric-cell">
        <span className="metric-cell-label">03 / MONITORED PERIOD</span>
        <span className="metric-cell-value">{coveredMonthsCount}</span>
      </div>

      <div className="metric-cell">
        <span className="metric-cell-label">04 / COMPLETED</span>
        <span className="metric-cell-value">—</span>
      </div>

      <div className="metric-cell">
        <span className="metric-cell-label">05 / H=3 EXTENSION EVENTS</span>
        <span className="metric-cell-value error-signal">—</span>
        <p className="metric-cell-subtext">
          Observed effective schedule-extension events across eligible H=3 monitoring windows.
        </p>
      </div>

      <div className="metric-cell">
        <span className="metric-cell-label">06 / DATA COVERAGE</span>
        <span className="metric-cell-value" style={{ fontSize: "14px", marginTop: "4px", letterSpacing: "0.05em" }}>
          {coverageRange()}
        </span>
      </div>
    </section>
  );
};
