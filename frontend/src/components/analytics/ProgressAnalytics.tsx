import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface ProgressAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
}

export const ProgressAnalytics: React.FC<ProgressAnalyticsProps> = ({ datasetInfo }) => {
  const uniqueProjects = datasetInfo?.unique_projects_count != null
    ? datasetInfo.unique_projects_count.toLocaleString()
    : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">05. Project Progress</h2>
        <span className="analytics-section-subtitle">PHYSICAL PROGRESS TRACKING (DATA PENDING)</span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Progress Tracking Note */}
        <div className="analytics-canvas-box">
          <div className="analytics-canvas-empty">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-canvas-empty-label">
              PORTFOLIO PHYSICAL PROGRESS AGGREGATION REQUIRES BACKEND PIPELINE. RECORD-LEVEL REPORTED PHYSICAL PROGRESS AVAILABLE IN PROJECT DIRECTORY.
            </div>
          </div>
        </div>

        {/* Right: Metrics Sidebar */}
        <div className="analytics-metrics-sidebar">
          <div className="analytics-metric-cell">
            <div className="analytics-metric-large-val">{uniqueProjects}</div>
            <div className="analytics-metric-label">Total Unique Monitored Projects</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Projects with Valid Progress</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Median Reported Progress</div>
          </div>
        </div>
      </div>
    </section>
  );
};
