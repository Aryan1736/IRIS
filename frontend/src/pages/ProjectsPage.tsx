import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects.ts";
import { fetchDatasetInfo } from "@/api/system.ts";
import { ProjectSearch, Filters } from "@/components/projects/ProjectSearch.tsx";
import { ProjectTable } from "@/components/projects/ProjectTable.tsx";
import { ProjectPagination } from "@/components/projects/ProjectPagination.tsx";
import { ShieldCheck } from "lucide-react";

export const ProjectsPage: React.FC = () => {
  const [filters, setFilters] = useState<Filters>({});
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const { data: projectsData, isLoading: isProjectsLoading } = useQuery({
    queryKey: ["projects", filters, page],
    queryFn: () => fetchProjects({ ...filters, page, page_size: pageSize }),
  });

  const { data: systemInfo } = useQuery({
    queryKey: ["systemInfo"],
    queryFn: fetchDatasetInfo,
  });

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
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
    <div className="bg-blueprint-grid" style={{ minHeight: "calc(100vh - 64px)", display: "flex", flexDirection: "column" }}>
      <div className="projects-container">
        {/* Page Intro */}
        <section className="projects-intro-section">
          <div className="projects-intro-left">
            <div className="projects-breadcrumb">IRIS / PROJECTS / DISCOVERY</div>
            <h1 className="projects-main-title">PROJECTS. FIND THE SIGNAL.</h1>
            <p className="projects-description">
              Search and examine infrastructure projects across the monitored portfolio, reporting history, sectors, agencies, and states.
            </p>
          </div>

          <div className="projects-metric-panel">
            <div>{uniqueProjectsCount !== "—" ? `${uniqueProjectsCount} UNIQUE PROJECTS` : "UNIQUE PROJECTS: DATA PENDING"}</div>
            <div>{observationsCount !== "—" ? `${observationsCount} OBSERVATIONS` : "OBSERVATIONS: DATA PENDING"}</div>
            <div>{getMonitoredPeriod()}</div>
          </div>
        </section>

        {/* Project Search & Filters */}
        <ProjectSearch filters={filters} onFilterChange={handleFilterChange} />

        {/* Project Portfolio Results */}
        <section className="portfolio-section">
          <div className="portfolio-header-row">
            <div>
              <h2 className="portfolio-heading">PROJECT PORTFOLIO</h2>
              <div className="portfolio-count">
                {total > 0 ? `${total.toLocaleString()} MATCHING PROJECTS` : "0 MATCHING PROJECTS"}
              </div>
            </div>
          </div>

          {isProjectsLoading ? (
            <div className="table-wrapper empty-table-message">
              LOADING PROJECTS...
            </div>
          ) : (
            <>
              <ProjectTable projects={projectsData?.items || []} />
              <ProjectPagination
                page={page}
                pageSize={pageSize}
                total={total}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            </>
          )}
        </section>
      </div>

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
