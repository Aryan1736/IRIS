import React from "react";
import { useNavigate } from "react-router-dom";
import type { ProjectSummaryItem } from "@/types/project.ts";

interface EarlyWarningSectionProps {
  projects?: ProjectSummaryItem[];
  isLoading?: boolean;
}

export const EarlyWarningSection: React.FC<EarlyWarningSectionProps> = ({
  projects = [],
  isLoading = false,
}) => {
  const navigate = useNavigate();
  const displayProjects = projects.slice(0, 5);

  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">SEE THE RISK BEFORE IT BECOMES THE OUTCOME.</h2>
      </div>

      <div className="dashboard-grid-1-3">
        {/* Left: Signals Indicator */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">EARLY WARNING SIGNALS</span>
            <span className="card-tag-pending">MODEL CONNECTIVITY: PENDING</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "8px" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-main)", textTransform: "uppercase" }}>
                SCHEDULE EXTENSION
              </span>
              <div style={{ width: "100%", height: "6px", backgroundColor: "var(--color-coral)" }} />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-main)", textTransform: "uppercase" }}>
                EXPENDITURE NON-IMPROVEMENT
              </span>
              <div style={{ width: "100%", height: "6px", backgroundColor: "rgba(186, 26, 26, 0.6)" }} />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-main)", textTransform: "uppercase" }}>
                REPORTING LATENCY
              </span>
              <div style={{ width: "100%", height: "6px", backgroundColor: "rgba(186, 26, 26, 0.3)" }} />
            </div>
          </div>
        </div>

        {/* Right: Monitored Project Signals Table */}
        <div className="dashboard-card-white" style={{ padding: 0, overflowX: "auto" }}>
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>PROJECT</th>
                <th>CODE</th>
                <th>SECTOR</th>
                <th>SIGNAL</th>
                <th style={{ textAlign: "right" }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", padding: "32px", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                    FETCHING MONITORED PROJECTS...
                  </td>
                </tr>
              ) : displayProjects.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: "center", padding: "32px", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                    NO MONITORED PROJECTS RETURNED FROM BACKEND
                  </td>
                </tr>
              ) : (
                displayProjects.map((p) => (
                  <tr
                    key={p.project_code}
                    onClick={() => navigate(`/projects/${p.project_code}`)}
                    style={{ cursor: "pointer" }}
                  >
                    <td style={{ fontFamily: "var(--font-sans)", fontWeight: 600, color: "var(--color-text-main)" }}>
                      {p.project_name}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", color: "var(--color-text-variant)" }}>
                      {p.project_code}
                    </td>
                    <td style={{ fontFamily: "var(--font-sans)", color: "var(--color-text-main)" }}>
                      {p.sector || "—"}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-coral)", fontWeight: 500 }}>
                      NOT CONNECTED
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", textDecoration: "underline", color: "var(--color-primary-950)" }}>
                        INSPECT
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
