import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { DatasetInfoResponse } from "@/types/system.ts";
import type { AnalyticsFilterState } from "./AnalyticsFilters.tsx";
import { fetchMonthlyObservations } from "@/api/projects.ts";
import { MonthlyActivityChart } from "@/components/dashboard/MonthlyActivityChart.tsx";

interface ActivityAnalyticsProps {
  datasetInfo?: DatasetInfoResponse;
  filters?: AnalyticsFilterState;
}

export const ActivityAnalytics: React.FC<ActivityAnalyticsProps> = ({ datasetInfo, filters }) => {
  const hasActiveFilters = Boolean(
    filters?.sector || filters?.agency || filters?.state || filters?.ministry
  );

  const months: string[] = datasetInfo?.covered_months || [];
  const startMonth = months.length > 0 ? months[0] : "—";
  const endMonth = months.length > 0 ? months[months.length - 1] : "—";

  const { data: monthlyData, isLoading: isMonthlyLoading } = useQuery({
    queryKey: ["monthlyObservationCounts", months, filters?.sector, filters?.agency, filters?.state, filters?.ministry],
    queryFn: () =>
      fetchMonthlyObservations(months, {
        sector: filters?.sector,
        agency: filters?.agency,
        state: filters?.state,
        ministry: filters?.ministry,
      }),
    enabled: months.length > 0,
    staleTime: 10 * 60 * 1000,
  });

  const filteredTotalObs = monthlyData
    ? monthlyData.reduce((acc, curr) => acc + curr.observations, 0)
    : 0;

  const observationsDisplay = hasActiveFilters
    ? filteredTotalObs.toLocaleString()
    : datasetInfo?.row_count != null && datasetInfo.row_count > 0
    ? datasetInfo.row_count.toLocaleString()
    : "—";

  const projectsDisplay = hasActiveFilters
    ? "FILTERED SCOPE"
    : datasetInfo?.unique_projects_count != null
    ? datasetInfo.unique_projects_count.toLocaleString()
    : "—";

  const monitoredMonthsCount = months.length > 0 ? months.length : "—";

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <div className="analytics-section-title-lockup">
          <h2 className="analytics-section-title">01. Portfolio Activity Over Time</h2>
          <span className="analytics-section-subtitle">
            {hasActiveFilters ? "FILTERED OBSERVATIONS & COVERAGE" : "LONGITUDINAL OBSERVATIONS & COVERAGE"}
          </span>
        </div>
        <span className="analytics-section-subtitle">
          {hasActiveFilters ? "TAXONOMY FILTER ACTIVE" : "ALL SECTORS & AGENCIES"}
        </span>
      </div>

      <div className="analytics-grid-2col">
        {/* Left: Real Interactive Monthly Chart */}
        <div className="analytics-canvas-box" style={{ padding: "16px" }}>
          <MonthlyActivityChart data={monthlyData || []} isLoading={isMonthlyLoading} />

          <div className="analytics-canvas-dates" style={{ marginTop: "8px", borderTop: "1px solid var(--color-border-hairline)", paddingTop: "8px" }}>
            <span>CADENCE START: {startMonth}</span>
            <span>LATEST CADENCE: {endMonth}</span>
          </div>
        </div>

        {/* Right: Metrics Sidebar */}
        <div className="analytics-metrics-sidebar">
          <div className="analytics-metric-cell">
            <div className="analytics-metric-large-val">{observationsDisplay}</div>
            <div className="analytics-metric-label">
              {hasActiveFilters ? "FILTERED OBSERVATIONS" : "OBSERVATIONS"}
            </div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-metric-large-val">{projectsDisplay}</div>
            <div className="analytics-metric-label">PROJECTS</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-metric-medium-val">{monitoredMonthsCount}</div>
            <div className="analytics-metric-label">MONITORED MONTHS</div>
          </div>

          <div className="analytics-metric-cell">
            <div className="analytics-data-pending-badge">DATA PENDING</div>
            <div className="analytics-metric-label">COMPLETED PROJECTS</div>
          </div>
        </div>
      </div>
    </section>
  );
};
