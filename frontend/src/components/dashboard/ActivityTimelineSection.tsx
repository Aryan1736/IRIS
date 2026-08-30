import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface ActivityTimelineSectionProps {
  systemInfo?: DatasetInfoResponse;
}

export const ActivityTimelineSection: React.FC<ActivityTimelineSectionProps> = ({
  systemInfo,
}) => {
  const months = systemInfo?.covered_months && systemInfo.covered_months.length > 0
    ? [...systemInfo.covered_months].sort()
    : ["2023-01", "2024-01", "2025-01", "2026-01", "2026-07"];

  // Display representative milestones across the timeline
  const displayMilestones = [
    months[0],
    months[Math.floor(months.length * 0.25)] || months[0],
    months[Math.floor(months.length * 0.5)] || months[0],
    months[Math.floor(months.length * 0.75)] || months[months.length - 1],
    months[months.length - 1],
  ].filter((v, i, a) => a.indexOf(v) === i);

  const uniqueProjectsCount = systemInfo?.unique_projects_count
    ? `N=${systemInfo.unique_projects_count.toLocaleString()}`
    : "N=—";

  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">PROJECT ACTIVITY OVER TIME.</h2>
        <span className="dashboard-section-subtitle">LONGITUDINAL OBSERVATION TIMELINE</span>
      </div>

      <div className="dashboard-grid-1-2">
        {/* Left: Longitudinal Observation Chart Area */}
        <div className="dashboard-card-white">
          <div
            style={{
              height: "300px",
              width: "100%",
              position: "relative",
              display: "flex",
              flexDirection: "column",
              justifyContent: "flex-end",
              paddingBottom: "32px",
              borderBottom: "1px solid var(--color-border-hairline)",
            }}
          >
            {/* Architectural Timeline Track */}
            <div style={{ position: "relative", width: "100%", height: "140px" }}>
              <svg
                style={{ width: "100%", height: "100%" }}
                preserveAspectRatio="none"
                viewBox="0 0 100 100"
              >
                <path
                  d="M0,80 L10,75 L20,78 L30,65 L40,60 L50,55 L60,58 L70,45 L80,40 L90,35 L100,30"
                  fill="none"
                  stroke="var(--color-primary-950)"
                  strokeWidth="1.5"
                />
              </svg>
            </div>

            {/* X-Axis Ticks (Real covered months bounds) */}
            <div
              style={{
                position: "absolute",
                bottom: "4px",
                left: 0,
                right: 0,
                display: "flex",
                justifyContent: "space-between",
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                color: "var(--color-text-dim)",
              }}
            >
              {displayMilestones.map((m) => (
                <span key={m}>{m}</span>
              ))}
            </div>
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              paddingTop: "12px",
            }}
          >
            <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span
                  style={{
                    width: "10px",
                    height: "10px",
                    backgroundColor: "var(--color-primary-950)",
                    display: "inline-block",
                  }}
                />
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--color-text-variant)",
                    textTransform: "uppercase",
                  }}
                >
                  ACTIVE PROJECTS
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span
                  style={{
                    width: "10px",
                    height: "10px",
                    border: "1px solid var(--color-primary-950)",
                    display: "inline-block",
                  }}
                />
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--color-text-variant)",
                    textTransform: "uppercase",
                  }}
                >
                  OBSERVATIONS
                </span>
              </div>
            </div>

            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                color: "var(--color-text-dim)",
              }}
            >
              {uniqueProjectsCount}
            </span>
          </div>
        </div>

        {/* Right: Portfolio State */}
        <div className="dashboard-card-paper">
          <div className="card-header-lockup">
            <span className="card-label">PORTFOLIO STATE</span>
            <span className="card-tag-pending">DEMO CLASSIFICATION — BACKEND PENDING</span>
          </div>

          <div className="progress-distribution-list" style={{ marginTop: "12px" }}>
            <div className="progress-distribution-item">
              <div className="progress-item-header">
                <span>ON TRACK</span>
                <span>82%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill-primary" style={{ width: "82%" }} />
              </div>
            </div>

            <div className="progress-distribution-item">
              <div className="progress-item-header">
                <span>AT RISK</span>
                <span>12%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill-coral" style={{ width: "12%" }} />
              </div>
            </div>

            <div className="progress-distribution-item">
              <div className="progress-item-header">
                <span>CRITICAL</span>
                <span>6%</span>
              </div>
              <div className="progress-track">
                <div className="progress-fill-coral" style={{ width: "6%" }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
