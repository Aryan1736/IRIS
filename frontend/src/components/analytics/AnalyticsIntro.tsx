import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface AnalyticsIntroProps {
  datasetInfo?: DatasetInfoResponse;
}

export const AnalyticsIntro: React.FC<AnalyticsIntroProps> = ({ datasetInfo }) => {
  const uniqueProjects = datasetInfo?.unique_projects_count != null
    ? datasetInfo.unique_projects_count.toLocaleString()
    : "—";

  const totalObs = datasetInfo?.row_count != null && datasetInfo.row_count > 0
    ? datasetInfo.row_count.toLocaleString()
    : "—";

  const months = datasetInfo?.covered_months || [];
  const period = months.length > 0
    ? `${months[0]} → ${months[months.length - 1]}`
    : "—";

  return (
    <header className="analytics-intro-header">
      <div className="analytics-breadcrumb">IRIS / ANALYTICS / PORTFOLIO ANALYSIS</div>
      <h1 className="analytics-main-title">UNDERSTAND HOW THE PORTFOLIO MOVES.</h1>
      <p className="analytics-subtitle">
        Longitudinal analysis of infrastructure activity, expenditure, schedule movement, completion progress, and portfolio composition across the monitored portfolio.
      </p>

      <div className="analytics-meta-strip">
        <div className="analytics-meta-item">
          <span className="analytics-meta-label">UNIQUE PROJECTS</span>
          <span className="analytics-meta-val">{uniqueProjects}</span>
        </div>

        <div className="analytics-meta-item">
          <span className="analytics-meta-label">OBSERVATIONS</span>
          <span className="analytics-meta-val">{totalObs}</span>
        </div>

        <div className="analytics-meta-item">
          <span className="analytics-meta-label">PERIOD</span>
          <span className="analytics-meta-val">{period}</span>
        </div>
      </div>
    </header>
  );
};
