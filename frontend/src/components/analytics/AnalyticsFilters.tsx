import React from "react";
import type { FilterOptionsResponse } from "@/types/project.ts";

export interface AnalyticsFilterState {
  sector: string;
  agency: string;
  state: string;
  ministry: string;
  report_month: string;
}

interface AnalyticsFiltersProps {
  filterOptions?: FilterOptionsResponse;
  filters: AnalyticsFilterState;
  onFilterChange: (filters: AnalyticsFilterState) => void;
}

export const AnalyticsFilters: React.FC<AnalyticsFiltersProps> = ({
  filterOptions,
  filters,
  onFilterChange,
}) => {
  const handleChange = (key: keyof AnalyticsFilterState, value: string) => {
    onFilterChange({
      ...filters,
      [key]: value,
    });
  };

  const sectors = filterOptions?.sectors || [];
  const agencies = filterOptions?.agencies || [];
  const states = filterOptions?.states || [];
  const ministries = filterOptions?.ministries || [];
  const reportMonths = filterOptions?.report_months || [];

  return (
    <div className="analytics-filters-bar" role="toolbar" aria-label="Analytics Filters">
      {/* Sector Filter */}
      <div className="analytics-filter-select-wrapper">
        <select
          aria-label="Filter by Sector"
          className="analytics-filter-select"
          value={filters.sector}
          onChange={(e) => handleChange("sector", e.target.value)}
        >
          <option value="">SECTOR (ALL)</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <span className="analytics-filter-icon">▼</span>
      </div>

      {/* Agency Filter */}
      <div className="analytics-filter-select-wrapper">
        <select
          aria-label="Filter by Agency"
          className="analytics-filter-select"
          value={filters.agency}
          onChange={(e) => handleChange("agency", e.target.value)}
        >
          <option value="">AGENCY (ALL)</option>
          {agencies.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <span className="analytics-filter-icon">▼</span>
      </div>

      {/* State Filter */}
      <div className="analytics-filter-select-wrapper">
        <select
          aria-label="Filter by State"
          className="analytics-filter-select"
          value={filters.state}
          onChange={(e) => handleChange("state", e.target.value)}
        >
          <option value="">STATE (ALL)</option>
          {states.map((st) => (
            <option key={st} value={st}>
              {st}
            </option>
          ))}
        </select>
        <span className="analytics-filter-icon">▼</span>
      </div>

      {/* Ministry Filter */}
      <div className="analytics-filter-select-wrapper">
        <select
          aria-label="Filter by Ministry"
          className="analytics-filter-select"
          value={filters.ministry}
          onChange={(e) => handleChange("ministry", e.target.value)}
        >
          <option value="">MINISTRY (ALL)</option>
          {ministries.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <span className="analytics-filter-icon">▼</span>
      </div>

      {/* Report Period Filter */}
      <div className="analytics-filter-select-wrapper">
        <select
          aria-label="Filter by Report Period"
          className="analytics-filter-select"
          value={filters.report_month}
          onChange={(e) => handleChange("report_month", e.target.value)}
        >
          <option value="">REPORT PERIOD (ALL)</option>
          {reportMonths.map((rm) => (
            <option key={rm} value={rm}>
              {rm}
            </option>
          ))}
        </select>
        <span className="analytics-filter-icon">▼</span>
      </div>

      <div style={{ marginLeft: "auto" }}>
        <span className="analytics-meta-label" style={{ fontSize: "9px" }}>
          SCOPE: CANONICAL TAXONOMIES
        </span>
      </div>
    </div>
  );
};
