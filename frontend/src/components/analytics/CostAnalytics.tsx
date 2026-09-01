import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface CostAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
}

export const CostAnalytics: React.FC<CostAnalyticsProps> = ({ datasetInfo }) => {
  const months = datasetInfo?.covered_months || [];
  const startMonth = months.length > 0 ? months[0] : "—";
  const endMonth = months.length > 0 ? months[months.length - 1] : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">03. Follow the Money</h2>
        <span className="analytics-section-subtitle">PORTFOLIO EXPENDITURE & CAPITAL FLOWS (DATA PENDING)</span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Expenditure Trajectory Canvas */}
        <div className="analytics-canvas-box">
          <div className="analytics-canvas-empty">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-canvas-empty-label">
              PORTFOLIO-WIDE EXPENDITURE TRAJECTORY REQUIRES BACKEND AGGREGATION PIPELINE
            </div>
          </div>

          <div className="analytics-canvas-dates">
            <span>CADENCE START: {startMonth}</span>
            <span>LATEST CADENCE: {endMonth}</span>
          </div>
        </div>

        {/* Right: Metrics Sidebar */}
        <div className="analytics-metrics-sidebar">
          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Total Reported Expenditure</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Original Cost</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Expenditure / Original Cost</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Projects with Reported Expenditure</div>
          </div>
        </div>
      </div>
    </section>
  );
};
