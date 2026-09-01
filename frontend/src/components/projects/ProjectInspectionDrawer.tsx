import React, { useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import type { ProjectSummaryItem } from "@/types/project.ts";
import { X, ArrowUpRight, ShieldCheck } from "lucide-react";
import { animateDrawerEnter, animateDrawerExit } from "@/lib/motion/presets.ts";

interface ProjectInspectionDrawerProps {
  project: ProjectSummaryItem | null;
  onClose: () => void;
}

export const ProjectInspectionDrawer: React.FC<ProjectInspectionDrawerProps> = ({
  project,
  onClose,
}) => {
  const overlayRef = useRef<HTMLDivElement>(null);
  const drawerRef = useRef<HTMLDivElement>(null);
  const isClosing = useRef(false);

  const handleClose = useCallback(() => {
    if (isClosing.current) return;
    isClosing.current = true;
    animateDrawerExit(overlayRef.current, drawerRef.current, () => {
      onClose();
    });
  }, [onClose]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleClose();
      }
    };

    if (project) {
      window.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
      // Animate entrance
      animateDrawerEnter(overlayRef.current, drawerRef.current);
    }

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [project, handleClose]);

  if (!project) return null;

  const encodedCode = encodeURIComponent(project.project_code);
  const progressVal = project.physical_progress != null ? Math.max(0, Math.min(100, project.physical_progress)) : null;

  return (
    <div
      ref={overlayRef}
      className="project-drawer-overlay"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-drawer-title"
    >
      <div
        ref={drawerRef}
        className="project-drawer-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="project-drawer-header">
          <div className="project-drawer-header-left">
            <span className="project-drawer-tag">PROJECT INSPECTION CONSOLE</span>
            <span className="project-drawer-code">{project.project_code}</span>
          </div>
          <button
            type="button"
            className="project-drawer-close-btn"
            onClick={handleClose}
            aria-label="Close project inspection console"
          >
            <X size={16} />
          </button>
        </div>

        <div className="project-drawer-body">
          {/* Project Title Block */}
          <div className="project-drawer-title-block">
            <h2 id="project-drawer-title" className="project-drawer-title">
              {project.project_name || "—"}
            </h2>
            <div className="project-drawer-subtitle">
              <span>{project.agency || "—"}</span>
              {project.ministry && <span>• {project.ministry}</span>}
            </div>
          </div>

          {/* Key Facts Metric Grid */}
          <div className="project-drawer-facts-grid">
            <div className="drawer-fact-cell">
              <span className="drawer-fact-label">SECTOR</span>
              <span className="drawer-fact-value">{project.sector || "—"}</span>
            </div>
            <div className="drawer-fact-cell">
              <span className="drawer-fact-label">STATE / REGION</span>
              <span className="drawer-fact-value">{project.state || "—"}</span>
            </div>
            <div className="drawer-fact-cell">
              <span className="drawer-fact-label">LATEST REPORT</span>
              <span className="drawer-fact-value" style={{ color: "#1A3C2B", fontWeight: 700 }}>
                {project.report_month || "—"}
              </span>
            </div>
            <div className="drawer-fact-cell">
              <span className="drawer-fact-label">PHYSICAL PROGRESS</span>
              <span className="drawer-fact-value">
                {progressVal !== null ? `${progressVal}%` : "NOT REPORTED"}
              </span>
            </div>
          </div>

          {/* Progress Pacing Visual Bar */}
          {progressVal !== null && (
            <div className="drawer-section-block">
              <div className="drawer-section-header">
                <span className="drawer-section-title">PHYSICAL COMPLETION PACING</span>
                <span className="drawer-section-val">{progressVal}%</span>
              </div>
              <div className="drawer-progress-track">
                <div
                  className="drawer-progress-fill"
                  style={{ width: `${progressVal}%` }}
                />
              </div>
            </div>
          )}

          {/* Financial Metrics */}
          <div className="drawer-section-block">
            <div className="drawer-section-header">
              <span className="drawer-section-title">FINANCIAL METRICS (RS CRORE)</span>
            </div>
            <div className="project-drawer-facts-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
              <div className="drawer-fact-cell">
                <span className="drawer-fact-label">ORIGINAL COST</span>
                <span className="drawer-fact-value">
                  {project.original_cost != null ? `₹${project.original_cost.toLocaleString()}` : "—"}
                </span>
              </div>
              <div className="drawer-fact-cell">
                <span className="drawer-fact-label">REVISED COST</span>
                <span className="drawer-fact-value">
                  {project.revised_cost != null ? `₹${project.revised_cost.toLocaleString()}` : "—"}
                </span>
              </div>
              <div className="drawer-fact-cell">
                <span className="drawer-fact-label">EXPENDITURE</span>
                <span className="drawer-fact-value">
                  {project.cumulative_expenditure != null ? `₹${project.cumulative_expenditure.toLocaleString()}` : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* Schedule Timeline */}
          <div className="drawer-section-block">
            <div className="drawer-section-header">
              <span className="drawer-section-title">SCHEDULE TIMELINE</span>
            </div>
            <div className="project-drawer-facts-grid" style={{ gridTemplateColumns: "repeat(2, 1fr)" }}>
              <div className="drawer-fact-cell">
                <span className="drawer-fact-label">APPROVAL DATE</span>
                <span className="drawer-fact-value">{project.approval_date || "—"}</span>
              </div>
              <div className="drawer-fact-cell">
                <span className="drawer-fact-label">ORIGINAL COMPLETION</span>
                <span className="drawer-fact-value">{project.original_completion_date || "—"}</span>
              </div>
            </div>
          </div>

          {/* Source Provenance Info */}
          <div className="drawer-provenance-box">
            <div className="drawer-provenance-title">
              <ShieldCheck size={14} color="#1A3C2B" />
              <span>CANONICAL SOURCE PROVENANCE</span>
            </div>
            <div className="drawer-provenance-row">
              <span>REPORT MONTH:</span>
              <strong>{project.report_month || "PAIMANA_FLASH_REPORT"}</strong>
            </div>
            <div className="drawer-provenance-row">
              <span>CANONICAL ID:</span>
              <strong>{project.project_code}</strong>
            </div>
            <div className="drawer-provenance-row">
              <span>EXTRACTION PIPELINE:</span>
              <strong>TABLE6_CANONICAL_VERIFIED</strong>
            </div>
          </div>
        </div>

        {/* Drawer Action Footer */}
        <div className="project-drawer-footer">
          <Link
            to={`/projects/${encodedCode}`}
            className="project-drawer-detail-link"
            onClick={onClose}
          >
            <span>OPEN FULL LONGITUDINAL ANALYSIS</span>
            <ArrowUpRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  );
};
