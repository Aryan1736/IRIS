import React from "react";
import type {
  ProjectCostRevisionsResponse,
  ProjectMonthObservationRead,
  ProjectTrajectoryResponse,
} from "@/types/project.ts";
import { ExpenditureTrajectoryChart } from "./ExpenditureTrajectoryChart.tsx";

interface ExpenditureTrajectorySectionProps {
  costData?: ProjectCostRevisionsResponse;
  snapshot?: ProjectMonthObservationRead;
  trajectoryData?: ProjectTrajectoryResponse;
}

export const ExpenditureTrajectorySection: React.FC<ExpenditureTrajectorySectionProps> = ({
  costData,
  snapshot,
  trajectoryData,
}) => {
  const revisions = costData?.revisions || [];
  const trajectoryPoints = trajectoryData?.trajectory || [];

  // Use full trajectory observations if available, otherwise fallback to cost revisions
  const observations = trajectoryPoints.length > 0
    ? trajectoryPoints.map((p) => ({
        report_month: p.report_month,
        cumulative_expenditure: p.cumulative_expenditure,
      }))
    : revisions.map((r) => ({
        report_month: r.report_month,
        cumulative_expenditure: r.cumulative_expenditure,
      }));

  const currentExp = snapshot?.cumulative_expenditure
    ?? observations[observations.length - 1]?.cumulative_expenditure
    ?? null;

  const originalCost = snapshot?.original_cost
    ?? costData?.latest_original_cost
    ?? (trajectoryPoints[0]?.original_cost ?? null);

  const currentExpText = currentExp !== null ? `₹ ${currentExp.toLocaleString()} CR` : "—";
  const origCostText = originalCost !== null ? `₹ ${originalCost.toLocaleString()} CR` : "—";

  const ratioText = currentExp !== null && originalCost !== null && originalCost > 0
    ? `${((currentExp / originalCost) * 100).toFixed(1)}%`
    : "—";

  return (
    <section className="project-detail-section">
      <h2 className="project-section-title">FOLLOW THE MONEY.</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }} className="lg:flex-row">
        {/* Left: Expenditure Trajectory Canvas */}
        <div
          style={{
            flex: 1,
            border: "1px solid var(--color-border-hairline)",
            padding: "24px",
            backgroundColor: "var(--color-surface)",
            height: "280px",
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--color-text-dim)",
              textTransform: "uppercase",
              marginBottom: "8px",
            }}
          >
            <span>CUMULATIVE EXPENDITURE (₹ CR)</span>
            <span>SANCTIONED COST REF</span>
          </div>

          <div style={{ position: "relative", width: "100%", height: "210px" }}>
            <ExpenditureTrajectoryChart
              observations={observations}
              originalCost={originalCost}
            />
          </div>
        </div>

        {/* Right: Summary Metrics */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", minWidth: "280px" }}>
          <div
            className="overview-metric-cell"
            style={{
              border: "1px solid var(--color-border-hairline)",
              backgroundColor: "var(--color-paper-light)",
            }}
          >
            <span className="overview-metric-label">Current Expenditure</span>
            <span className="overview-metric-val">{currentExpText}</span>
          </div>

          <div className="overview-metric-cell" style={{ border: "1px solid var(--color-border-hairline)" }}>
            <span className="overview-metric-label">Original Cost</span>
            <span className="overview-metric-val">{origCostText}</span>
          </div>

          <div className="overview-metric-cell" style={{ border: "1px solid var(--color-border-hairline)" }}>
            <span className="overview-metric-label">Expenditure / Original</span>
            <span className="overview-metric-val">{ratioText}</span>
          </div>
        </div>
      </div>

      <p
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "10px",
          color: "var(--color-text-dim)",
          margin: "8px 0 0 0",
        }}
      >
        Reported cumulative expenditure is an interim reporting measure and should not be interpreted as audited final project cost.
      </p>
    </section>
  );
};
