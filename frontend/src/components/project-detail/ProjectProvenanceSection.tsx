import React from "react";
import type { ProjectDetailResponse, ProjectMonthObservationRead } from "@/types/project.ts";

interface ProjectProvenanceSectionProps {
  project?: ProjectDetailResponse;
  snapshot?: ProjectMonthObservationRead;
  projectCode: string;
}

export const ProjectProvenanceSection: React.FC<ProjectProvenanceSectionProps> = ({
  project,
  snapshot,
  projectCode,
}) => {
  const obsCount = project?.total_observations_count ? `${project.total_observations_count}` : "—";
  const firstObs = project?.first_reported_month || "—";
  const lastObs = project?.latest_report_month || "—";
  const sourceFile = snapshot?.source_file || "PAIMANA FLASH REPORT";
  const extractionMethod = snapshot?.extraction_method || "CANONICAL PIPELINE";

  return (
    <section className="project-detail-section">
      <h2 className="project-section-title">BUILT FOR AUDITABILITY.</h2>

      <div className="provenance-audit-grid">
        <div className="provenance-audit-item">
          <span className="provenance-audit-label">Project Code</span>
          <span className="provenance-audit-val">{projectCode}</span>
        </div>

        <div className="provenance-audit-item">
          <span className="provenance-audit-label">Observations</span>
          <span className="provenance-audit-val">{obsCount}</span>
        </div>

        <div className="provenance-audit-item">
          <span className="provenance-audit-label">First Observed</span>
          <span className="provenance-audit-val">{firstObs}</span>
        </div>

        <div className="provenance-audit-item">
          <span className="provenance-audit-label">Last Observed</span>
          <span className="provenance-audit-val">{lastObs}</span>
        </div>

        <div className="provenance-audit-item">
          <span className="provenance-audit-label">Source Document</span>
          <span className="provenance-audit-val" style={{ wordBreak: "break-all" }}>{sourceFile}</span>
        </div>

        <div className="provenance-audit-item">
          <span className="provenance-audit-label">Extraction Method</span>
          <span className="provenance-audit-val verified">{extractionMethod}</span>
        </div>
      </div>
    </section>
  );
};
