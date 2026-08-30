import React from "react";

export const CostIntelligenceSection: React.FC = () => {
  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">FOLLOW THE MONEY.</h2>
      </div>

      <div className="dashboard-grid-1-2">
        {/* Left: Expenditure Trajectory */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">EXPENDITURE TRAJECTORY</span>
          </div>

          <div style={{ height: "240px", width: "100%", position: "relative", borderLeft: "1px solid var(--color-border-hairline)", borderBottom: "1px solid var(--color-border-hairline)" }}>
            <svg
              style={{ width: "100%", height: "100%" }}
              preserveAspectRatio="none"
              viewBox="0 0 100 100"
            >
              <path
                d="M0,90 Q25,85 50,60 T100,20"
                fill="none"
                stroke="var(--color-primary-950)"
                strokeWidth="2"
              />
            </svg>
            <div style={{ position: "absolute", bottom: "8px", right: "12px", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
              AGGREGATE EXPENDITURE EVOLUTION
            </div>
          </div>
        </div>

        {/* Right: Cost Revision Signal */}
        <div className="dashboard-card-paper">
          <div className="card-header-lockup">
            <span className="card-label">COST REVISION SIGNAL</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: "24px", fontWeight: 700, color: "var(--color-coral)" }}>
              DATA PENDING
            </div>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
              REPORTED EXPENDITURE / ORIGINAL COST
            </span>
          </div>

          <div style={{ marginTop: "auto" }}>
            <div
              style={{
                padding: "16px",
                border: "1px solid rgba(186, 26, 26, 0.25)",
                backgroundColor: "var(--color-risk-high-bg)",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", fontWeight: 600, color: "var(--color-coral)", textTransform: "uppercase" }}>
                ATTENTION REQUIRED
              </span>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-variant)", margin: 0, lineHeight: 1.4 }}>
                — projects show cumulative expenditure exceeding original cost baseline.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
