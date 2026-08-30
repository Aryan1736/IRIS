import React from "react";
import type { ModelInfoResponse } from "@/types/risk.ts";

interface IntelligenceIntroProps {
  modelInfo?: ModelInfoResponse;
  reportMonth: string;
}

export const IntelligenceIntro: React.FC<IntelligenceIntroProps> = ({
  modelInfo,
  reportMonth,
}) => {
  const isReady = modelInfo?.status === "READY";
  const horizon = modelInfo?.horizon_months ? `H=${modelInfo.horizon_months} MONTHS` : "H=3 MONTHS";

  return (
    <section className="intelligence-intro-header">
      <div className="intelligence-breadcrumb">
        IRIS / INTELLIGENCE / EARLY WARNING
      </div>

      <div className="intelligence-intro-grid">
        <div className="intelligence-title-lockup">
          <h1 className="intelligence-main-title">
            See the Risk Before It Becomes the Outcome.
          </h1>
          <p className="intelligence-subtitle">
            Early-warning intelligence for schedule extension risk, longitudinal delay probability, and TreeSHAP explainability drivers across the monitored portfolio.
          </p>
        </div>

        <div className="intelligence-telemetry-box">
          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">MODEL STATUS</span>
            <span className="intelligence-telemetry-val">
              {isReady ? "SERVING READY" : "STATUS PENDING"}
            </span>
          </div>

          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">HORIZON</span>
            <span className="intelligence-telemetry-val">{horizon}</span>
          </div>

          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">EVALUATION</span>
            <span className="intelligence-telemetry-val">WALK-FORWARD</span>
          </div>

          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">REGIME</span>
            <span className="intelligence-telemetry-val">LEGACY / MODERN</span>
          </div>

          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">ACTIVE EVALUATION</span>
            <span className="intelligence-telemetry-val" style={{ color: "#1A3C2B" }}>
              {reportMonth}
            </span>
          </div>

          <div className="intelligence-telemetry-row">
            <span className="intelligence-telemetry-label">MODEL OUTPUT</span>
            <span className="intelligence-telemetry-val" style={{ color: isReady ? "#1A3C2B" : "#BA1A1A" }}>
              {isReady ? "● LIVE SERVING ACTIVE" : "○ NOT CONNECTED"}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
