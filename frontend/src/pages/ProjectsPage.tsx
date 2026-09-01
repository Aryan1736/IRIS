import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects, fetchFilterOptions } from "@/api/projects.ts";
import { fetchDatasetInfo } from "@/api/system.ts";
import { ProjectSearch, Filters } from "@/components/projects/ProjectSearch.tsx";
import { PortfolioSnapshot } from "@/components/projects/PortfolioSnapshot.tsx";
import { ProjectTable } from "@/components/projects/ProjectTable.tsx";
import { ProjectPagination } from "@/components/projects/ProjectPagination.tsx";
import { ProjectInspectionDrawer } from "@/components/projects/ProjectInspectionDrawer.tsx";
import type { ProjectSummaryItem } from "@/types/project.ts";
import { ShieldCheck, AlertCircle } from "lucide-react";
import { usePageEnter } from "@/lib/motion/useMotion.ts";

export const ProjectsPage: React.FC = () => {
  const containerRef = usePageEnter<HTMLDivElement>();
  const [filters, setFilters] = useState<Filters>({});
  const [page, setPage] = useState(1);
  const [inspectingProject, setInspectingProject] = useState<ProjectSummaryItem | null>(null);
  const pageSize = 25;

  const {
    data: projectsData,
    isLoading: isProjectsLoading,
    isError: isProjectsError,
    error: projectsError,
    refetch: refetchProjects,
  } = useQuery({
    queryKey: ["projects", filters, page],
    queryFn: () => fetchProjects({ ...filters, page, page_size: pageSize }),
  });

  const { data: systemInfo, isLoading: isSystemLoading } = useQuery({
    queryKey: ["systemInfo"],
    queryFn: fetchDatasetInfo,
  });

  const { data: filterOptions, isLoading: isOptionsLoading } = useQuery({
    queryKey: ["filterOptions"],
    queryFn: fetchFilterOptions,
  });

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilters({});
    setPage(1);
  };

  const total = projectsData?.total ?? 0;
  const totalPages = projectsData?.total_pages ?? 0;

  const getMonitoredPeriod = () => {
    if (!systemInfo?.covered_months || systemInfo.covered_months.length === 0) {
      return "DATA PENDING";
    }
    const sorted = [...systemInfo.covered_months].sort();
    return `${sorted[0]} → ${sorted[sorted.length - 1]}`;
  };

  const uniqueProjectsCount = systemInfo?.unique_projects_count != null
    ? systemInfo.unique_projects_count.toLocaleString()
    : "—";

  const observationsCount = systemInfo?.row_count != null
    ? systemInfo.row_count.toLocaleString()
    : "—";

  return (
    <div style={{ minHeight: "calc(100vh - 64px)", display: "flex", flexDirection: "column", width: "100%" }}>
      <div ref={containerRef} className="projects-container">
        {/* Page Intro Hero Section */}
        <section className="projects-intro-section">
          <div className="projects-intro-left">
            <div className="projects-breadcrumb">IRIS / PROJECTS / DISCOVERY</div>
            <h1 className="projects-main-title">PROJECTS. FIND THE SIGNAL.</h1>
            <p className="projects-description">
              Search and examine infrastructure projects across the monitored portfolio, reporting history, sectors, agencies, and states.
            </p>
          </div>

          <div className="projects-metric-panel">
            <div className="projects-telemetry-row">
              <span className="projects-telemetry-label">UNIQUE PROJECTS</span>
              <span className="projects-telemetry-val">{isSystemLoading ? "..." : uniqueProjectsCount}</span>
            </div>
            <div className="projects-telemetry-row">
              <span className="projects-telemetry-label">OBSERVATIONS</span>
              <span className="projects-telemetry-val">{isSystemLoading ? "..." : observationsCount}</span>
            </div>
            <div className="projects-telemetry-row">
              <span className="projects-telemetry-label">COVERED PERIOD</span>
              <span className="projects-telemetry-val" style={{ color: "#1A3C2B" }}>{getMonitoredPeriod()}</span>
            </div>
            <div className="projects-telemetry-row">
              <span className="projects-telemetry-label">INTEGRITY</span>
              <span className="projects-telemetry-val" style={{ color: "#1A3C2B" }}>VERIFIED PIPELINE</span>
            </div>
          </div>
        </section>

        {/* Section 01: Portfolio Snapshot & Taxonomy Telemetry */}
        <PortfolioSnapshot
          systemInfo={systemInfo}
          options={filterOptions}
          isLoading={isSystemLoading || isOptionsLoading}
        />

        {/* Project Search & Filter Command Bar */}
        <ProjectSearch
          filters={filters}
          onFilterChange={handleFilterChange}
          options={filterOptions}
        />

        {/* Section 02: Project Directory Results */}
        <section className="portfolio-section" aria-label="Project Records Directory">
          <div className="portfolio-header-row">
            <div>
              <div className="portfolio-section-num-tag">02. PROJECT DIRECTORY</div>
              <h2 className="portfolio-heading">MONITORED PROJECT RECORDS</h2>
              <div className="portfolio-count">
                {total > 0
                  ? `SHOWING 1–${Math.min(pageSize, total).toLocaleString()} OF ${total.toLocaleString()} MATCHING OBSERVATIONS`
                  : "0 MATCHING OBSERVATIONS"}
              </div>
            </div>
          </div>

          {isProjectsError ? (
            <div className="projects-error-banner" role="alert">
              <div className="projects-error-icon">
                <AlertCircle size={20} />
              </div>
              <div className="projects-error-content">
                <div className="projects-error-title">PROJECT DIRECTORY UNAVAILABLE</div>
                <p className="projects-error-message">
                  {projectsError instanceof Error ? projectsError.message : "Unable to retrieve project records from the monitoring service."}
                </p>
                <button
                  type="button"
                  className="projects-error-retry-btn"
                  onClick={() => refetchProjects()}
                >
                  RETRY CONNECTION
                </button>
              </div>
            </div>
          ) : (
            <>
              <ProjectTable
                projects={projectsData?.items || []}
                isLoading={isProjectsLoading}
                onInspect={(project) => setInspectingProject(project)}
                onResetFilters={handleResetFilters}
              />
              <ProjectPagination
                page={page}
                pageSize={pageSize}
                total={total}
                totalPages={totalPages}
                onPageChange={setPage}
                entityName="MATCHING OBSERVATIONS"
              />
            </>
          )}
        </section>
      </div>

      {/* Project Quick Inspection Console Drawer */}
      <ProjectInspectionDrawer
        project={inspectingProject}
        onClose={() => setInspectingProject(null)}
      />

      {/* Bottom Data Provenance Strip */}
      <footer className="provenance-strip">
        <div className="provenance-strip-inner">
          <div className="provenance-metrics">
            <span>SOURCE: PAIMANA MONITORING DATA</span>
            <span>OBSERVATIONS: {observationsCount}</span>
            <span>PROJECTS: {uniqueProjectsCount}</span>
            <span>MONITORED PERIOD: {getMonitoredPeriod()}</span>
          </div>
          <div className="provenance-status">
            <ShieldCheck size={15} />
            <span>DATA INTEGRITY: VERIFIED</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
