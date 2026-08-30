import React from "react";
import type { ProjectCostRevisionsResponse, ProjectMonthObservationRead } from "@/types/project.ts";

interface ExpenditureTrajectorySectionProps {
  costData?: ProjectCostRevisionsResponse;
  snapshot?: ProjectMonthObservationRead;
}

export const ExpenditureTrajectorySection: React.FC<ExpenditureTrajectorySectionProps> = ({
  costData,
  snapshot,
}) => {
  const revisions = costData?.revisions || [];
  const currentExp = snapshot?.cumulative_expenditure ?? revisions[revisions.length - 1]?.cumulative_expenditure ?? null;
  const originalCost = snapshot?.original_cost ?? costData?.latest_original_cost ?? null;

  const currentExpText = currentExp !== null ? `₹ ${currentExp.toLocaleString()} CR` : "—";
  const origCostText = originalCost !== null ? `₹ ${originalCost.toLocaleString()} CR` : "—";

  const ratioText = currentExp !== null && originalCost !== null && originalCost > 0
    ? `${((currentExp / originalCost) * 100).toFixed(1)}%`
    : "—";

  // Calculate authentic points for expenditure curve
  const validExpPoints: { x: number; y: number; val: number }[] = [];
  const allValues = [
    ...(originalCost ? [originalCost] : []),
    ...revisions.map((r) => r.cumulative_expenditure).filter((v): v is number => v !== null && v !== undefined),
  ];
  const maxVal = allValues.length > 0 ? Math.max(...allValues, 1) : 1;

  revisions.forEach((r, idx) => {
    if (r.cumulative_expenditure !== null && r.cumulative_expenditure !== undefined) {
      const x = revisions.length > 1 ? (idx / (revisions.length - 1)) * 100 : 50;
      const y = 90 - (r.cumulative_expenditure / maxVal) * 75;
      validExpPoints.push({ x, y, val: r.cumulative_expenditure });
    }
  });

  const expPathD = validExpPoints.length > 1
    ? `M ${validExpPoints.map((pt) => `${pt.x},${pt.y}`).join(" L ")}`
    : "";

  const sanctionedCostY = originalCost !== null && maxVal > 0
    ? Math.max(10, 90 - (originalCost / maxVal) * 75)
    : 25;

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
            height: "260px",
            position: "relative",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
            <span>CUMULATIVE EXPENDITURE (₹ CR)</span>
            <span>SANCTIONED COST REF</span>
          </div>

          <div style={{ position: "relative", width: "100%", height: "160px" }}>
            {validExpPoints.length > 0 ? (
              <svg
                style={{ width: "100%", height: "100%", position: "absolute", inset: 0 }}
                preserveAspectRatio="none"
                viewBox="0 0 100 100"
              >
                {/* Sanctioned Cost Reference Dashed Line */}
                {originalCost !== null && (
                  <line
                    x1="0"
                    y1={sanctionedCostY}
                    x2="100"
                    y2={sanctionedCostY}
                    stroke="var(--color-border-outline)"
                    strokeDasharray="4 4"
                    strokeWidth="1"
                    opacity="0.6"
                  />
                )}
                {/* Genuine Expenditure line */}
                {expPathD && (
                  <path
                    d={expPathD}
                    fill="none"
                    stroke="var(--color-primary-950)"
                    strokeWidth="2"
                  />
                )}
                {/* Genuine Data Points */}
                {validExpPoints.map((pt, i) => (
                  <circle
                    key={`exp-pt-${i}`}
                    cx={pt.x}
                    cy={pt.y}
                    r="2"
                    fill="var(--color-surface)"
                    stroke="var(--color-primary-950)"
                    strokeWidth="1.5"
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
                NO EXPENDITURE TRAJECTORY REPORTED
              </div>
            )}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
            <span>START</span>
            <span>LATEST OBSERVATION</span>
          </div>
        </div>

        {/* Right: Summary Metrics */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", minWidth: "280px" }}>
          <div className="overview-metric-cell" style={{ border: "1px solid var(--color-border-hairline)", backgroundColor: "var(--color-paper-light)" }}>
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

      <p style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", margin: "8px 0 0 0" }}>
        Reported cumulative expenditure is an interim reporting measure and should not be interpreted as audited final project cost.
      </p>
    </section>
  );
};
