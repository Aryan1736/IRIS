import React from "react";
import type { ProjectMonthObservationRead, ProjectDetailResponse } from "@/types/project.ts";

interface ProjectSignalsSectionProps {
  snapshot?: ProjectMonthObservationRead;
  project?: ProjectDetailResponse;
}

export const ProjectSignalsSection: React.FC<ProjectSignalsSectionProps> = ({
  snapshot,
  project,
}) => {
  const hasRevision = Boolean(snapshot?.revised_completion_date);
  const revDate = snapshot?.revised_completion_date || "NO REVISION REPORTED";

  const expValue = snapshot?.cumulative_expenditure !== null && snapshot?.cumulative_expenditure !== undefined
    ? `₹ ${snapshot.cumulative_expenditure.toLocaleString()} CR`
    : "NOT REPORTED";

  const progressValue = snapshot?.physical_progress !== null && snapshot?.physical_progress !== undefined
    ? `${snapshot.physical_progress}%`
    : "NOT REPORTED";

  const obsCount = project?.total_observations_count
    ? `${project.total_observations_count} OBSERVATIONS`
    : "CADENCE RECORDED";

  return (
    <section className="project-detail-section">
      <h2 className="project-section-title">SEE THE SIGNALS.</h2>

      <div className="signals-grid-4col">
        {/* Schedule */}
        <div className="signal-cell">
          <div className="signal-info-wrap">
            <span className="signal-sublabel">Schedule</span>
            <span className="signal-title">EXTENSION HISTORY</span>
          </div>
          <span className={`signal-tag ${hasRevision ? "review" : "stable"}`}>
            {hasRevision ? revDate : "UNCHANGED"}
          </span>
        </div>

        {/* Expenditure */}
        <div className="signal-cell">
          <div className="signal-info-wrap">
            <span className="signal-sublabel">Expenditure</span>
            <span className="signal-title">TRAJECTORY</span>
          </div>
          <span className="signal-tag">
            {expValue}
          </span>
        </div>

        {/* Progress */}
        <div className="signal-cell">
          <div className="signal-info-wrap">
            <span className="signal-sublabel">Progress</span>
            <span className="signal-title">CURRENT TRAJECTORY</span>
          </div>
          <span className="signal-tag">
            {progressValue}
          </span>
        </div>

        {/* Reporting */}
        <div className="signal-cell">
          <div className="signal-info-wrap">
            <span className="signal-sublabel">Reporting</span>
            <span className="signal-title">OBSERVATION CONTINUITY</span>
          </div>
          <span className="signal-tag stable">
            {obsCount}
          </span>
        </div>
      </div>

      <div className="signals-banner">
        MODEL CONNECTIVITY: <span style={{ color: "var(--color-primary-950)", fontWeight: 600 }}>PENDING</span>
      </div>
    </section>
  );
};
