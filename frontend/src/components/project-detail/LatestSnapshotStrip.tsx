import React from "react";
import type { ProjectMonthObservationRead } from "@/types/project.ts";
import { AlertTriangle } from "lucide-react";

interface LatestSnapshotStripProps {
  snapshot?: ProjectMonthObservationRead;
}

export const LatestSnapshotStrip: React.FC<LatestSnapshotStripProps> = ({
  snapshot,
}) => {
  const origCost = snapshot?.original_cost !== null && snapshot?.original_cost !== undefined
    ? `₹ ${snapshot.original_cost.toLocaleString()} CR`
    : "—";

  const origCompletion = snapshot?.original_completion_date || "—";

  const revCost = snapshot?.revised_cost !== null && snapshot?.revised_cost !== undefined
    ? `₹ ${snapshot.revised_cost.toLocaleString()} CR`
    : "NOT REPORTED";

  const revCompletion = snapshot?.revised_completion_date || "—";
  const hasScheduleShift = Boolean(
    snapshot?.original_completion_date &&
    snapshot?.revised_completion_date &&
    snapshot.original_completion_date !== snapshot.revised_completion_date
  );

  const progress = snapshot?.physical_progress !== null && snapshot?.physical_progress !== undefined
    ? `${snapshot.physical_progress}%`
    : "—";

  const expenditure = snapshot?.cumulative_expenditure !== null && snapshot?.cumulative_expenditure !== undefined
    ? `₹ ${snapshot.cumulative_expenditure.toLocaleString()} CR`
    : "—";

  return (
    <section className="project-overview-strip">
      {/* 01 / Original Cost */}
      <div className="overview-metric-cell">
        <span className="overview-metric-label">Original Cost</span>
        <span className="overview-metric-val">{origCost}</span>
      </div>

      {/* 02 / Original Completion */}
      <div className="overview-metric-cell">
        <span className="overview-metric-label">Original Completion</span>
        <span className="overview-metric-val">{origCompletion}</span>
      </div>

      {/* 03 / Revised Cost */}
      <div className="overview-metric-cell" style={{ backgroundColor: "var(--color-paper-light)" }}>
        <span className="overview-metric-label">Revised Cost</span>
        <span className={`overview-metric-val ${revCost === "NOT REPORTED" ? "unreported" : ""}`}>
          {revCost}
        </span>
      </div>

      {/* 04 / Revised Completion */}
      <div
        className="overview-metric-cell"
        style={{
          backgroundColor: hasScheduleShift ? "rgba(186, 26, 26, 0.05)" : "var(--color-surface)",
        }}
      >
        <span className={`overview-metric-label ${hasScheduleShift ? "coral" : ""}`}>
          {hasScheduleShift && <AlertTriangle size={12} color="var(--color-coral)" />}
          Revised Completion
        </span>
        <span className={`overview-metric-val ${hasScheduleShift ? "coral" : ""}`}>
          {revCompletion}
        </span>
      </div>

      {/* 05 / Physical Progress */}
      <div className="overview-metric-cell" style={{ backgroundColor: "rgba(197, 236, 211, 0.15)" }}>
        <span className="overview-metric-label">Progress</span>
        <span className="overview-metric-val" style={{ color: "var(--color-primary-container)" }}>
          {progress}
        </span>
      </div>

      {/* 06 / Cumulative Expenditure */}
      <div className="overview-metric-cell">
        <span className="overview-metric-label">Expenditure</span>
        <span className="overview-metric-val">{expenditure}</span>
      </div>
    </section>
  );
};
