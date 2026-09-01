import React from "react";
import { Link } from "react-router-dom";

export const ScheduleIntelligenceSection: React.FC = () => {
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
        <h2 className="dashboard-section-title">WHERE SCHEDULES MOVE.</h2>
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
          VIEW SCHEDULE ANALYTICS →
        </Link>
      </div>

      <div className="dashboard-grid-2-col">
        {/* Left: Schedule Extensions Card */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">SCHEDULE EXTENSIONS</span>
            <span className="card-tag-pending">DATA PENDING</span>
          </div>

          <div
            style={{
              height: "180px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              border: "1px dashed var(--color-border-hairline)",
              margin: "16px 0",
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
                maxWidth: "400px",
                lineHeight: 1.4,
              }}
            >
              PORTFOLIO-WIDE SCHEDULE EXTENSION AGGREGATION REQUIRES BACKEND PIPELINE. PROJECT-LEVEL SCHEDULE REVISIONS AVAILABLE VIA PROJECT DETAIL.
            </span>
          </div>

          <p style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", fontStyle: "italic", margin: 0 }}>
            NOTE: Observed extension events represent historical reporting shifts, not necessarily terminal project failure.
          </p>
        </div>

        {/* Right: Schedule Position Card */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">SCHEDULE POSITION CLASSIFICATION</span>
            <span className="card-tag-pending">DATA PENDING</span>
          </div>

          <div
            style={{
              height: "180px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              border: "1px dashed var(--color-border-hairline)",
              margin: "16px 0",
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
                maxWidth: "400px",
                lineHeight: 1.4,
              }}
            >
              SCHEDULE POSITION AGGREGATION REQUIRES BACKEND DATA
            </span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
            <span>ORIGINAL COMPLETION BOUNDARY</span>
            <span>REVISED COMPLETION BOUNDARY</span>
          </div>
        </div>
      </div>
    </section>
  );
};
