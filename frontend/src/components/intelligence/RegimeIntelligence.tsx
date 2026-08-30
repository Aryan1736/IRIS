import React from "react";
import type { SummaryResponse } from "@/types/risk.ts";

interface RegimeIntelligenceProps {
  summary?: SummaryResponse;
}

export const RegimeIntelligence: React.FC<RegimeIntelligenceProps> = ({ summary }) => {
  const regimes = summary?.regimes || [];
  const sectorSummary = summary?.sector_summary || [];

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <h2 className="intelligence-section-title">04. Regime Intelligence & Sector Risk</h2>
        <span className="intelligence-section-subtitle">
          LONGITUDINAL REGIME SPECIFICATION & SECTOR RISK PROFILES
        </span>
      </div>

      <div className="intelligence-regime-grid">
        {/* Left: Regime Metadata */}
        <div className="intelligence-regime-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "12px" }}>
            <h3 className="intelligence-overview-card-title">Dual-Regime Architecture</h3>
            <span className="intelligence-section-subtitle">ACTIVE REGIMES</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {regimes.map((reg) => (
              <div
                key={reg.regime}
                style={{
                  padding: "16px",
                  background: "#FFFFFF",
                  border: "1px solid var(--color-border-hairline)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "8px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="intelligence-badge-regime">{reg.regime} REGIME</span>
                  <span style={{ fontWeight: 600, color: "#1A3C2B" }}>
                    {reg.project_count.toLocaleString()} PROJECTS
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                  <span>MODEL ID:</span>
                  <span style={{ fontWeight: 600 }}>{reg.model_id}</span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                  <span>CALIBRATION:</span>
                  <span style={{ fontWeight: 600, color: reg.calibration_active ? "#022617" : "var(--color-text-muted)" }}>
                    {reg.calibration_active ? "TEMPORAL PLATT SCALING (ACTIVE)" : "UNCALIBRATED"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Sector Risk Summary */}
        <div className="intelligence-regime-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "12px" }}>
            <h3 className="intelligence-overview-card-title">Sector Risk Summary</h3>
            <span className="intelligence-section-subtitle">
              {sectorSummary.length} MONITORED SECTORS
            </span>
          </div>

          <div style={{ maxHeight: "320px", overflowY: "auto", border: "1px solid var(--color-border-hairline)" }}>
            <table className="intelligence-table" aria-label="Sector Risk Summary Table">
              <thead>
                <tr>
                  <th>SECTOR</th>
                  <th>PROJECTS</th>
                  <th>MEAN RISK</th>
                  <th>MAX RISK</th>
                </tr>
              </thead>
              <tbody>
                {sectorSummary.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: "center", padding: "20px" }}>
                      —
                    </td>
                  </tr>
                ) : (
                  sectorSummary.map((sec) => (
                    <tr key={sec.sector || "UNKNOWN"}>
                      <td style={{ fontWeight: 600, maxWidth: "200px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {sec.sector || "—"}
                      </td>
                      <td>{sec.project_count.toLocaleString()}</td>
                      <td style={{ color: "#BA1A1A", fontWeight: 600 }}>
                        {(sec.mean_risk_probability * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        {(sec.highest_risk_probability * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};
