import React from "react";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

export const PredictiveSection: React.FC = () => {
  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 45,
  });

  return (
    <section
      id="predictive"
      ref={sectionRef}
      className="landing-section landing-section-light hairline-b"
    >
      <div className="container-main">
        {/* Section Heading */}
        <div style={{ marginBottom: "48px" }} className="landing-reveal-item">
          <div className="landing-section-badge">
            <span className="landing-section-badge-dot" />
            <span>[ 04 / PREDICTIVE INTELLIGENCE ]</span>
          </div>

          <h2 className="landing-section-heading">
            SEE THE RISK BEFORE IT
            <br />
            BECOMES THE OUTCOME.
          </h2>

          <p className="landing-section-desc">
            Machine learning early-warning indicators trained strictly on verified longitudinal flash
            report data, detecting cost slippage and milestone delays before they become systemic.
          </p>
        </div>

        {/* 4 Architectural Cards with Grid Hairlines */}
        <div
          className="landing-grid-container"
          style={{
            gridTemplateColumns: "repeat(4, 1fr)",
          }}
        >
          {/* PI-01: Cost Overrun Prediction */}
          <div className="landing-card landing-reveal-item" style={{ minHeight: "280px" }}>
            <div className="landing-card-header">
              <span>[ PI-01 ]</span>
              <span style={{ fontSize: "9px", fontWeight: 700, color: "var(--color-primary-800)" }}>COST</span>
            </div>

            <h3 className="landing-card-title">
              COST OVERRUN
              <br />
              PREDICTION
            </h3>

            <p className="landing-card-body" style={{ marginBottom: "20px" }}>
              Quantifies probabilistic escalation range beyond approved revised estimates.
            </p>

            <div
              className="hairline-all"
              style={{
                height: "85px",
                marginTop: "auto",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                backgroundColor: "#faf9f6",
                padding: "16px",
                gap: "6px",
              }}
            >
              <div style={{ width: "100%", height: "8px", backgroundColor: "#D9E8DF", borderRadius: "var(--radius-none)" }} />
              <div style={{ width: "78%", height: "8px", backgroundColor: "#A4CBB8", borderRadius: "var(--radius-none)" }} />
              <div style={{ width: "42%", height: "8px", backgroundColor: "#FF8A65", borderRadius: "var(--radius-none)" }} />
            </div>
          </div>

          {/* PI-02: Schedule Delay Prediction */}
          <div className="landing-card landing-reveal-item" style={{ minHeight: "280px" }}>
            <div className="landing-card-header">
              <span>[ PI-02 ]</span>
              <span style={{ fontSize: "9px", fontWeight: 700, color: "var(--color-primary-800)" }}>SCHEDULE</span>
            </div>

            <h3 className="landing-card-title">
              SCHEDULE DELAY
              <br />
              PREDICTION
            </h3>

            <p className="landing-card-body" style={{ marginBottom: "20px" }}>
              Forecasts milestone slippage using historical sector completion velocities.
            </p>

            <div
              className="hairline-all"
              style={{
                height: "85px",
                marginTop: "auto",
                display: "flex",
                alignItems: "flex-end",
                justifyContent: "space-between",
                backgroundColor: "#faf9f6",
                padding: "14px 18px",
                gap: "8px",
              }}
            >
              <div style={{ flex: 1, height: "40%", backgroundColor: "#D9E8DF" }} />
              <div style={{ flex: 1, height: "85%", backgroundColor: "#A4CBB8" }} />
              <div style={{ flex: 1, height: "60%", backgroundColor: "#FF8A65" }} />
              <div style={{ flex: 1, height: "30%", backgroundColor: "#D9E8DF" }} />
            </div>
          </div>

          {/* PI-03: Project Risk Scoring */}
          <div className="landing-card landing-reveal-item" style={{ minHeight: "280px" }}>
            <div className="landing-card-header">
              <span>[ PI-03 ]</span>
              <span style={{ fontSize: "9px", fontWeight: 700, color: "var(--color-primary-800)" }}>RISK</span>
            </div>

            <h3 className="landing-card-title">
              PROJECT RISK
              <br />
              SCORING
            </h3>

            <p className="landing-card-body" style={{ marginBottom: "20px" }}>
              Composite risk indices calibrated across expenditure pacing and timeline lag.
            </p>

            <div
              className="hairline-all"
              style={{
                height: "85px",
                marginTop: "auto",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#faf9f6",
              }}
            >
              <div
                style={{
                  width: "52px",
                  height: "52px",
                  borderRadius: "50%",
                  border: "3px solid #FF8A65",
                  borderTopColor: "var(--color-primary-600)",
                  borderRightColor: "var(--color-primary-600)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "var(--font-mono)",
                  fontSize: "12px",
                  fontWeight: 700,
                  color: "var(--color-primary-900)",
                }}
              >
                0.84
              </div>
            </div>
          </div>

          {/* PI-04: Early Warning Signals */}
          <div className="landing-card landing-reveal-item" style={{ minHeight: "280px" }}>
            <div className="landing-card-header">
              <span>[ PI-04 ]</span>
              <span style={{ fontSize: "9px", fontWeight: 700, color: "var(--color-primary-800)" }}>SIGNAL</span>
            </div>

            <h3 className="landing-card-title">
              EARLY WARNING
              <br />
              SIGNALS
            </h3>

            <p className="landing-card-body" style={{ marginBottom: "20px" }}>
              Zero-expenditure progress, revised cost drops, and reporting anomalies.
            </p>

            <div
              className="hairline-all"
              style={{
                height: "85px",
                marginTop: "auto",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#faf9f6",
                padding: "16px",
                gap: "5px",
              }}
            >
              <div style={{ width: "100%", height: "5px", backgroundColor: "#FFE0D6" }} />
              <div style={{ width: "100%", height: "5px", backgroundColor: "#FFCCBC" }} />
              <div style={{ width: "100%", height: "5px", backgroundColor: "#FFA88E" }} />
              <div style={{ width: "100%", height: "5px", backgroundColor: "#FF8A65" }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
