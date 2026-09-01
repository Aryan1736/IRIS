import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDatasetInfo } from "@/api/system.ts";
import { fetchFilterOptions } from "@/api/projects.ts";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner.tsx";
import { Card } from "@/components/ui/Card.tsx";
import { Button } from "@/components/ui/Button.tsx";
import { TechnicalLabel } from "@/components/ui/TechnicalLabel.tsx";
import { AnalyticsIntro } from "@/components/analytics/AnalyticsIntro.tsx";
import { AnalyticsFilters, type AnalyticsFilterState } from "@/components/analytics/AnalyticsFilters.tsx";
import { ActivityAnalytics } from "@/components/analytics/ActivityAnalytics.tsx";
import { ScheduleAnalytics } from "@/components/analytics/ScheduleAnalytics.tsx";
import { CostAnalytics } from "@/components/analytics/CostAnalytics.tsx";
import { PortfolioComposition } from "@/components/analytics/PortfolioComposition.tsx";
import { ProgressAnalytics } from "@/components/analytics/ProgressAnalytics.tsx";
import { CompletionAnalytics } from "@/components/analytics/CompletionAnalytics.tsx";
import { AnalyticsDataProfile } from "@/components/analytics/AnalyticsDataProfile.tsx";
import { usePageEnter } from "@/lib/motion/useMotion.ts";

export const AnalyticsPage: React.FC = () => {
  const containerRef = usePageEnter<HTMLDivElement>();
  const [filters, setFilters] = useState<AnalyticsFilterState>({
    sector: "",
    agency: "",
    state: "",
    ministry: "",
    report_month: "",
  });

  const {
    data: datasetInfo,
    isLoading: isDatasetLoading,
    isError: isDatasetError,
    error: datasetError,
    refetch: refetchDataset,
  } = useQuery({
    queryKey: ["dataset-info"],
    queryFn: fetchDatasetInfo,
  });

  const {
    data: filterOptions,
    isLoading: isFiltersLoading,
  } = useQuery({
    queryKey: ["filter-options"],
    queryFn: fetchFilterOptions,
  });

  if (isDatasetLoading && isFiltersLoading) {
    return (
      <div className="analytics-container">
        <div style={{ padding: "80px 0", display: "flex", justifyContent: "center" }}>
          <LoadingSpinner size="lg" label="CONNECTING TO IRIS PORTFOLIO ANALYTICS..." />
        </div>
      </div>
    );
  }

  if (isDatasetError) {
    return (
      <div className="analytics-container">
        <div style={{ maxWidth: "600px", margin: "60px auto" }}>
          <TechnicalLabel label="SERVICE FAULT" sublabel="ANALYTICS PIPELINE" />
          <Card
            style={{ marginTop: "16px" }}
            padding="lg"
            title="Analytics Service Unavailable"
            subtitle="DATASET METADATA RETRIEVAL FAILED"
          >
            <p
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "var(--font-size-base)",
                color: "var(--color-text-variant)",
                lineHeight: 1.6,
                marginBottom: "24px",
              }}
            >
              {datasetError instanceof Error ? datasetError.message : "Failed to load dataset metadata."}
            </p>
            <Button variant="primary" size="sm" onClick={() => refetchDataset()}>
              RETRY CONNECTION
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="analytics-container">
      {/* Intro & Telemetry */}
      <AnalyticsIntro datasetInfo={datasetInfo} />

      {/* Filter Bar */}
      <AnalyticsFilters
        filterOptions={filterOptions}
        filters={filters}
        onFilterChange={setFilters}
      />

      {/* 01. Portfolio Activity Over Time */}
      <ActivityAnalytics datasetInfo={datasetInfo} filters={filters} />

      {/* 02. Where Schedules Move */}
      <ScheduleAnalytics datasetInfo={datasetInfo} />

      {/* 03. Follow the Money */}
      <CostAnalytics datasetInfo={datasetInfo} />

      {/* 04. Portfolio Composition */}
      <PortfolioComposition filterOptions={filterOptions} />

      {/* 05. Project Progress */}
      <ProgressAnalytics datasetInfo={datasetInfo} />

      {/* 06. Completion Movement */}
      <CompletionAnalytics datasetInfo={datasetInfo} />

      {/* 07. Observations / Data Profile */}
      <AnalyticsDataProfile datasetInfo={datasetInfo} />
    </div>
  );
};
