import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchModelInfo,
  fetchRiskOptions,
  fetchRiskProjects,
  fetchRiskSummary,
} from "@/api/risk.ts";
import type { RiskRecord, TopRiskProject } from "@/types/risk.ts";
import { IntelligenceIntro } from "@/components/intelligence/IntelligenceIntro.tsx";
import {
  RiskFilters,
  type IntelligenceFilterState,
} from "@/components/intelligence/RiskFilters.tsx";
import { PortfolioRiskOverview } from "@/components/intelligence/PortfolioRiskOverview.tsx";
import { RiskProjectTable } from "@/components/intelligence/RiskProjectTable.tsx";
import { RiskDistribution } from "@/components/intelligence/RiskDistribution.tsx";
import { SectorRiskChart } from "@/components/intelligence/SectorRiskChart.tsx";
import { RegimeIntelligence } from "@/components/intelligence/RegimeIntelligence.tsx";
import { RiskDriverIntelligence } from "@/components/intelligence/RiskDriverIntelligence.tsx";
import { ModelGovernance } from "@/components/intelligence/ModelGovernance.tsx";
import { WhatTheModelKnows } from "@/components/intelligence/WhatTheModelKnows.tsx";
import { IntelligenceAuditTrail } from "@/components/intelligence/IntelligenceAuditTrail.tsx";
import { RiskDetailDrawer } from "@/components/intelligence/RiskDetailDrawer.tsx";
import { usePageEnter } from "@/lib/motion/useMotion.ts";

export const IntelligencePage: React.FC = () => {
  const containerRef = usePageEnter<HTMLDivElement>();
  const [filters, setFilters] = useState<IntelligenceFilterState>({
    report_month: "",
    regime: "",
    sector: "",
    agency: "",
    state: "",
    ministry: "",
    search: "",
  });

  const [page, setPage] = useState(1);
  const [selectedProject, setSelectedProject] = useState<RiskRecord | TopRiskProject | null>(null);

  // 1. Fetch Risk Dashboard Options
  const { data: optionsData } = useQuery({
    queryKey: ["riskOptions"],
    queryFn: () => fetchRiskOptions(),
    staleTime: 5 * 60 * 1000,
  });

  // Default report month sync
  useEffect(() => {
    if (optionsData?.default_report_month && !filters.report_month) {
      setFilters((prev) => ({
        ...prev,
        report_month: optionsData.default_report_month,
      }));
    }
  }, [optionsData, filters.report_month]);

  const activeMonth = filters.report_month || optionsData?.default_report_month || "2026-04";

  // 2. Fetch Model Governance Info
  const { data: modelInfoData } = useQuery({
    queryKey: ["modelInfo"],
    queryFn: () => fetchModelInfo(),
    staleTime: 10 * 60 * 1000,
  });

  // 3. Fetch Portfolio Risk Summary
  const { data: summaryData } = useQuery({
    queryKey: [
      "riskSummary",
      activeMonth,
      filters.regime,
      filters.sector,
      filters.agency,
      filters.state,
      filters.ministry,
      filters.search,
    ],
    queryFn: () =>
      fetchRiskSummary({
        report_month: activeMonth,
        regime: filters.regime || undefined,
        sector: filters.sector || undefined,
        agency: filters.agency || undefined,
        state: filters.state || undefined,
        ministry: filters.ministry || undefined,
        search: filters.search || undefined,
        top_n: 10,
      }),
    enabled: !!activeMonth,
  });

  // 4. Fetch Ranked Projects List
  const { data: projectsData, isLoading: projectsLoading } = useQuery({
    queryKey: [
      "riskProjects",
      activeMonth,
      page,
      filters.regime,
      filters.sector,
      filters.agency,
      filters.state,
      filters.ministry,
      filters.search,
    ],
    queryFn: () =>
      fetchRiskProjects({
        report_month: activeMonth,
        page,
        page_size: 25,
        regime: filters.regime || undefined,
        sector: filters.sector || undefined,
        agency: filters.agency || undefined,
        state: filters.state || undefined,
        ministry: filters.ministry || undefined,
        search: filters.search || undefined,
      }),
    enabled: !!activeMonth,
  });

  const handleFilterChange = (newFilters: IntelligenceFilterState) => {
    setFilters(newFilters);
    setPage(1);
  };

  return (
    <div ref={containerRef} className="intelligence-container">
      {/* Intro & Telemetry */}
      <IntelligenceIntro
        modelInfo={modelInfoData}
        reportMonth={activeMonth}
      />

      {/* Filter Toolbar */}
      <RiskFilters
        options={optionsData}
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      {/* Section 01: Portfolio Risk Overview (Quantile Probability Band + KPI Strip) */}
      <PortfolioRiskOverview summary={summaryData} />

      {/* Section 02: Highest-Risk Projects (Top Risk Bar Ranking + Redesigned Table) */}
      <RiskProjectTable
        topRiskProjects={summaryData?.top_risk_projects}
        data={projectsData}
        isLoading={projectsLoading}
        page={page}
        pageSize={25}
        onPageChange={setPage}
        onSelectProject={setSelectedProject}
      />

      {/* Section 03: Model Output Distribution (Quantile Summary) */}
      <RiskDistribution
        distribution={summaryData?.score_distribution}
        reportMonth={activeMonth}
      />

      {/* Section 04: Risk by Sector (Horizontal Bar Chart) */}
      <SectorRiskChart sectorSummary={summaryData?.sector_summary} />

      {/* Section 05: Risk by Regime (Dual-Regime Architecture) */}
      <RegimeIntelligence summary={summaryData} />

      {/* Section 06: Risk Driver Intelligence (Diverging Signed Margin Architecture) */}
      <RiskDriverIntelligence />

      {/* Section 08 & 09: Model Governance & Feature Architecture */}
      <div className="intelligence-gov-grid">
        <ModelGovernance modelInfo={modelInfoData} />
        <WhatTheModelKnows />
      </div>

      {/* Section 10: Model Status / Audit Trail */}
      <IntelligenceAuditTrail modelInfo={modelInfoData} />

      {/* Section 07: Project Inspection Console Drawer */}
      {selectedProject && (
        <RiskDetailDrawer
          record={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  );
};
