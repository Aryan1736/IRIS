import React from "react";
import type { ProjectTrajectoryResponse } from "@/types/project.ts";

interface SourceObservationTableProps {
  trajectoryData?: ProjectTrajectoryResponse;
}

export const SourceObservationTable: React.FC<SourceObservationTableProps> = ({
  trajectoryData,
}) => {
  const points = trajectoryData?.trajectory ? [...trajectoryData.trajectory].reverse() : [];

  return (
    <section className="project-detail-section">
      <div className="project-section-header-wrap">
        <h2 className="project-section-title">SOURCE RECORD.</h2>
        <span className="project-section-side-note">
          {points.length} MONTHLY OBSERVATIONS
        </span>
      </div>

      <div style={{ width: "100%", overflowX: "auto", border: "1px solid var(--color-border-hairline)", backgroundColor: "var(--color-surface)" }}>
        <table className="detail-table">
          <thead>
            <tr>
              <th>REPORT MONTH</th>
              <th>COST (₹ CR)</th>
              <th>CUM. EXPENDITURE</th>
              <th>PROGRESS</th>
              <th>ORIG. COMPLETION</th>
              <th>REV. COMPLETION</th>
            </tr>
          </thead>
          <tbody>
            {points.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", padding: "24px", color: "var(--color-text-dim)" }}>
                  NO OBSERVATION RECORDS RECORDED
                </td>
              </tr>
            ) : (
              points.map((obs, idx) => {
                const cost = obs.revised_cost ?? obs.original_cost;
                const costText = cost !== null && cost !== undefined ? cost.toLocaleString() : "—";
                const expText = obs.cumulative_expenditure !== null && obs.cumulative_expenditure !== undefined
                  ? obs.cumulative_expenditure.toLocaleString()
                  : "—";
                const progressText = obs.physical_progress !== null && obs.physical_progress !== undefined
                  ? `${obs.physical_progress}%`
                  : "—";
                const origComp = obs.original_completion_date || "—";
                const revComp = obs.revised_completion_date || "—";
                const isShifted = obs.revised_completion_date && obs.original_completion_date && obs.revised_completion_date !== obs.original_completion_date;

                return (
                  <tr key={`${obs.report_month}-${idx}`}>
                    <td style={{ fontWeight: 600 }}>{obs.report_month}</td>
                    <td>{costText}</td>
                    <td>{expText}</td>
                    <td>{progressText}</td>
                    <td>{origComp}</td>
                    <td style={{ color: isShifted ? "var(--color-coral)" : "inherit" }}>
                      {revComp}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
};
