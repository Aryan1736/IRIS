import React from "react";
import type { ProjectTrajectoryResponse } from "@/types/project.ts";

interface ProjectTrajectorySectionProps {
  trajectoryData?: ProjectTrajectoryResponse;
}

export const ProjectTrajectorySection: React.FC<ProjectTrajectorySectionProps> = ({
  trajectoryData,
}) => {
  const points = trajectoryData?.trajectory || [];
  const hasData = points.length > 0;

  const firstMonth = points[0]?.report_month || "—";
  const lastMonth = points[points.length - 1]?.report_month || "—";

  // Build authentic SVG path points for physical progress
  const validProgressPoints: { x: number; y: number; val: number; month: string }[] = [];

  points.forEach((p, idx) => {
    if (p.physical_progress !== null && p.physical_progress !== undefined) {
      const x = points.length > 1 ? (idx / (points.length - 1)) * 100 : 50;
      const y = 90 - (Math.min(Math.max(p.physical_progress, 0), 100) / 100) * 80;
      validProgressPoints.push({ x, y, val: p.physical_progress, month: p.report_month });
    }
  });

  const progressPathD = validProgressPoints.length > 1
    ? `M ${validProgressPoints.map((pt) => `${pt.x},${pt.y}`).join(" L ")}`
    : "";

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
        {/* Subtle 40px grid overlay */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.08,
            backgroundImage:
              "linear-gradient(to right, #727973 1px, transparent 1px), linear-gradient(to bottom, #727973 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        {/* Authentic Time series visualization */}
        {validProgressPoints.length > 0 ? (
          <svg
            style={{ width: "100%", height: "100%", position: "absolute", inset: 0 }}
            preserveAspectRatio="none"
            viewBox="0 0 100 100"
          >
            {/* Progress line */}
            {progressPathD && (
              <path
                d={progressPathD}
                fill="none"
                stroke="var(--color-primary-950)"
                strokeWidth="1.5"
              />
            )}
            {/* Data Point Markers */}
            {validProgressPoints.map((pt, i) => (
              <circle
                key={`dot-${i}`}
                cx={pt.x}
                cy={pt.y}
                r="1.8"
                fill="var(--color-surface)"
                stroke="var(--color-primary-950)"
                strokeWidth="1"
              />
            ))}
          </svg>
        ) : (
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              color: "var(--color-text-dim)",
            }}
          >
            NO LONGITUDINAL PROGRESS OBSERVATIONS REPORTED
          </div>
        )}

        <div
          style={{
            position: "absolute",
            bottom: "8px",
            left: "16px",
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            color: "var(--color-text-dim)",
          }}
        >
          {firstMonth}
        </div>
        <div
          style={{
            position: "absolute",
            bottom: "8px",
            right: "16px",
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            color: "var(--color-text-dim)",
          }}
        >
          {lastMonth}
        </div>
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
