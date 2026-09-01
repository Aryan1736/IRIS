import React from "react";
import type { ProjectTrajectoryResponse } from "@/types/project.ts";
import { ProjectTrajectoryChart } from "./ProjectTrajectoryChart.tsx";

interface ProjectTrajectorySectionProps {
  trajectoryData?: ProjectTrajectoryResponse;
}

export const ProjectTrajectorySection: React.FC<ProjectTrajectorySectionProps> = ({
  trajectoryData,
}) => {
  const points = trajectoryData?.trajectory || [];
  const hasData = points.length > 0;

  return (
    <section className="project-detail-section">
      <div className="project-section-header-wrap">
        <div>
          <span className="project-section-eyebrow">LONGITUDINAL OBSERVATIONS</span>
          <h2 className="project-section-title">EVERY PROJECT HAS A HISTORY.</h2>
        </div>
        <div className="project-section-side-note">
          PROJECT CODE + REPORT MONTH = OBSERVATION
        </div>
      </div>

      <div className="trajectory-canvas-box">
        {/* Subtle grid pattern */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.05,
            backgroundImage:
              "linear-gradient(to right, #727973 1px, transparent 1px), linear-gradient(to bottom, #727973 1px, transparent 1px)",
            backgroundSize: "40px 40px",
            pointerEvents: "none",
          }}
        />

        {/* Interactive Data-Driven Longitudinal Chart */}
        <ProjectTrajectoryChart observations={points} />
      </div>

      {/* Bottom observation cadence markers */}
      {hasData && (
        <div className="observation-cadence-strip">
          {points.map((pt, idx) => {
            const hasObservation = pt.physical_progress !== null || pt.cumulative_expenditure !== null;
            const parts = pt.report_month.split("-");
            const shortMonth = parts.length === 2 ? `${parts[1]}/${parts[0].slice(2)}` : pt.report_month;

            return (
              <div key={`${pt.report_month}-${idx}`} className="cadence-item">
                <div className={`cadence-marker ${hasObservation ? "" : "dim"}`} />
                <span className="cadence-month">{shortMonth}</span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
