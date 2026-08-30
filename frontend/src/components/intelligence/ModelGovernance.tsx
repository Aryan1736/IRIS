import React from "react";
import type { ModelInfoResponse } from "@/types/risk.ts";

interface ModelGovernanceProps {
  modelInfo?: ModelInfoResponse;
}

export const ModelGovernance: React.FC<ModelGovernanceProps> = ({ modelInfo }) => {
  const models = modelInfo?.models || [];

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <h2 className="intelligence-section-title">05. Model Governance</h2>
        <span className="intelligence-section-subtitle">
          AUDITABLE SERVING CONTRACT & VALIDATION POLICIES
        </span>
      </div>

      <div className="intelligence-gov-card">
        <div className="intelligence-gov-row">
          <span className="intelligence-gov-label">TARGET DEFINITION</span>
          <span className="intelligence-gov-val">H=3 SCHEDULE EXTENSION (target_effective_schedule_ext_3m)</span>
        </div>

        <div className="intelligence-gov-row">
          <span className="intelligence-gov-label">VALIDATION METHODOLOGY</span>
          <span className="intelligence-gov-val">WALK-FORWARD TEMPORAL SPLIT</span>
        </div>

        <div className="intelligence-gov-row">
          <span className="intelligence-gov-label">EMBARGO / PURGING POLICY</span>
          <span className="intelligence-gov-val">T + 3 &lt; EVALUATION WINDOW</span>
        </div>

        <div className="intelligence-gov-row">
          <span className="intelligence-gov-label">SERVING ARTIFACT VERSION</span>
          <span className="intelligence-gov-val">{modelInfo?.serving_artifact_version || "—"}</span>
        </div>

        <div className="intelligence-gov-row">
          <span className="intelligence-gov-label">SERVING STATUS</span>
          <span className="intelligence-gov-val" style={{ color: "#1A3C2B" }}>
            {modelInfo?.status === "READY" ? "READY (LIVE SERVING ACTIVE)" : modelInfo?.status || "—"}
          </span>
        </div>

        {/* Models details list */}
        <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "12px" }}>
          {models.map((mod) => (
            <div
              key={mod.regime}
              style={{
                padding: "12px",
                background: "#FFFFFF",
                border: "1px solid var(--color-border-hairline)",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                fontSize: "11px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700 }}>
                <span>{mod.regime} MODEL: {mod.model_id}</span>
                <span className="intelligence-badge-regime">{mod.family}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", color: "var(--color-text-secondary)" }}>
                <span>EXPLANATION: {mod.explanation_method}</span>
                <span>FEATURES: {mod.features_count}</span>
              </div>
              <div style={{ color: "var(--color-text-muted)", fontSize: "10px" }}>
                CALIBRATION POLICY: {mod.calibration_policy}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
