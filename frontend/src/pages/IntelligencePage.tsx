import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchModelInfo,
  fetchRiskOptions,
  fetchRiskProjects,
  fetchRiskSummary,
} from "@/api/risk.ts";
import type { RiskRecord } from "@/types/risk.ts";
import {
  IntelligenceIntro,
} from "@/components/intelligence/IntelligenceIntro.tsx";
import {
  RiskFilters,
  type IntelligenceFilterState,
} from "@/components/intelligence/RiskFilters.tsx";
import { RiskOverviewCards } from "@/components/intelligence/RiskOverviewCards.tsx";
import { RiskProjectTable } from "@/components/intelligence/RiskProjectTable.tsx";
import { RiskDistribution } from "@/components/intelligence/RiskDistribution.tsx";
import { RegimeIntelligence } from "@/components/intelligence/RegimeIntelligence.tsx";
import { ModelGovernance } from "@/components/intelligence/ModelGovernance.tsx";
import { WhatTheModelKnows } from "@/components/intelligence/WhatTheModelKnows.tsx";
import { IntelligenceAuditTrail } from "@/components/intelligence/IntelligenceAuditTrail.tsx";
import { RiskDetailDrawer } from "@/components/intelligence/RiskDetailDrawer.tsx";

export const IntelligencePage: React.FC = () => {
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
  const [selectedProject, setSelectedProject] = useState<RiskRecord | null>(null);

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
    <div className="intelligence-container">
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

      {/* Section 01: Portfolio Risk Overview */}
      <RiskOverviewCards summary={summaryData} />

      {/* Section 02: Ranked Projects Requiring Attention */}
      <RiskProjectTable
        data={projectsData}
        isLoading={projectsLoading}
        page={page}
        pageSize={25}
        onPageChange={setPage}
        onSelectProject={setSelectedProject}
      />

      {/* Section 03: Model Output Distribution */}
      <RiskDistribution
        distribution={summaryData?.score_distribution}
        reportMonth={activeMonth}
      />

      {/* Section 04: Regime Intelligence & Sector Risk */}
      <RegimeIntelligence summary={summaryData} />

      {/* Section 05 & 06: Model Governance & Feature Architecture */}
      <div className="intelligence-gov-grid">
        <ModelGovernance modelInfo={modelInfoData} />
        <WhatTheModelKnows />
      </div>

      {/* Section 07: Model Status / Audit Trail */}
      <IntelligenceAuditTrail modelInfo={modelInfoData} />

      {/* Inspection Drawer */}
      {selectedProject && (
        <RiskDetailDrawer
          record={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  );
};
