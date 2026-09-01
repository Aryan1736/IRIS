import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchRiskSummary, fetchModelInfo } from "@/api/risk.ts";
import { IrisTopRiskRankingChart } from "@/components/common/charts/IrisTopRiskRankingChart.tsx";

export const EarlyWarningSection: React.FC = () => {
  const navigate = useNavigate();

  const { data: modelInfo } = useQuery({
    queryKey: ["modelInfo"],
    queryFn: fetchModelInfo,
    staleTime: 10 * 60 * 1000,
  });

  const { data: riskSummary, isLoading } = useQuery({
    queryKey: ["earlyWarningRiskSummary"],
    queryFn: () => fetchRiskSummary({ report_month: "2026-04", top_n: 5 }),
    staleTime: 10 * 60 * 1000,
  });

  const topProjects = riskSummary?.top_risk_projects?.slice(0, 5) || [];
  const meanRisk = riskSummary?.score_distribution?.mean != null
    ? `${(riskSummary.score_distribution.mean * 100).toFixed(1)}%`
    : "—";

  const isModelReady = modelInfo?.status === "READY";

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
        <h2 className="dashboard-section-title">SEE THE RISK BEFORE IT BECOMES THE OUTCOME.</h2>
        <Link
          to="/intelligence"
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
          VIEW FULL RISK INTELLIGENCE →
        </Link>
      </div>

      <div className="dashboard-grid-1-3">
        {/* Left: Signals Indicator & Model Architecture */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">EARLY WARNING SIGNALS</span>
            <span
              className={isModelReady ? "card-tag-active" : "card-tag-pending"}
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                padding: "2px 6px",
                backgroundColor: isModelReady ? "var(--color-primary-950)" : "var(--color-risk-high-bg)",
                color: isModelReady ? "#FFFFFF" : "var(--color-coral)",
                fontWeight: 600,
              }}
            >
              {isModelReady ? "MODEL: LIVE SERVING READY" : "MODEL CONNECTIVITY: PENDING"}
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginTop: "12px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
                PRIMARY TARGET
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 600, color: "var(--color-text-main)" }}>
                SCHEDULE EXTENSION (H=3)
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
                SERVING POPULATION
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 600, color: "var(--color-text-main)" }}>
                {riskSummary?.project_count ? `${riskSummary.project_count.toLocaleString()} EVALUATED PROJECTS` : "—"}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
                MEAN CALIBRATED RISK
              </span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 700, color: "var(--color-coral)" }}>
                {meanRisk}
              </span>
            </div>

            <div style={{ paddingTop: "8px", borderTop: "1px solid var(--color-border-hairline)" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
                ACTIVE HORIZON: 3 MONTHS
              </span>
            </div>
          </div>
        </div>

        {/* Right: Visual Ranking + Monitored Project Signals Table */}
        <div className="dashboard-card-white" style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Recharts Top Risk Horizontal Mini Ranking */}
          {topProjects.length > 0 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "12px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="card-label" style={{ color: "var(--color-primary-950)", fontWeight: 700 }}>
                  TOP ELEVATED RISK CONCENTRATIONS
                </span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
                  CALIBRATED PROBABILITY %
                </span>
              </div>
              <IrisTopRiskRankingChart
                projects={topProjects}
                onSelectProject={(p) => navigate(`/projects/${encodeURIComponent(p.project_code)}`)}
                height={160}
              />
            </div>
          )}

          <div style={{ overflowX: "auto" }}>
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>PROJECT</th>
                  <th>CODE</th>
                  <th>SECTOR</th>
                  <th>CALIBRATED RISK</th>
                  <th style={{ textAlign: "right" }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center", padding: "32px", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                      FETCHING MONITORED RISK PROJECTS...
                    </td>
                  </tr>
                ) : topProjects.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: "center", padding: "32px", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                      NO MONITORED PROJECTS RETURNED FROM SERVING LAYER
                    </td>
                  </tr>
                ) : (
                  topProjects.map((p) => {
                    const encodedCode = encodeURIComponent(p.project_code);
                    const riskFormatted = `${(p.risk_probability * 100).toFixed(1)}%`;
                    return (
                      <tr
                        key={p.project_code}
                        onClick={() => navigate(`/projects/${encodedCode}`)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            navigate(`/projects/${encodedCode}`);
                          }
                        }}
                        tabIndex={0}
                        role="button"
                        aria-label={`Inspect ${p.project_name || p.project_code}`}
                        style={{ cursor: "pointer" }}
                      >
                        <td style={{ fontFamily: "var(--font-sans)", fontWeight: 600, color: "var(--color-text-main)" }}>
                          {p.project_name || "—"}
                        </td>
                        <td style={{ fontFamily: "var(--font-mono)", color: "var(--color-text-variant)" }}>
                          {p.project_code}
                        </td>
                        <td style={{ fontFamily: "var(--font-sans)", color: "var(--color-text-main)" }}>
                          {p.sector || "—"}
                        </td>
                        <td style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--color-coral)", fontWeight: 700 }}>
                          {riskFormatted}
                        </td>
                        <td style={{ textAlign: "right" }}>
                          <Link
                            to={`/projects/${encodedCode}`}
                            onClick={(e) => e.stopPropagation()}
                            style={{
                              fontFamily: "var(--font-mono)",
                              fontSize: "11px",
                              textDecoration: "underline",
                              color: "var(--color-primary-950)",
                              fontWeight: 600,
                            }}
                          >
                            INSPECT
                          </Link>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};
