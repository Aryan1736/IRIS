import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface ScheduleAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
}

export const ScheduleAnalytics: React.FC<ScheduleAnalyticsProps> = ({ datasetInfo }) => {
  const months = datasetInfo?.covered_months || [];
  const startMonth = months.length > 0 ? months[0] : "—";
  const endMonth = months.length > 0 ? months[months.length - 1] : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">02. Where Schedules Move</h2>
        <span className="analytics-section-subtitle">SCHEDULE EXTENSIONS & REVISIONS (DATA PENDING)</span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Schedule Movement Canvas */}
        <div className="analytics-canvas-box">
          <div className="analytics-canvas-empty">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-canvas-empty-label">
              PORTFOLIO-WIDE SCHEDULE EXTENSION DISTRIBUTION REQUIRES BACKEND AGGREGATION PIPELINE
            </div>
          </div>

          <div className="analytics-canvas-dates">
            <span>CADENCE START: {startMonth}</span>
            <span>LATEST CADENCE: {endMonth}</span>
          </div>
        </div>

        {/* Right: Metrics & Position Classification */}
        <div className="analytics-metrics-sidebar">
          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">Schedule Extensions</div>
            <div className="analytics-metric-subtext">REPORTED LONGITUDINAL OBSERVATIONS</div>
          </div>

          <div className="analytics-position-list">
            <span className="analytics-meta-label">Schedule Position</span>

            <div className="analytics-position-item">
              <span className="analytics-position-name">AHEAD</span>
              <span className="analytics-data-pending-badge">DATA PENDING</span>
            </div>

            <div className="analytics-position-item">
              <span className="analytics-position-name">WITHIN</span>
              <span className="analytics-data-pending-badge">DATA PENDING</span>
            </div>

            <div className="analytics-position-item">
              <span className="analytics-position-name">APPROACHING</span>
              <span className="analytics-data-pending-badge">DATA PENDING</span>
            </div>

            <div className="analytics-position-item">
              <span className="analytics-position-name">PAST</span>
              <span className="analytics-data-pending-badge">DATA PENDING</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
