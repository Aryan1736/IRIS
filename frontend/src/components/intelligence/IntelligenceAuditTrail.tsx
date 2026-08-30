import React from "react";
import type { ModelInfoResponse } from "@/types/risk.ts";

interface IntelligenceAuditTrailProps {
  modelInfo?: ModelInfoResponse;
}

export const IntelligenceAuditTrail: React.FC<IntelligenceAuditTrailProps> = ({ modelInfo }) => {
  const isReady = modelInfo?.status === "READY";

  const auditItems = [
    { label: "TARGET DEFINITION", status: "VERIFIED", active: true },
    { label: "LABELS GENERATION", status: "GENERATED", active: true },
    { label: "WALK-FORWARD EVAL", status: "COMPLETE", active: true },
    { label: "LOGISTIC BENCHMARK", status: "TRAINED", active: true },
    { label: "NONLINEAR CHALLENGER", status: "TRAINED", active: true },
    { label: "LIVE SERVING PIPELINE", status: isReady ? "SERVING ACTIVE" : "STATUS PENDING", active: isReady },
  ];

  return (
    <section className="intelligence-audit-banner">
      <div className="intelligence-audit-header">
        <h2 className="intelligence-audit-title">07. Model Status / Audit Trail</h2>
        <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "rgba(255, 255, 255, 0.7)" }}>
          GOVERNED PIPELINE SPECIFICATION
        </span>
      </div>

      <div className="intelligence-audit-grid">
        {auditItems.map((item) => (
          <div key={item.label} className="intelligence-audit-cell">
            <span className="intelligence-audit-label">{item.label}</span>
            <span className="intelligence-audit-status" style={{ color: item.active ? "#9EFFBF" : "#FF8C69" }}>
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
};
