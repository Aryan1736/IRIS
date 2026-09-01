import React from "react";
import type { SummaryResponse } from "@/types/risk.ts";

interface RegimeIntelligenceProps {
  summary?: SummaryResponse;
}

export const RegimeIntelligence: React.FC<RegimeIntelligenceProps> = ({ summary }) => {
  const regimes = summary?.regimes || [];

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <div className="intelligence-section-title-lockup">
          <h2 className="intelligence-section-title">05. Risk by Regime</h2>
          <span className="intelligence-section-subtitle">
            LONGITUDINAL REGIME SPECIFICATION & DUAL-MODEL ARCHITECTURE
          </span>
        </div>
        <span className="intelligence-section-subtitle">
          SYSTEM ARCHITECTURE
        </span>
      </div>

      <div className="intelligence-regime-grid">
        {regimes.length === 0 ? (
          <div className="intelligence-regime-card">
            <div style={{ padding: "20px", textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-muted)" }}>
              NO REGIME METADATA RETURNED FOR CURRENT SCOPE.
            </div>
          </div>
        ) : (
          regimes.map((reg) => (
            <div key={reg.regime} className="intelligence-regime-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span className="intelligence-badge-regime">{reg.regime} REGIME</span>
                  <h3 className="intelligence-overview-card-title" style={{ fontSize: "16px" }}>
                    {reg.regime === "MODERN" ? "Modern Six-Digit Architecture" : "Legacy Multi-Format Architecture"}
                  </h3>
                </div>
                <span className="intelligence-section-subtitle">
                  {reg.project_count.toLocaleString()} EVALUATED PROJECTS
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                  <span className="intelligence-gov-label">SERVING MODEL ID:</span>
                  <span style={{ fontWeight: 600, color: "var(--color-primary-950)" }}>{reg.model_id}</span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                  <span className="intelligence-gov-label">CALIBRATION METHOD:</span>
                  <span style={{ fontWeight: 600, color: reg.calibration_active ? "#022617" : "var(--color-text-muted)" }}>
                    {reg.calibration_active ? "TEMPORAL PLATT SCALING (ACTIVE)" : "UNCALIBRATED RAW LOGITS"}
                  </span>
                </div>

                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                  <span className="intelligence-gov-label">EVALUATED POPULATION:</span>
                  <span style={{ fontWeight: 600, color: "var(--color-primary-950)" }}>
                    {reg.project_count.toLocaleString()} PROJECTS
                  </span>
                </div>

                <div style={{ fontSize: "11px", fontFamily: "var(--font-sans)", color: "var(--color-text-secondary)", lineHeight: 1.4, borderTop: "1px solid var(--color-border-hairline)", paddingTop: "8px" }}>
                  {reg.regime === "MODERN"
                    ? "Modern regime evaluates 6-digit canonical infrastructure codes (July 2025 – July 2026) using regularized linear and gradient-boosted predictors."
                    : "Legacy regime evaluates historical multi-format identifier codes (October 2023 – June 2025) with structural triplet parsing and specialized calibration."}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
};
