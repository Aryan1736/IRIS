import React from "react";
import { Link } from "react-router-dom";
import type { ProjectListResponse, RiskRecord, TopRiskProject } from "@/types/risk.ts";
import { IrisTopRiskRankingChart } from "@/components/common/charts/IrisTopRiskRankingChart.tsx";
import { useStaggerList } from "@/lib/motion/useMotion.ts";

interface RiskProjectTableProps {
  topRiskProjects?: TopRiskProject[];
  data?: ProjectListResponse;
  isLoading: boolean;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onSelectProject: (project: RiskRecord | TopRiskProject) => void;
}

export const RiskProjectTable: React.FC<RiskProjectTableProps> = ({
  topRiskProjects,
  data,
  isLoading,
  page,
  pageSize,
  onPageChange,
  onSelectProject,
}) => {
  const items = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const topList = topRiskProjects || [];
  const tbodyRef = useStaggerList<HTMLTableSectionElement>(items, "tr");

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <div className="intelligence-section-title-lockup">
          <h2 className="intelligence-section-title">02. Highest-Risk Projects</h2>
          <span className="intelligence-section-subtitle">
            RANKED EVALUATION ({total.toLocaleString()} MONITORED PROJECTS)
          </span>
        </div>
        <span className="intelligence-section-subtitle">
          SORT: DESCENDING RISK PROBABILITY
        </span>
      </div>

      {/* Top-Risk Visual Ranking Horizontal BarChart */}
      {topList.length > 0 && (
        <div className="intelligence-top-risk-ranking-card" style={{ background: "#FFFFFF", border: "1px solid var(--color-border-hairline)", padding: "16px 20px", display: "flex", flexDirection: "column", gap: "12px", marginBottom: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="intelligence-section-subtitle" style={{ color: "var(--color-primary-950)", fontWeight: 700 }}>
              CONCENTRATED RISK ELEVATION RANKING (TOP {topList.length} EVALUATED)
            </span>
            <span className="intelligence-section-subtitle">
              CLICK BAR TO INSPECT PROJECT
            </span>
          </div>

          <IrisTopRiskRankingChart
            projects={topList}
            onSelectProject={onSelectProject}
            height={Math.max(220, topList.length * 36)}
          />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "8px", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-muted)" }}>
            <span>SCALE: 0% → 100% CALIBRATED PROBABILITY</span>
            <span>VISUAL HIERARCHY: TOP ELEVATED RANKS HIGHLIGHTED IN CORAL | INSTITUTIONAL EVERGREEN</span>
          </div>
        </div>
      )}

      {/* Ranked Project Table */}
      <div className="intelligence-table-card">
        <table className="intelligence-table" aria-label="Risk Ranked Projects Table">
          <thead>
            <tr>
              <th>RANK</th>
              <th>PROJECT</th>
              <th>RISK PROBABILITY</th>
              <th>PERCENTILE</th>
              <th>REGIME</th>
              <th>CALIBRATION</th>
              <th>TOP EARLY-WARNING DRIVER</th>
              <th style={{ textAlign: "right" }}>ACTION</th>
            </tr>
          </thead>
          <tbody ref={tbodyRef}>
            {isLoading ? (
              <tr>
                <td colSpan={8} style={{ textAlign: "center", padding: "40px" }}>
                  <div className="intelligence-section-subtitle">LOADING RISK INTELLIGENCE DATA...</div>
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: "center", padding: "40px" }}>
                  <div className="intelligence-section-subtitle">NO RISK RECORDS MATCH THE CURRENT FILTERS.</div>
                </td>
              </tr>
            ) : (
              items.map((project) => {
                const topPos = project.top_positive_contributors?.[0];
                const topDriverText = topPos
                  ? `${topPos.display_name || topPos.feature} (+${topPos.contribution.toFixed(2)})`
                  : "—";

                const probPercent = project.risk_probability * 100;
                const isTopRank = project.risk_rank <= 3;

                return (
                  <tr key={project.project_code}>
                    {/* Rank */}
                    <td className="intelligence-rank-cell">
                      #{project.risk_rank}
                    </td>

                    {/* Project Code & Name */}
                    <td>
                      <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                        <Link
                          to={`/projects/${encodeURIComponent(project.project_code)}`}
                          className="intelligence-project-code"
                        >
                          {project.project_code}
                        </Link>
                        <span className="intelligence-project-name" title={project.project_name || "—"}>
                          {project.project_name || "—"}
                        </span>
                        <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
                          {project.agency || project.sector || "—"}
                        </span>
                      </div>
                    </td>

                    {/* Risk Probability with internal visual bar */}
                    <td>
                      <div className="intelligence-prob-cell">
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                          <span
                            className="intelligence-prob-val"
                            style={{ color: isTopRank ? "#BA1A1A" : "var(--color-primary-950)" }}
                          >
                            {probPercent.toFixed(1)}%
                          </span>
                          <span className="intelligence-prob-raw">
                            RAW: {(project.raw_probability * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="intelligence-prob-bar-track">
                          <div
                            className="intelligence-prob-bar-fill"
                            style={{
                              width: `${Math.min(100, Math.max(4, probPercent))}%`,
                              backgroundColor: isTopRank ? "#BA1A1A" : "#1A3C2B",
                            }}
                          />
                        </div>
                      </div>
                    </td>

                    {/* Percentile */}
                    <td>
                      <div style={{ fontWeight: 600 }}>
                        TOP {Math.max(0.1, (100 - project.risk_percentile * 100)).toFixed(1)}%
                      </div>
                      <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
                        P{(project.risk_percentile * 100).toFixed(0)}
                      </span>
                    </td>

                    {/* Regime */}
                    <td>
                      <span className="intelligence-badge-regime">
                        {project.regime}
                      </span>
                    </td>

                    {/* Calibration */}
                    <td>
                      {project.calibration_active ? (
                        <span className="intelligence-badge-calibrated">
                          CALIBRATION ACTIVE
                        </span>
                      ) : (
                        <span className="intelligence-badge-uncalibrated">
                          RAW PROBABILITY
                        </span>
                      )}
                    </td>

                    {/* Top Driver */}
                    <td style={{ maxWidth: "240px" }}>
                      <span
                        style={{
                          fontSize: "11px",
                          color: topPos ? "var(--color-primary-950)" : "var(--color-text-muted)",
                          fontWeight: topPos ? 500 : 400,
                          display: "block",
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                        title={topDriverText}
                      >
                        {topDriverText}
                      </span>
                    </td>

                    {/* Action */}
                    <td style={{ textAlign: "right" }}>
                      <button
                        type="button"
                        className="intelligence-btn-inspect"
                        onClick={() => onSelectProject(project)}
                        aria-label={`Inspect ${project.project_code}`}
                      >
                        INSPECT
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="intelligence-pagination">
          <span className="intelligence-section-subtitle">
            PAGE {page} OF {totalPages} ({total.toLocaleString()} TOTAL PROJECTS)
          </span>

          <div className="intelligence-pagination-controls">
            <button
              type="button"
              className="intelligence-pagination-btn"
              disabled={page <= 1 || isLoading}
              onClick={() => onPageChange(page - 1)}
            >
              PREVIOUS
            </button>
            <button
              type="button"
              className="intelligence-pagination-btn"
              disabled={page >= totalPages || isLoading}
              onClick={() => onPageChange(page + 1)}
            >
              NEXT
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
