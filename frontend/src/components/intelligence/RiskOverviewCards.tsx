import React from "react";
import type { SummaryResponse } from "@/types/risk.ts";

interface RiskOverviewCardsProps {
  summary?: SummaryResponse;
}

export const RiskOverviewCards: React.FC<RiskOverviewCardsProps> = ({ summary }) => {
  const meanProb = summary?.score_distribution?.mean != null
    ? `${(summary.score_distribution.mean * 100).toFixed(1)}%`
    : "—";

  const medianProb = summary?.score_distribution?.median != null
    ? `${(summary.score_distribution.median * 100).toFixed(1)}%`
    : "—";

  const evaluatedCount = summary?.project_count != null
    ? summary.project_count.toLocaleString()
    : "—";

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <h2 className="intelligence-section-title">01. Portfolio Risk Overview</h2>
        <span className="intelligence-section-subtitle">EARLY WARNING RISK MODULES</span>
      </div>

      <div className="intelligence-overview-grid">
        {/* Module 1: Schedule Extension */}
        <div className="intelligence-overview-card">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <span className="intelligence-section-subtitle" style={{ color: "#1A3C2B", fontWeight: 700 }}>
              TARGET: SCHEDULE_EXT_3M
            </span>
            <h3 className="intelligence-overview-card-title">Schedule Extension</h3>
          </div>

          <div className="intelligence-overview-card-body">
            <div className="intelligence-overview-metric-row">
              <span>MEAN RISK:</span>
              <span className="intelligence-overview-metric-val">{meanProb}</span>
            </div>
            <div className="intelligence-overview-metric-row">
              <span>MEDIAN RISK:</span>
              <span className="intelligence-overview-metric-val">{medianProb}</span>
            </div>
            <div className="intelligence-overview-metric-row">
              <span>EVALUATED:</span>
              <span className="intelligence-overview-metric-val">{evaluatedCount} PROJECTS</span>
            </div>
            <div className="intelligence-overview-metric-row" style={{ borderTop: "1px solid rgba(0,0,0,0.06)", paddingTop: "4px" }}>
              <span>STATUS:</span>
              <span style={{ color: "#1A3C2B", fontWeight: 700 }}>LIVE SERVING ACTIVE</span>
            </div>
          </div>
        </div>

        {/* Module 2: Cost Escalation */}
        <div className="intelligence-overview-card">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <span className="intelligence-section-subtitle">TARGET: COST_GROWTH</span>
            <h3 className="intelligence-overview-card-title" style={{ color: "var(--color-text-secondary)" }}>
              Cost Escalation
            </h3>
          </div>

          <div className="intelligence-overview-card-body">
            <div className="intelligence-overview-metric-row">
              <span>OUTPUT:</span>
              <span>—</span>
            </div>
            <div className="intelligence-overview-metric-row">
              <span>MODEL STATUS:</span>
              <span style={{ color: "var(--color-text-muted)" }}>NOT YET DEPLOYED</span>
            </div>
            <div className="intelligence-overview-metric-row" style={{ borderTop: "1px solid rgba(0,0,0,0.06)", paddingTop: "4px" }}>
              <span>DATA BOUNDARY:</span>
              <span className="intelligence-badge-uncalibrated">DATA PENDING</span>
            </div>
          </div>
        </div>

        {/* Module 3: Project Trajectory */}
        <div className="intelligence-overview-card">
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <span className="intelligence-section-subtitle">TARGET: MULTI_METRIC</span>
            <h3 className="intelligence-overview-card-title" style={{ color: "var(--color-text-secondary)" }}>
              Project Trajectory
            </h3>
          </div>

          <div className="intelligence-overview-card-body">
            <div className="intelligence-overview-metric-row">
              <span>OUTPUT:</span>
              <span>—</span>
            </div>
            <div className="intelligence-overview-metric-row">
              <span>MODEL STATUS:</span>
              <span style={{ color: "var(--color-text-muted)" }}>NOT YET DEPLOYED</span>
            </div>
            <div className="intelligence-overview-metric-row" style={{ borderTop: "1px solid rgba(0,0,0,0.06)", paddingTop: "4px" }}>
              <span>DATA BOUNDARY:</span>
              <span className="intelligence-badge-uncalibrated">DATA PENDING</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
