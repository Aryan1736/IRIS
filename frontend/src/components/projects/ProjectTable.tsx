import React from "react";
import { useNavigate } from "react-router-dom";
import type { ProjectSummaryItem } from "@/types/project.ts";
import { ArrowRight } from "lucide-react";

interface ProjectTableProps {
  projects: ProjectSummaryItem[];
}

export const ProjectTable: React.FC<ProjectTableProps> = ({ projects }) => {
  const navigate = useNavigate();

  return (
    <div className="table-wrapper">
      <table className="projects-table">
        <thead>
          <tr>
            <th>PROJECT</th>
            <th>PROJECT CODE</th>
            <th>SECTOR</th>
            <th>AGENCY</th>
            <th>STATE</th>
            <th>LATEST REPORT</th>
            <th>PHYSICAL PROGRESS</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project) => (
            <tr
              key={project.project_code}
              onClick={() => navigate(`/projects/${project.project_code}`)}
            >
              <td className="col-project-name">{project.project_name || "—"}</td>
              <td className="col-project-code">{project.project_code}</td>
              <td className="col-sector">{project.sector || "—"}</td>
              <td className="col-agency">{project.agency || "—"}</td>
              <td className="col-state">{project.state || "—"}</td>
              <td className="col-report">{project.report_month || "—"}</td>
              <td>
                <div className="col-progress-content">
                  <span className="progress-value">
                    {project.physical_progress !== null && project.physical_progress !== undefined
                      ? `${project.physical_progress}%`
                      : "—"}
                  </span>
                  <span className="row-arrow">
                    <ArrowRight size={14} />
                  </span>
                </div>
              </td>
            </tr>
          ))}
          {projects.length === 0 && (
            <tr>
              <td colSpan={7} className="empty-table-message">
                NO PROJECTS FOUND MATCHING FILTERS.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
