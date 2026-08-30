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
        {/* Left: Progress Classification Breakdown */}
        <div className="analytics-position-list">
          <div className="analytics-position-item">
            <span className="analytics-position-name">On Track</span>
            <span className="analytics-data-pending-badge">DATA PENDING</span>
          </div>

          <div className="analytics-position-item">
            <span className="analytics-position-name">At Risk</span>
            <span className="analytics-data-pending-badge">DATA PENDING</span>
          </div>

          <div className="analytics-position-item">
            <span className="analytics-position-name">Critical</span>
            <span className="analytics-data-pending-badge">DATA PENDING</span>
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
