import React from "react";
import { Link } from "react-router-dom";
import type { ProjectListResponse, RiskRecord } from "@/types/risk.ts";

interface RiskProjectTableProps {
  data?: ProjectListResponse;
  isLoading: boolean;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onSelectProject: (project: RiskRecord) => void;
}

export const RiskProjectTable: React.FC<RiskProjectTableProps> = ({
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

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <h2 className="intelligence-section-title">02. Projects Requiring Attention</h2>
        <span className="intelligence-section-subtitle">
          RANKED EVALUATION ({total.toLocaleString()} MONITORED PROJECTS)
        </span>
      </div>

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
          <tbody>
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

                    {/* Risk Probability */}
                    <td>
                      <div className="intelligence-prob-val" style={{ color: "#BA1A1A" }}>
                        {(project.risk_probability * 100).toFixed(1)}%
                      </div>
                      <span className="intelligence-prob-raw">
                        RAW: {(project.raw_probability * 100).toFixed(1)}%
                      </span>
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
                    <td style={{ maxWidth: "220px" }}>
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
