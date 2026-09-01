import React from "react";
import { IrisSignedDriversChart } from "@/components/common/charts/IrisSignedDriversChart.tsx";

export const RiskDriverIntelligence: React.FC = () => {
  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <div className="intelligence-section-title-lockup">
          <h2 className="intelligence-section-title">06. Risk Driver Intelligence</h2>
          <span className="intelligence-section-subtitle">
            SIGNED FEATURE CONTRIBUTIONS & MODEL EXPLAINABILITY ARCHITECTURE
          </span>
        </div>
        <span className="intelligence-section-subtitle">
          EXPLAINABILITY: TREESHAP / LOGISTIC MARGINS
        </span>
      </div>

      <div className="intelligence-driver-card" style={{ background: "#FFFFFF", border: "1px solid var(--color-border-hairline)", padding: "16px 20px" }}>
        {/* Diverging Center-Line Recharts Visualization */}
        <div className="intelligence-driver-diagram" style={{ marginBottom: "16px" }}>
          <div className="intelligence-driver-axis-header" style={{ marginBottom: "8px" }}>
            <span style={{ color: "#1A3C2B", fontWeight: 700 }}>
              ◀ RISK-REDUCING DRIVERS (- RAW MARGIN LOGIT)
            </span>
            <span style={{ textAlign: "center", color: "var(--color-primary-950)", fontSize: "12px", fontWeight: 700 }}>
              0.0
            </span>
            <span style={{ textAlign: "right", color: "#BA1A1A", fontWeight: 700 }}>
              RISK-INCREASING DRIVERS (+ RAW MARGIN LOGIT) ▶
            </span>
          </div>

          <IrisSignedDriversChart
            isIllustrative={true}
            height={220}
          />

          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-muted)", marginTop: "8px", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "6px" }}>
            <span>- LOGIT SHIFT (LOWERS EXTENSION PROBABILITY)</span>
            <span>BASELINE MODEL INTERCEPT (0.0)</span>
            <span>+ LOGIT SHIFT (ELEVATES EXTENSION PROBABILITY)</span>
          </div>
        </div>

        {/* Explanatory Guide Box */}
        <div className="intelligence-driver-guide-grid">
          <div className="intelligence-driver-guide-box">
            <span className="intelligence-section-subtitle" style={{ color: "#BA1A1A", fontWeight: 700 }}>
              POSITIVE MARGIN LOGIT CONTRIBUTIONS (+Δ)
            </span>
            <p style={{ margin: 0, fontFamily: "var(--font-sans)", fontSize: "13px", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Positive values push the model's uncalibrated linear/tree margin score higher, indicating attributes that elevated schedule extension probability (e.g. tight months to effective schedule, high schedule lag, or severe cost escalation).
            </p>
          </div>

          <div className="intelligence-driver-guide-box">
            <span className="intelligence-section-subtitle" style={{ color: "#1A3C2B", fontWeight: 700 }}>
              NEGATIVE MARGIN LOGIT CONTRIBUTIONS (-Δ)
            </span>
            <p style={{ margin: 0, fontFamily: "var(--font-sans)", fontSize: "13px", color: "var(--color-text-secondary)", lineHeight: 1.5 }}>
              Negative values subtract from the model's margin score, indicating protective attributes that suppressed extension probability (e.g. robust physical progress pacing, historical schedule stability, or favorable sector benchmarks).
            </p>
          </div>
        </div>

        <div style={{ paddingTop: "12px", borderTop: "1px solid var(--color-border-hairline)", marginTop: "12px" }}>
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            EXPLAINABILITY GOVERNANCE NOTE: VALUES REPRESENT SIGNED MARGIN CONTRIBUTIONS TO MODEL LOGIT SPACE, NOT PROBABILITIES OR VERIFIED CAUSAL MECHANISMS. PER-PROJECT DRIVERS ARE ACCESSIBLE VIA THE PROJECT INSPECTION CONSOLE.
          </span>
        </div>
      </div>
    </section>
  );
};
