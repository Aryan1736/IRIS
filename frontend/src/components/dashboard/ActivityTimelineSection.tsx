import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { DatasetInfoResponse } from "@/types/system.ts";
import { fetchMonthlyObservations } from "@/api/projects.ts";
import { fetchRiskSummary } from "@/api/risk.ts";
import { MonthlyActivityChart } from "./MonthlyActivityChart.tsx";

interface ActivityTimelineSectionProps {
  systemInfo?: DatasetInfoResponse;
}

export const ActivityTimelineSection: React.FC<ActivityTimelineSectionProps> = ({
  systemInfo,
}) => {
  const months = systemInfo?.covered_months || [];

  // Query actual monthly observations time series
  const { data: monthlyData, isLoading: isMonthlyLoading } = useQuery({
    queryKey: ["monthlyObservationCounts", months],
    queryFn: () => fetchMonthlyObservations(months),
    enabled: months.length > 0,
    staleTime: 10 * 60 * 1000,
  });

  // Query latest risk summary for real portfolio risk distribution
  const latestMonth = months.length > 0 ? months[months.length - 1] : "2026-04";
  const { data: riskSummary, isLoading: isRiskLoading } = useQuery({
    queryKey: ["portfolioRiskSummary", latestMonth],
    queryFn: () => fetchRiskSummary({ report_month: latestMonth }),
    staleTime: 10 * 60 * 1000,
  });

  const uniqueProjectsCount = systemInfo?.unique_projects_count
    ? `N=${systemInfo.unique_projects_count.toLocaleString()}`
    : "N=—";

  const scoreDist = riskSummary?.score_distribution;
  const p25 = scoreDist?.p25 != null ? (scoreDist.p25 * 100).toFixed(1) : null;
  const median = scoreDist?.median != null ? (scoreDist.median * 100).toFixed(1) : null;
  const p75 = scoreDist?.p75 != null ? (scoreDist.p75 * 100).toFixed(1) : null;
  const p95 = scoreDist?.p95 != null ? (scoreDist.p95 * 100).toFixed(1) : null;

  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">PROJECT ACTIVITY OVER TIME.</h2>
        <span className="dashboard-section-subtitle">LONGITUDINAL OBSERVATION TIMELINE</span>
      </div>

      <div className="dashboard-grid-1-2">
        {/* Left: Real Longitudinal Observation Chart Area */}
        <div className="dashboard-card-white">
          <MonthlyActivityChart data={monthlyData || []} isLoading={isMonthlyLoading} />

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              paddingTop: "16px",
              borderTop: "1px solid var(--color-border-hairline)",
              marginTop: "8px",
            }}
          >
            <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span
                  style={{
                    width: "10px",
                    height: "10px",
                    backgroundColor: "#1A3C2B",
                    display: "inline-block",
                  }}
                />
                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--color-text-variant)",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  OBSERVATIONS BY MONTH
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
              {uniqueProjectsCount} UNIQUE PROJECTS
            </span>
          </div>
        </div>

        {/* Right: Real H=3 Schedule Extension Risk Distribution */}
        <div className="dashboard-card-paper">
          <div className="card-header-lockup">
            <span className="card-label">H=3 SCHEDULE EXTENSION RISK</span>
            <span className="card-tag-pending">
              {riskSummary?.project_count
                ? `EVALUATED: N=${riskSummary.project_count.toLocaleString()}`
                : "SERVING LAYER READY"}
            </span>
          </div>

          {isRiskLoading ? (
            <div
              style={{
                padding: "32px 0",
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                color: "var(--color-text-dim)",
                textTransform: "uppercase",
                textAlign: "center",
              }}
            >
              LOADING RISK DISTRIBUTION...
            </div>
          ) : scoreDist ? (
            <div className="progress-distribution-list" style={{ marginTop: "12px", gap: "12px" }}>
              {/* P25 Lower Quartile */}
              <div className="progress-distribution-item">
                <div className="progress-item-header">
                  <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)" }}>P25 (LOWER QUARTILE)</span>
                  <span style={{ fontWeight: 600 }}>{p25}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill-primary" style={{ width: `${p25}%`, opacity: 0.5 }} />
                </div>
              </div>

              {/* Median */}
              <div className="progress-distribution-item">
                <div className="progress-item-header">
                  <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)" }}>MEDIAN RISK (P50)</span>
                  <span style={{ fontWeight: 600 }}>{median}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill-primary" style={{ width: `${median}%`, opacity: 0.8 }} />
                </div>
              </div>

              {/* P75 Upper Quartile */}
              <div className="progress-distribution-item">
                <div className="progress-item-header">
                  <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)" }}>P75 (UPPER QUARTILE)</span>
                  <span style={{ fontWeight: 600, color: "var(--color-coral)" }}>{p75}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill-coral" style={{ width: `${p75}%`, opacity: 0.7 }} />
                </div>
              </div>

              {/* P95 Tail Risk */}
              <div className="progress-distribution-item">
                <div className="progress-item-header">
                  <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)" }}>P95 (TAIL RISK)</span>
                  <span style={{ fontWeight: 700, color: "var(--color-coral)" }}>{p95}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill-coral" style={{ width: `${p95}%` }} />
                </div>
              </div>

              <div style={{ paddingTop: "8px", borderTop: "1px solid var(--color-border-hairline)" }}>
                <p
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    color: "var(--color-text-dim)",
                    margin: 0,
                    lineHeight: 1.4,
                  }}
                >
                  TARGET: EFFECTIVE SCHEDULE EXTENSION (H=3). CALIBRATED PROBABILITY QUANTILE DISTRIBUTION FROM ACTIVE SERVING LAYER.
                </p>
              </div>
            </div>
          ) : (
            <div
              style={{
                padding: "24px 0",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                textAlign: "center",
              }}
            >
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-coral)", fontWeight: 600 }}>
                DATA PENDING
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
                MODEL CLASSIFICATION AGGREGATION NOT AVAILABLE
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
