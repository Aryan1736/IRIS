import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import type { RiskRecord } from "@/types/risk.ts";
import { fetchProjectRiskHistory } from "@/api/risk.ts";

interface RiskDetailDrawerProps {
  record: RiskRecord | null;
  onClose: () => void;
}

export const RiskDetailDrawer: React.FC<RiskDetailDrawerProps> = ({ record, onClose }) => {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const projectCode = record?.project_code || "";

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ["projectRiskHistory", projectCode],
    queryFn: () => fetchProjectRiskHistory(projectCode),
    enabled: !!projectCode,
  });

  if (!record) return null;

  const historyItems = historyData?.items || [];
  const posContribs = record.top_positive_contributors || [];
  const negContribs = record.top_negative_contributors || [];

  // Calculate max contribution for scale
  const maxContrib = Math.max(
    1,
    ...posContribs.map((c) => Math.abs(c.contribution)),
    ...negContribs.map((c) => Math.abs(c.contribution))
  );

  return (
    <div className="intelligence-modal-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-label="Risk Inspection Drawer">
      <div className="intelligence-drawer" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="intelligence-drawer-header">
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span className="intelligence-section-subtitle">PROJECT RISK INSPECTION</span>
            <h2 className="intelligence-main-title" style={{ fontSize: "24px" }}>
              {record.project_code}
            </h2>
            <span style={{ fontSize: "14px", color: "var(--color-text-secondary)" }}>
              {record.project_name || "—"}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Link
              to={`/projects/${encodeURIComponent(record.project_code)}`}
              className="intelligence-btn-inspect"
              style={{ textDecoration: "none" }}
            >
              VIEW FULL PROJECT →
            </Link>
            <button
              type="button"
              className="intelligence-drawer-close"
              onClick={onClose}
              aria-label="Close drawer"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "12px",
            fontFamily: "var(--font-mono)",
            background: "#FFFFFF",
            border: "1px solid var(--color-border-hairline)",
            padding: "16px",
          }}
        >
          <div>
            <span className="intelligence-gov-label">CALIBRATED RISK</span>
            <div style={{ fontSize: "20px", fontWeight: 700, color: "#BA1A1A" }}>
              {(record.risk_probability * 100).toFixed(1)}%
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              RAW: {(record.raw_probability * 100).toFixed(1)}%
            </span>
          </div>

          <div>
            <span className="intelligence-gov-label">PORTFOLIO RANK</span>
            <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--color-primary-950)" }}>
              #{record.risk_rank}
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              OF {record.population_size} PROJECTS
            </span>
          </div>

          <div>
            <span className="intelligence-gov-label">PERCENTILE</span>
            <div style={{ fontSize: "20px", fontWeight: 700, color: "var(--color-primary-950)" }}>
              TOP {Math.max(0.1, (100 - record.risk_percentile * 100)).toFixed(1)}%
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              P{(record.risk_percentile * 100).toFixed(0)}
            </span>
          </div>
        </div>

        {/* Technical Governance Metadata */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", alignItems: "center" }}>
          <span className="intelligence-badge-regime">{record.regime} REGIME</span>
          {record.calibration_active ? (
            <span className="intelligence-badge-calibrated">CALIBRATION ACTIVE</span>
          ) : (
            <span className="intelligence-badge-uncalibrated">RAW PROBABILITY</span>
          )}
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
            MODEL: {record.model_id}
          </span>
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
            SPACE: {record.version_metadata?.contribution_space || "RAW_MARGIN_LOGIT"}
          </span>
        </div>

        {/* Explainability Section */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "8px" }}>
            <h3 className="intelligence-overview-card-title" style={{ fontSize: "16px" }}>
              Signed Feature Drivers (Model Contributions)
            </h3>
            <span className="intelligence-section-subtitle">
              METHOD: {record.version_metadata?.explanation_method || "TREESHAP"} (RAW MARGIN LOGITS)
            </span>
            <div style={{ fontSize: "10px", color: "var(--color-text-muted)", marginTop: "4px", lineHeight: 1.4 }}>
              Values represent signed margin contributions to model logit space, not probabilities or verified causal mechanisms.
            </div>
          </div>

          {/* Positive Contributors (Risk Increasing) */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)", fontWeight: 700, color: "#BA1A1A" }}>
              ▲ MODEL RISK-INCREASING DRIVERS (+ RAW MARGIN LOGIT)
            </span>
            {posContribs.length === 0 ? (
              <div style={{ fontSize: "11px", color: "var(--color-text-muted)" }}>None reported</div>
            ) : (
              posContribs.map((c) => {
                const widthPercent = (Math.abs(c.contribution) / maxContrib) * 100;
                return (
                  <div key={c.feature} className="intelligence-contrib-bar-row">
                    <span className="intelligence-contrib-name" title={`${c.display_name} (${c.feature})`}>
                      {c.display_name || c.feature}
                    </span>
                    <div className="intelligence-contrib-track">
                      <div
                        className="intelligence-contrib-fill-pos"
                        style={{ width: `${Math.min(100, Math.max(4, widthPercent))}%` }}
                      />
                    </div>
                    <span className="intelligence-contrib-val" style={{ color: "#BA1A1A" }}>
                      +{c.contribution.toFixed(2)}
                    </span>
                  </div>
                );
              })
            )}
          </div>

          {/* Negative Contributors (Risk Reducing) */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "8px" }}>
            <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)", fontWeight: 700, color: "#1A3C2B" }}>
              ▼ MODEL RISK-REDUCING DRIVERS (- RAW MARGIN LOGIT)
            </span>
            {negContribs.length === 0 ? (
              <div style={{ fontSize: "11px", color: "var(--color-text-muted)" }}>None reported</div>
            ) : (
              negContribs.map((c) => {
                const widthPercent = (Math.abs(c.contribution) / maxContrib) * 100;
                return (
                  <div key={c.feature} className="intelligence-contrib-bar-row">
                    <span className="intelligence-contrib-name" title={`${c.display_name} (${c.feature})`}>
                      {c.display_name || c.feature}
                    </span>
                    <div className="intelligence-contrib-track">
                      <div
                        className="intelligence-contrib-fill-neg"
                        style={{ width: `${Math.min(100, Math.max(4, widthPercent))}%` }}
                      />
                    </div>
                    <span className="intelligence-contrib-val" style={{ color: "#1A3C2B" }}>
                      {c.contribution.toFixed(2)}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Longitudinal History */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 className="intelligence-overview-card-title" style={{ fontSize: "16px" }}>
              Longitudinal Risk History
            </h3>
            <span className="intelligence-section-subtitle">
              {historyItems.length} EVALUATED MONTHS
            </span>
          </div>

          {historyLoading ? (
            <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
              LOADING LONGITUDINAL RISK HISTORY...
            </div>
          ) : historyItems.length === 0 ? (
            <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
              NO HISTORICAL EVALUATION OBSERVATIONS FOUND.
            </div>
          ) : (
            <div style={{ maxHeight: "200px", overflowY: "auto", border: "1px solid var(--color-border-hairline)" }}>
              <table className="intelligence-table">
                <thead>
                  <tr>
                    <th>MONTH</th>
                    <th>RISK PROBABILITY</th>
                    <th>RAW PROBABILITY</th>
                    <th>RANK</th>
                  </tr>
                </thead>
                <tbody>
                  {historyItems.map((h) => (
                    <tr key={h.report_month}>
                      <td style={{ fontWeight: 600 }}>{h.report_month}</td>
                      <td style={{ color: "#BA1A1A", fontWeight: 700 }}>
                        {(h.risk_probability * 100).toFixed(1)}%
                      </td>
                      <td style={{ color: "var(--color-text-muted)" }}>
                        {(h.raw_probability * 100).toFixed(1)}%
                      </td>
                      <td>#{h.risk_rank}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
