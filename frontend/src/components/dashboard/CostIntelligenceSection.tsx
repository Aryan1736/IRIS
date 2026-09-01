import React from "react";
import { Link } from "react-router-dom";

export const CostIntelligenceSection: React.FC = () => {
  return (
    <section className="dashboard-section">
      <div
        className="dashboard-section-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <h2 className="dashboard-section-title">FOLLOW THE MONEY.</h2>
        <Link
          to="/analytics"
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--color-primary-950)",
            textDecoration: "none",
            fontWeight: 600,
            transition: "opacity 150ms ease",
          }}
        >
          VIEW COST ANALYTICS →
        </Link>
      </div>

      <div className="dashboard-grid-1-2">
        {/* Left: Expenditure Trajectory */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">EXPENDITURE TRAJECTORY</span>
            <span className="card-tag-pending">DATA PENDING</span>
          </div>

          <div
            style={{
              height: "200px",
              width: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              border: "1px dashed var(--color-border-hairline)",
              margin: "16px 0 8px 0",
              padding: "16px",
              textAlign: "center",
            }}
          >
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                fontWeight: 600,
                color: "var(--color-coral)",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              DATA PENDING
            </span>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--color-text-dim)",
                textTransform: "uppercase",
                maxWidth: "420px",
                lineHeight: 1.4,
              }}
            >
              PORTFOLIO-WIDE EXPENDITURE TRAJECTORY REQUIRES BACKEND AGGREGATION PIPELINE. PROJECT-LEVEL EXPENDITURE EVOLUTION AVAILABLE VIA PROJECT DETAIL.
            </span>
          </div>

          <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase", textAlign: "right" }}>
            AGGREGATE EXPENDITURE EVOLUTION
          </div>
        </div>

        {/* Right: Cost Revision Signal */}
        <div className="dashboard-card-paper">
          <div className="card-header-lockup">
            <span className="card-label">COST REVISION SIGNAL</span>
            <span className="card-tag-pending">DATA PENDING</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "12px" }}>
            <div style={{ fontFamily: "var(--font-heading)", fontSize: "24px", fontWeight: 700, color: "var(--color-coral)" }}>
              DATA PENDING
            </div>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
              REPORTED EXPENDITURE / ORIGINAL COST
            </span>
          </div>

          <div style={{ marginTop: "auto", paddingTop: "16px" }}>
            <div
              style={{
                padding: "16px",
                border: "1px solid var(--color-border-hairline)",
                backgroundColor: "var(--color-surface)",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", fontWeight: 600, color: "var(--color-text-main)", textTransform: "uppercase" }}>
                BASELINE OBSERVATION NOTE
              </span>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-variant)", margin: 0, lineHeight: 1.4 }}>
                Cumulative expenditure vs original cost ratio is evaluated on individual project records.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
