import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDatasetInfo } from "@/api/system.ts";
import { fetchFilterOptions } from "@/api/projects.ts";
import { DashboardIntro } from "@/components/dashboard/DashboardIntro.tsx";
import { PortfolioMetricsGrid } from "@/components/dashboard/PortfolioMetricsGrid.tsx";
import { ActivityTimelineSection } from "@/components/dashboard/ActivityTimelineSection.tsx";
import { ScheduleIntelligenceSection } from "@/components/dashboard/ScheduleIntelligenceSection.tsx";
import { CostIntelligenceSection } from "@/components/dashboard/CostIntelligenceSection.tsx";
import { EarlyWarningSection } from "@/components/dashboard/EarlyWarningSection.tsx";
import { PortfolioCompositionSection } from "@/components/dashboard/PortfolioCompositionSection.tsx";
import { SystemProvenanceSection } from "@/components/dashboard/SystemProvenanceSection.tsx";
import { ShieldCheck } from "lucide-react";
import { usePageEnter } from "@/lib/motion/useMotion.ts";

export const DashboardPage: React.FC = () => {
  const containerRef = usePageEnter<HTMLDivElement>();

  const { data: systemInfo } = useQuery({
    queryKey: ["systemInfo"],
    queryFn: fetchDatasetInfo,
  });

  const { data: filterOptions, isLoading: isFilterOptionsLoading } = useQuery({
    queryKey: ["filterOptions"],
    queryFn: fetchFilterOptions,
  });

  return (
    <div style={{ minHeight: "calc(100vh - 64px)", display: "flex", flexDirection: "column", width: "100%" }}>
      <div ref={containerRef} className="dashboard-container">
        {/* Intro */}
        <DashboardIntro lastUpdated={systemInfo?.ingested_at ? systemInfo.ingested_at.slice(0, 10) : "2026-08-29"} />

        {/* 6-Cell Metrics Bar */}
        <PortfolioMetricsGrid systemInfo={systemInfo} />

        {/* Section 01 — Portfolio Movement */}
        <ActivityTimelineSection systemInfo={systemInfo} />

        {/* Section 02 — Schedule Intelligence */}
        <ScheduleIntelligenceSection />

        {/* Section 03 — Cost Intelligence */}
        <CostIntelligenceSection />

        {/* Section 04 — Early Warning */}
        <EarlyWarningSection />

        {/* Section 05 — Portfolio Composition */}
        <PortfolioCompositionSection
          filterOptions={filterOptions}
          isLoading={isFilterOptionsLoading}
        />

        {/* Section 06 — Data / Model Status */}
        <SystemProvenanceSection systemInfo={systemInfo} />
      </div>

      {/* Bottom Data Provenance Strip */}
      <footer className="provenance-strip">
        <div className="provenance-strip-inner">
          <div className="provenance-metrics">
            <span>© 2026 IRIS INFRASTRUCTURE MONITORING</span>
            <span>PROVENANCE: PAIMANA CORE</span>
            <span>DATA COVERAGE: {systemInfo?.covered_months && systemInfo.covered_months.length > 0 ? `${systemInfo.covered_months.length} MONTHS` : "2023-01 → 2026-07"}</span>
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
