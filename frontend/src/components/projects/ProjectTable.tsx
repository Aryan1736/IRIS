import React from "react";
import { Link, useNavigate } from "react-router-dom";
import type { ProjectSummaryItem } from "@/types/project.ts";
import { ArrowUpRight, Eye } from "lucide-react";
import { useStaggerList } from "@/lib/motion/useMotion.ts";

interface ProjectTableProps {
  projects: ProjectSummaryItem[];
  isLoading?: boolean;
  onInspect?: (project: ProjectSummaryItem) => void;
  onResetFilters?: () => void;
}

export const ProjectTable: React.FC<ProjectTableProps> = ({
  projects,
  isLoading = false,
  onInspect,
  onResetFilters,
}) => {
  const navigate = useNavigate();
  const tbodyRef = useStaggerList<HTMLTableSectionElement>(projects, "tr.project-row");

  if (isLoading) {
    return (
      <div className="table-wrapper" aria-label="Loading Projects">
        <table className="projects-table">
          <thead>
            <tr>
              <th style={{ width: "30%" }}>PROJECT</th>
              <th style={{ width: "12%" }}>PROJECT CODE</th>
              <th style={{ width: "12%" }}>SECTOR</th>
              <th style={{ width: "12%" }}>AGENCY</th>
              <th style={{ width: "10%" }}>STATE / REGION</th>
              <th style={{ width: "10%" }}>LATEST REPORT</th>
              <th style={{ width: "14%" }}>PHYSICAL PROGRESS</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 8 }).map((_, idx) => (
              <tr key={`skeleton-${idx}`} className="project-table-skeleton-row">
                <td>
                  <div className="skeleton-bar" style={{ width: "75%", height: "14px", marginBottom: "6px" }} />
                  <div className="skeleton-bar" style={{ width: "45%", height: "10px" }} />
                </td>
                <td><div className="skeleton-bar" style={{ width: "65px", height: "12px" }} /></td>
                <td><div className="skeleton-bar" style={{ width: "80px", height: "12px" }} /></td>
                <td><div className="skeleton-bar" style={{ width: "70px", height: "12px" }} /></td>
                <td><div className="skeleton-bar" style={{ width: "50px", height: "12px" }} /></td>
                <td><div className="skeleton-bar" style={{ width: "60px", height: "12px" }} /></td>
                <td>
                  <div className="skeleton-bar" style={{ width: "100%", height: "10px" }} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="table-wrapper" aria-label="Project Records Table">
      <table className="projects-table">
        <thead>
          <tr>
            <th style={{ width: "30%" }}>PROJECT</th>
            <th style={{ width: "12%" }}>PROJECT CODE</th>
            <th style={{ width: "12%" }}>SECTOR</th>
            <th style={{ width: "12%" }}>AGENCY</th>
            <th style={{ width: "10%" }}>STATE / REGION</th>
            <th style={{ width: "10%" }}>LATEST REPORT</th>
            <th style={{ width: "14%" }}>PHYSICAL PROGRESS</th>
          </tr>
        </thead>
        <tbody ref={tbodyRef}>
          {projects.map((project) => {
            const encodedCode = encodeURIComponent(project.project_code);
            const progress = project.physical_progress;
            const progressVal = progress != null ? Math.max(0, Math.min(100, progress)) : null;

            return (
              <tr
                key={project.id ? `project-${project.id}` : `${project.project_code}-${project.report_month}`}
                className="project-row"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    navigate(`/projects/${encodedCode}`);
                  }
                }}
              >
                {/* Project Name Cell */}
                <td className="col-project-name">
                  <div className="project-name-cell-wrapper">
                    <Link
                      to={`/projects/${encodedCode}`}
                      className="project-name-link"
                      title={project.project_name || project.project_code}
                    >
                      {project.project_name || "—"}
                    </Link>
                    <div className="project-sub-meta">
                      {project.agency && <span>{project.agency}</span>}
                      {project.ministry && <span>• {project.ministry}</span>}
                    </div>
                  </div>
                </td>

                {/* Project Code */}
                <td className="col-project-code">
                  <Link
                    to={`/projects/${encodedCode}`}
                    className="project-code-link"
                  >
                    {project.project_code}
                  </Link>
                </td>

                {/* Sector */}
                <td className="col-sector">{project.sector || "—"}</td>

                {/* Agency */}
                <td className="col-agency">{project.agency || "—"}</td>

                {/* State */}
                <td className="col-state">{project.state || "—"}</td>

                {/* Report Month */}
                <td className="col-report">
                  <span className="report-month-badge">
                    {project.report_month || "DATA PENDING"}
                  </span>
                </td>

                {/* Physical Progress & Actions */}
                <td className="col-progress">
                  <div className="progress-cell-container">
                    <div className="progress-metrics-row">
                      <span className="progress-value-text">
                        {progress != null ? `${progress}%` : "—"}
                      </span>
                      {onInspect && (
                        <button
                          type="button"
                          className="project-row-inspect-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            onInspect(project);
                          }}
                          aria-label={`Inspect ${project.project_name || project.project_code}`}
                          title="Open Quick Inspection Drawer"
                        >
                          <Eye size={12} />
                          <span>INSPECT</span>
                        </button>
                      )}
                      <Link
                        to={`/projects/${encodedCode}`}
                        className="project-row-open-link"
                        aria-label={`Open project ${project.project_name || project.project_code}`}
                        title="View Full Longitudinal Project"
                      >
                        <ArrowUpRight size={13} />
                      </Link>
                    </div>

                    {/* Progress Bar Track */}
                    {progressVal !== null ? (
                      <div
                        className="progress-bar-track"
                        role="progressbar"
                        aria-valuenow={progressVal}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`Physical progress ${progress} percent`}
                      >
                        <div
                          className="progress-bar-fill"
                          style={{ width: `${progressVal}%` }}
                        />
                      </div>
                    ) : (
                      <div className="progress-bar-track progress-bar-empty" />
                    )}
                  </div>
                </td>
              </tr>
            );
          })}

          {projects.length === 0 && (
            <tr>
              <td colSpan={7}>
                <div className="empty-projects-container">
                  <div className="empty-projects-title">NO PROJECTS FOUND MATCHING CURRENT QUERY</div>
                  <p className="empty-projects-subtitle">
                    No infrastructure records match your active search terms or taxonomy filters.
                  </p>
                  {onResetFilters && (
                    <button
                      type="button"
                      className="empty-projects-reset-btn"
                      onClick={onResetFilters}
                    >
                      RESET SEARCH & CLEAR ALL FILTERS
                    </button>
                  )}
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
