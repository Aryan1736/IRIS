import React from "react";
import type { ProjectDetailResponse } from "@/types/project.ts";

interface ProjectDetailHeaderProps {
  project?: ProjectDetailResponse;
  projectCode: string;
}

export const ProjectDetailHeader: React.FC<ProjectDetailHeaderProps> = ({
  project,
  projectCode,
}) => {
  const projectName = project?.project_name || "PROJECT DETAIL";
  const sector = project?.sector || "—";
  const agency = project?.agency || "—";
  const state = project?.state || "—";
  const firstObs = project?.first_reported_month || "—";
  const lastObs = project?.latest_report_month || "—";
  const obsCount = project?.total_observations_count ? `${project.total_observations_count}` : "—";

  return (
    <header className="project-header-lockup">
      <div className="project-title-area">
        <div className="project-code-tag-wrap">
          <span className="project-code-pill">{projectCode}</span>
          <span className="project-record-label">INFRASTRUCTURE RECORD</span>
        </div>

        <h1 className="project-main-title">{projectName}</h1>

        <div className="project-meta-pills">
          <div className="project-meta-item">
            <span className="project-meta-label">SECTOR:</span>
            <span>{sector}</span>
          </div>

          <div className="project-meta-item">
            <span className="project-meta-label">AGENCY:</span>
            <span>{agency}</span>
          </div>

          <div className="project-meta-item">
            <span className="project-meta-label">STATE:</span>
            <span>{state}</span>
          </div>

          <div className="project-meta-item">
            <span className="project-meta-label">STATUS:</span>
            <span className="project-status-badge">
              <span className="status-dot-active" />
              <span>MONITORED</span>
            </span>
          </div>
        </div>
      </div>

      <div className="project-header-telemetry">
        <div className="telemetry-row">
          <span className="telemetry-label">FIRST OBSERVED:</span>
          <span>{firstObs}</span>
        </div>
        <div className="telemetry-row">
          <span className="telemetry-label">LAST OBSERVED:</span>
          <span>{lastObs}</span>
        </div>
        <div className="telemetry-row">
          <span className="telemetry-label">OBSERVATIONS:</span>
          <span>{obsCount}</span>
        </div>
        <div className="telemetry-row" style={{ marginTop: "4px", paddingTop: "6px", borderTop: "1px solid var(--color-border-hairline)" }}>
          <span className="telemetry-label">SOURCE:</span>
          <span>PAIMANA MONITORING DATA</span>
        </div>
      </div>
    </header>
  );
};
