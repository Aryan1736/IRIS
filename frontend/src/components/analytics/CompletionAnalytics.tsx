import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface CompletionAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
}

export const CompletionAnalytics: React.FC<CompletionAnalyticsProps> = ({ datasetInfo }) => {
  const months = datasetInfo?.covered_months || [];
  const startMonth = months.length > 0 ? months[0] : "—";
  const endMonth = months.length > 0 ? months[months.length - 1] : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">06. Completion Movement</h2>
        <span className="analytics-section-subtitle">SCHEDULE REVISION COMPARISON (DATA PENDING)</span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Completion Movement Canvas */}
        <div className="analytics-canvas-box">
          <div className="analytics-canvas-empty">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-canvas-empty-label">
              PORTFOLIO COMPLETION MOVEMENT ANALYSIS REQUIRES LONGITUDINAL AGGREGATION PIPELINE
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
            <div className="analytics-metric-label">Revised Completion</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">No Reported Revision</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Reported Extensions</div>
          </div>
        </div>
      </div>
    </section>
  );
};
