import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface AnalyticsDataProfileProps {
  datasetInfo?: DatasetInfoResponse;
}

export const AnalyticsDataProfile: React.FC<AnalyticsDataProfileProps> = ({
  datasetInfo,
}) => {
  const codedMonths = datasetInfo?.covered_months?.length ? `${datasetInfo.covered_months.length}` : "—";
  const uniqueProjects = datasetInfo?.unique_projects_count != null
    ? datasetInfo.unique_projects_count.toLocaleString()
    : "—";
  const rowCount = datasetInfo?.row_count != null && datasetInfo.row_count > 0
    ? datasetInfo.row_count.toLocaleString()
    : "—";

  return (
    <section className="analytics-data-profile-banner">
      <div className="analytics-data-profile-header">
        <h2 className="analytics-data-profile-title">07. Observations / Data Profile</h2>
        <span className="analytics-meta-label" style={{ color: "rgba(255, 255, 255, 0.7)" }}>
          AUDITABLE CANONICAL SPECIFICATION
        </span>
      </div>

      <div className="analytics-data-profile-grid">
        <div className="analytics-data-profile-cell">
          <span className="analytics-data-profile-val">{codedMonths}</span>
          <span className="analytics-data-profile-label">Coded Months</span>
        </div>

        <div className="analytics-data-profile-cell">
          <span className="analytics-data-profile-val">{uniqueProjects}</span>
          <span className="analytics-data-profile-label">Unique Projects</span>
        </div>

        <div className="analytics-data-profile-cell">
          <span className="analytics-data-profile-val">{rowCount}</span>
          <span className="analytics-data-profile-label">Project-Month Obs.</span>
        </div>

        <div className="analytics-data-profile-cell">
          <div
            style={{
              display: "inline-block",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "rgba(255, 255, 255, 0.9)",
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              padding: "4px 8px",
              border: "1px dashed rgba(255, 255, 255, 0.3)",
              width: "fit-content",
              marginBottom: "4px",
            }}
          >
            DATA PENDING
          </div>
          <span className="analytics-data-profile-label">Completed Records</span>
        </div>

        <div className="analytics-data-profile-cell">
          <div
            style={{
              display: "inline-block",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "rgba(255, 255, 255, 0.9)",
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              padding: "4px 8px",
              border: "1px dashed rgba(255, 255, 255, 0.3)",
              width: "fit-content",
              marginBottom: "4px",
            }}
          >
            DATA PENDING
          </div>
          <span className="analytics-data-profile-label">Extension Obs.</span>
        </div>
      </div>
    </section>
  );
};
