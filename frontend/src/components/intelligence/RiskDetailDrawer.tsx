import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Brush,
} from "recharts";
import type { RiskRecord, TopRiskProject } from "@/types/risk.ts";
import { fetchProjectRiskHistory, fetchProjectRiskRecord } from "@/api/risk.ts";
import { IrisChartTooltip } from "@/components/common/charts/IrisChartTooltip.tsx";
import { IrisSignedDriversChart } from "@/components/common/charts/IrisSignedDriversChart.tsx";
import { animateDrawerEnter, animateDrawerExit } from "@/lib/motion/presets.ts";

interface RiskDetailDrawerProps {
  record: RiskRecord | TopRiskProject | null;
  onClose: () => void;
}

export const RiskDetailDrawer: React.FC<RiskDetailDrawerProps> = ({ record, onClose }) => {
  const overlayRef = React.useRef<HTMLDivElement>(null);
  const drawerRef = React.useRef<HTMLDivElement>(null);
  const isClosing = React.useRef(false);

  const handleClose = React.useCallback(() => {
    if (isClosing.current) return;
    isClosing.current = true;
    animateDrawerExit(overlayRef.current, drawerRef.current, () => {
      onClose();
    });
  }, [onClose]);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleClose();
      }
    };

    if (record) {
      window.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
      animateDrawerEnter(overlayRef.current, drawerRef.current);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [record, handleClose]);

  const projectCode = record?.project_code || "";

  // 1. Fetch full project risk record if contributors are not embedded (e.g. from TopRiskProject)
  const isFullRecord = record && "top_positive_contributors" in record;
  const { data: fullRecordData } = useQuery({
    queryKey: ["projectRiskRecord", projectCode],
    queryFn: () => fetchProjectRiskRecord(projectCode, "2026-04"),
    enabled: !isFullRecord && !!projectCode,
  });

  // 2. Fetch project risk history for longitudinal line chart
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ["projectRiskHistory", projectCode],
    queryFn: () => fetchProjectRiskHistory(projectCode),
    enabled: !!projectCode,
  });

  if (!record) return null;

  const currentRecord = isFullRecord ? (record as RiskRecord) : fullRecordData || (record as unknown as RiskRecord);
  const historyItems = historyData?.items ? [...historyData.items] : [];
  // Sort history chronologically
  historyItems.sort((a, b) => a.report_month.localeCompare(b.report_month));

  const chartData = historyItems.map((h) => ({
    month: h.report_month,
    calibratedRisk: Number((h.risk_probability * 100).toFixed(1)),
    rawProbability: Number((h.raw_probability * 100).toFixed(1)),
    rank: h.risk_rank,
  }));

  const posContribs = currentRecord.top_positive_contributors || [];
  const negContribs = currentRecord.top_negative_contributors || [];
  const isTopRank = currentRecord.risk_rank <= 3;

  return (
    <div
      ref={overlayRef}
      className="intelligence-modal-backdrop"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-label="Risk Inspection Drawer"
    >
      <div
        ref={drawerRef}
        className="intelligence-drawer"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="intelligence-drawer-header">
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span className="intelligence-section-subtitle">PROJECT RISK INSPECTION CONSOLE</span>
            <h2 className="intelligence-main-title" style={{ fontSize: "24px" }}>
              {currentRecord.project_code}
            </h2>
            <span style={{ fontSize: "14px", color: "var(--color-text-secondary)" }}>
              {currentRecord.project_name || "—"}
            </span>
            <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
              {currentRecord.agency || currentRecord.sector || "—"}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Link
              to={`/projects/${encodeURIComponent(currentRecord.project_code)}`}
              className="intelligence-btn-inspect"
              style={{ textDecoration: "none" }}
            >
              VIEW FULL PROJECT →
            </Link>
            <button
              type="button"
              className="intelligence-drawer-close"
              onClick={handleClose}
              aria-label="Close drawer"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Hero Key Metrics Grid */}
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
            <div style={{ fontSize: "22px", fontWeight: 700, color: isTopRank ? "#BA1A1A" : "#1A3C2B" }}>
              {(currentRecord.risk_probability * 100).toFixed(1)}%
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              RAW: {(currentRecord.raw_probability * 100).toFixed(1)}%
            </span>
          </div>

          <div>
            <span className="intelligence-gov-label">PORTFOLIO RANK</span>
            <div style={{ fontSize: "22px", fontWeight: 700, color: "var(--color-primary-950)" }}>
              #{currentRecord.risk_rank}
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              OF {currentRecord.population_size || 1625} PROJECTS
            </span>
          </div>

          <div>
            <span className="intelligence-gov-label">PERCENTILE</span>
            <div style={{ fontSize: "22px", fontWeight: 700, color: "var(--color-primary-950)" }}>
              TOP {Math.max(0.1, (100 - currentRecord.risk_percentile * 100)).toFixed(1)}%
            </div>
            <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
              P{(currentRecord.risk_percentile * 100).toFixed(0)}
            </span>
          </div>
        </div>

        {/* Technical Governance Badges */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", alignItems: "center" }}>
          <span className="intelligence-badge-regime">{currentRecord.regime} REGIME</span>
          {currentRecord.calibration_active ? (
            <span className="intelligence-badge-calibrated">CALIBRATION ACTIVE</span>
          ) : (
            <span className="intelligence-badge-uncalibrated">RAW PROBABILITY</span>
          )}
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
            MODEL: {currentRecord.model_id}
          </span>
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}>
            SPACE: {currentRecord.version_metadata?.contribution_space || "RAW_MARGIN_LOGIT"}
          </span>
        </div>

        {/* Longitudinal History Recharts Composed Chart */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", background: "#FFFFFF", border: "1px solid var(--color-border-hairline)", padding: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="intelligence-section-subtitle" style={{ color: "var(--color-primary-950)", fontWeight: 700 }}>
              LONGITUDINAL RISK EVALUATION HISTORY
            </span>
            <span className="intelligence-section-subtitle">
              {historyItems.length} EVALUATED MONTHS
            </span>
          </div>

          {historyLoading ? (
            <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)", padding: "20px", textAlign: "center" }}>
              LOADING RISK HISTORY...
            </div>
          ) : chartData.length > 0 ? (
            <div style={{ width: "100%", height: 180 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 12, left: -20, bottom: 0 }} syncId="iris-risk-history">
                  <CartesianGrid stroke="#E2E3DF" strokeDasharray="3 3" vertical={false} />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: "#606460", fontSize: 10, fontFamily: "var(--font-mono)" }}
                    stroke="#E2E3DF"
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#606460", fontSize: 10, fontFamily: "var(--font-mono)" }}
                    stroke="#E2E3DF"
                    tickFormatter={(v) => `${v}%`}
                  />
                  <Tooltip
                    content={
                      <IrisChartTooltip
                        titlePrefix="EVAL MONTH"
                        customFormatter={(payload) => {
                          const entry = Array.isArray(payload) ? payload[0]?.payload : undefined;
                          if (!entry) return [];
                          return [
                            {
                              label: "CALIBRATED RISK",
                              value: `${entry.calibratedRisk}%`,
                              color: entry.rank <= 3 ? "#BA1A1A" : "#1A3C2B",
                            },
                            {
                              label: "RAW PROBABILITY",
                              value: `${entry.rawProbability}%`,
                              color: "#A0A4A0",
                            },
                            {
                              label: "PORTFOLIO RANK",
                              value: `#${entry.rank}`,
                              color: "#FFFFFF",
                            },
                          ];
                        }}
                      />
                    }
                  />
                  <Legend
                    verticalAlign="top"
                    align="right"
                    wrapperStyle={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "9px",
                      letterSpacing: "0.06em",
                      textTransform: "uppercase",
                      paddingBottom: "4px",
                    }}
                  />
                  <Line
                    type="linear"
                    dataKey="calibratedRisk"
                    name="Calibrated Risk"
                    stroke="#1A3C2B"
                    strokeWidth={2}
                    dot={{ r: 3.5, fill: "#1A3C2B", stroke: "#FFFFFF", strokeWidth: 1.5 }}
                    activeDot={{ r: 5.5, fill: "#BA1A1A", stroke: "#FFFFFF", strokeWidth: 2 }}
                    isAnimationActive={false}
                  />
                  <Line
                    type="linear"
                    dataKey="rawProbability"
                    name="Raw Probability"
                    stroke="#8A8E8A"
                    strokeWidth={1.5}
                    strokeDasharray="4 2"
                    dot={{ r: 2.5, fill: "#8A8E8A", stroke: "#FFFFFF", strokeWidth: 1 }}
                    activeDot={{ r: 4.5, fill: "#1A3C2B", stroke: "#FFFFFF", strokeWidth: 1.5 }}
                    isAnimationActive={false}
                  />
                  {chartData.length > 12 && (
                    <Brush dataKey="month" height={18} stroke="#1A3C2B" />
                  )}
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)", padding: "10px", textAlign: "center" }}>
              NO HISTORICAL EVALUATIONS FOUND.
            </div>
          )}
        </div>

        {/* Explainability Section: Signed Feature Drivers Recharts Chart & List */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", background: "#FFFFFF", border: "1px solid var(--color-border-hairline)", padding: "16px" }}>
          <div style={{ borderBottom: "1px solid var(--color-border-hairline)", paddingBottom: "8px" }}>
            <h3 className="intelligence-overview-card-title" style={{ fontSize: "16px" }}>
              Signed Feature Drivers (Model Contributions)
            </h3>
            <span className="intelligence-section-subtitle">
              METHOD: {currentRecord.version_metadata?.explanation_method || "TREESHAP"} (RAW MARGIN LOGITS)
            </span>
            <div style={{ fontSize: "10px", color: "var(--color-text-muted)", marginTop: "4px", lineHeight: 1.4 }}>
              Values represent signed margin contributions to model logit space, not probabilities or verified causal mechanisms.
            </div>
          </div>

          <IrisSignedDriversChart
            positiveContributors={posContribs}
            negativeContributors={negContribs}
            height={Math.max(160, (posContribs.length + negContribs.length) * 36)}
          />

          {/* Accessible Driver Breakdown Items */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "12px" }}>
            {posContribs.map((c) => (
              <div key={c.feature} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                <span style={{ color: "var(--color-primary-950)" }}>▲ {c.display_name || c.feature}</span>
                <span style={{ color: "#BA1A1A", fontWeight: 700 }}>+{c.contribution.toFixed(2)}</span>
              </div>
            ))}
            {negContribs.map((c) => (
              <div key={c.feature} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                <span style={{ color: "var(--color-primary-950)" }}>▼ {c.display_name || c.feature}</span>
                <span style={{ color: "#1A3C2B", fontWeight: 700 }}>{c.contribution.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* History Table */}
        {historyItems.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "16px" }}>
            <span className="intelligence-section-subtitle">HISTORICAL EVALUATION TABLE</span>
            <div style={{ maxHeight: "180px", overflowY: "auto", border: "1px solid var(--color-border-hairline)" }}>
              <table className="intelligence-table">
                <thead>
                  <tr>
                    <th>MONTH</th>
                    <th>CALIBRATED RISK</th>
                    <th>RAW PROBABILITY</th>
                    <th>RANK</th>
                  </tr>
                </thead>
                <tbody>
                  {historyItems.map((h) => (
                    <tr key={h.report_month}>
                      <td style={{ fontWeight: 600 }}>{h.report_month}</td>
                      <td style={{ color: h.risk_rank <= 3 ? "#BA1A1A" : "var(--color-primary-950)", fontWeight: 700 }}>
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
          </div>
        )}
      </div>
    </div>
  );
};
