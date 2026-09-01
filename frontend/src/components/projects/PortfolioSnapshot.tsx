import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";
import type { FilterOptionsResponse } from "@/types/project.ts";
import { useStaggerList } from "@/lib/motion/useMotion.ts";

interface PortfolioSnapshotProps {
  systemInfo?: DatasetInfoResponse;
  options?: FilterOptionsResponse;
  isLoading?: boolean;
}

export const PortfolioSnapshot: React.FC<PortfolioSnapshotProps> = ({
  systemInfo,
  options,
  isLoading = false,
}) => {
  const gridRef = useStaggerList<HTMLDivElement>(systemInfo, ".portfolio-snapshot-card");

  const uniqueProjects = systemInfo?.unique_projects_count != null
    ? systemInfo.unique_projects_count.toLocaleString()
    : "—";

  const observations = systemInfo?.row_count != null
    ? systemInfo.row_count.toLocaleString()
    : "—";

  const monthsCount = systemInfo?.covered_months?.length
    ? `${systemInfo.covered_months.length} MONTHS`
    : "—";

  const latestReport = systemInfo?.covered_months?.length
    ? [...systemInfo.covered_months].sort().slice(-1)[0]
    : "—";

  const sectorsCount = options?.sectors?.length != null
    ? options.sectors.length.toLocaleString()
    : "—";

  const agenciesCount = options?.agencies?.length != null
    ? options.agencies.length.toLocaleString()
    : "—";

  const statesCount = options?.states?.length != null
    ? options.states.length.toLocaleString()
    : "—";

  return (
    <section className="portfolio-snapshot-section" aria-label="Portfolio Snapshot">
      <div className="portfolio-snapshot-header">
        <span className="portfolio-snapshot-num">01.</span>
        <span className="portfolio-snapshot-title">PORTFOLIO SNAPSHOT & TAXONOMY TELEMETRY</span>
      </div>

      <div ref={gridRef} className="portfolio-snapshot-grid">
        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">TOTAL PROJECTS</span>
          <span className="snapshot-card-val">{isLoading ? "..." : uniqueProjects}</span>
          <span className="snapshot-card-sub">UNIQUE IDENTIFIERS</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">OBSERVATIONS</span>
          <span className="snapshot-card-val">{isLoading ? "..." : observations}</span>
          <span className="snapshot-card-sub">HISTORICAL RECORDS</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">MONITORED PERIOD</span>
          <span className="snapshot-card-val">{isLoading ? "..." : monthsCount}</span>
          <span className="snapshot-card-sub">LONGITUDINAL SPAN</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">LATEST EVALUATION</span>
          <span className="snapshot-card-val">{isLoading ? "..." : latestReport}</span>
          <span className="snapshot-card-sub">ACTIVE AUDIT MONTH</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">ACTIVE SECTORS</span>
          <span className="snapshot-card-val">{isLoading ? "..." : sectorsCount}</span>
          <span className="snapshot-card-sub">INFRASTRUCTURE DOMAINS</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">AGENCIES</span>
          <span className="snapshot-card-val">{isLoading ? "..." : agenciesCount}</span>
          <span className="snapshot-card-sub">EXECUTING BODIES</span>
        </div>

        <div className="portfolio-snapshot-card">
          <span className="snapshot-card-label">STATES / REGIONS</span>
          <span className="snapshot-card-val">{isLoading ? "..." : statesCount}</span>
          <span className="snapshot-card-sub">GEOGRAPHIC SCOPE</span>
        </div>
      </div>
    </section>
  );
};
