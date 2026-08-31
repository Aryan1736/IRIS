import React from "react";
import type { DashboardOptionsResponse, Regime } from "@/types/risk.ts";

export interface IntelligenceFilterState {
  report_month: string;
  regime: Regime | "";
  sector: string;
  agency: string;
  state: string;
  ministry: string;
  search: string;
}

interface RiskFiltersProps {
  options?: DashboardOptionsResponse;
  filters: IntelligenceFilterState;
  onFilterChange: (filters: IntelligenceFilterState) => void;
}

export const RiskFilters: React.FC<RiskFiltersProps> = ({
  options,
  filters,
  onFilterChange,
}) => {
  const months = options?.report_months || [];
  const regimes = options?.regimes || [];
  const sectors = options?.sectors || [];
  const agencies = options?.agencies || [];
  const states = options?.states || [];
  const ministries = options?.ministries || [];

  const handleSelect = (key: keyof IntelligenceFilterState, value: string) => {
    onFilterChange({
      ...filters,
      [key]: value,
    });
  };

  return (
    <div className="intelligence-filters-bar" role="toolbar" aria-label="Risk Intelligence Filters">
      {/* Report Month Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-month-filter"
          name="report_month"
          aria-label="Evaluation Month"
          className="intelligence-filter-select"
          value={filters.report_month}
          onChange={(e) => handleSelect("report_month", e.target.value)}
        >
          {months.map((m) => (
            <option key={m} value={m}>
              EVAL MONTH: {m}
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* Regime Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-regime-filter"
          name="regime"
          aria-label="Regime Filter"
          className="intelligence-filter-select"
          value={filters.regime}
          onChange={(e) => handleSelect("regime", e.target.value as Regime | "")}
        >
          <option value="">REGIME (ALL)</option>
          {regimes.map((r) => (
            <option key={r} value={r}>
              {r} REGIME
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* Sector Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-sector-filter"
          name="sector"
          aria-label="Sector Filter"
          className="intelligence-filter-select"
          value={filters.sector}
          onChange={(e) => handleSelect("sector", e.target.value)}
        >
          <option value="">SECTOR (ALL)</option>
          {sectors.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* Agency Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-agency-filter"
          name="agency"
          aria-label="Agency Filter"
          className="intelligence-filter-select"
          value={filters.agency}
          onChange={(e) => handleSelect("agency", e.target.value)}
        >
          <option value="">AGENCY (ALL)</option>
          {agencies.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* State Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-state-filter"
          name="state"
          aria-label="State Filter"
          className="intelligence-filter-select"
          value={filters.state}
          onChange={(e) => handleSelect("state", e.target.value)}
        >
          <option value="">STATE (ALL)</option>
          {states.map((st) => (
            <option key={st} value={st}>
              {st}
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* Ministry Filter */}
      <div className="intelligence-filter-select-wrapper">
        <select
          id="risk-ministry-filter"
          name="ministry"
          aria-label="Ministry Filter"
          className="intelligence-filter-select"
          value={filters.ministry}
          onChange={(e) => handleSelect("ministry", e.target.value)}
        >
          <option value="">MINISTRY (ALL)</option>
          {ministries.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <span className="intelligence-filter-icon">▼</span>
      </div>

      {/* Search Input */}
      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px" }}>
        <input
          id="risk-search-input"
          name="search"
          type="text"
          aria-label="Search Risk Projects"
          placeholder="SEARCH PROJECT CODE / NAME..."
          className="intelligence-search-input"
          value={filters.search}
          onChange={(e) => handleSelect("search", e.target.value)}
        />
      </div>
    </div>
  );
};
