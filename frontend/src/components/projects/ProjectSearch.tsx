import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchFilterOptions } from "@/api/projects.ts";
import { Search, ChevronDown, X } from "lucide-react";
import type { FilterOptionsResponse } from "@/types/project.ts";

export interface Filters {
  search?: string;
  sector?: string;
  agency?: string;
  state?: string;
  ministry?: string;
  report_month?: string;
}

interface ProjectSearchProps {
  filters: Filters;
  onFilterChange: (filters: Filters) => void;
  options?: FilterOptionsResponse;
}

export const ProjectSearch: React.FC<ProjectSearchProps> = ({
  filters,
  onFilterChange,
  options: externalOptions,
}) => {
  const { data: fetchedOptions } = useQuery({
    queryKey: ["filterOptions"],
    queryFn: fetchFilterOptions,
    enabled: !externalOptions,
  });

  const options = externalOptions || fetchedOptions;

  const [searchInput, setSearchInput] = useState(filters.search || "");
  const filtersRef = React.useRef(filters);
  filtersRef.current = filters;

  // Sync external search filter changes to local input
  useEffect(() => {
    setSearchInput(filters.search || "");
  }, [filters.search]);

  // Debounce search input changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if ((searchInput || undefined) !== filtersRef.current.search) {
        onFilterChange({ ...filtersRef.current, search: searchInput || undefined });
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput, onFilterChange]);

  const handleChange = (key: keyof Filters, value: string) => {
    onFilterChange({ ...filters, [key]: value || undefined });
  };

  const handleClear = () => {
    setSearchInput("");
    onFilterChange({});
  };

  const handleClearField = (key: keyof Filters) => {
    if (key === "search") {
      setSearchInput("");
    }
    const updated = { ...filters };
    delete updated[key];
    onFilterChange(updated);
  };

  const hasActiveFilters = Boolean(
    filters.sector ||
    filters.agency ||
    filters.state ||
    filters.ministry ||
    filters.report_month ||
    filters.search
  );

  return (
    <section className="search-section" aria-label="Project Search and Filters">
      <div className="search-section-label">PROJECT SEARCH</div>

      {/* Main Search Input */}
      <div className="search-input-wrapper">
        <span className="search-input-icon">
          <Search size={18} />
        </span>
        <input
          id="project-search-input"
          name="search"
          aria-label="Search projects"
          className="search-input"
          placeholder="SEARCH PROJECT NAME, CODE, AGENCY, SECTOR..."
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        {searchInput && (
          <button
            type="button"
            className="search-clear-input-btn"
            onClick={() => {
              setSearchInput("");
              onFilterChange({ ...filters, search: undefined });
            }}
            aria-label="Clear search input"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Filters Command Strip */}
      <div className="filters-bar" role="toolbar" aria-label="Project Taxonomy Filters">
        <span className="filters-label">FILTERS:</span>

        {/* Sector Select */}
        <div className="filter-select-wrapper">
          <select
            id="project-sector-select"
            name="sector"
            aria-label="Filter by sector"
            className="filter-select"
            value={filters.sector || ""}
            onChange={(e) => handleChange("sector", e.target.value)}
          >
            <option value="">SECTOR (ALL)</option>
            {options?.sectors?.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <span className="filter-select-arrow">
            <ChevronDown size={13} />
          </span>
        </div>

        {/* Agency Select */}
        <div className="filter-select-wrapper">
          <select
            id="project-agency-select"
            name="agency"
            aria-label="Filter by agency"
            className="filter-select"
            value={filters.agency || ""}
            onChange={(e) => handleChange("agency", e.target.value)}
          >
            <option value="">AGENCY (ALL)</option>
            {options?.agencies?.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
          <span className="filter-select-arrow">
            <ChevronDown size={13} />
          </span>
        </div>

        {/* State Select */}
        <div className="filter-select-wrapper">
          <select
            id="project-state-select"
            name="state"
            aria-label="Filter by state"
            className="filter-select"
            value={filters.state || ""}
            onChange={(e) => handleChange("state", e.target.value)}
          >
            <option value="">STATE / REGION (ALL)</option>
            {options?.states?.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
          <span className="filter-select-arrow">
            <ChevronDown size={13} />
          </span>
        </div>

        {/* Ministry Select */}
        <div className="filter-select-wrapper">
          <select
            id="project-ministry-select"
            name="ministry"
            aria-label="Filter by ministry"
            className="filter-select"
            value={filters.ministry || ""}
            onChange={(e) => handleChange("ministry", e.target.value)}
          >
            <option value="">MINISTRY (ALL)</option>
            {options?.ministries?.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <span className="filter-select-arrow">
            <ChevronDown size={13} />
          </span>
        </div>

        {/* Report Period Select */}
        <div className="filter-select-wrapper">
          <select
            id="project-report-month-select"
            name="report_month"
            aria-label="Filter by report period"
            className="filter-select"
            value={filters.report_month || ""}
            onChange={(e) => handleChange("report_month", e.target.value)}
          >
            <option value="">REPORT PERIOD (ALL)</option>
            {options?.report_months?.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <span className="filter-select-arrow">
            <ChevronDown size={13} />
          </span>
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <button
            type="button"
            className="clear-filters-btn"
            onClick={handleClear}
          >
            CLEAR FILTERS
          </button>
        )}
      </div>

      {/* Active Filter Tags Row */}
      {hasActiveFilters && (
        <div className="active-filters-row" aria-label="Active Filter Tags">
          <span className="active-filters-title">ACTIVE CRITERIA:</span>
          {filters.search && (
            <span className="active-filter-tag">
              SEARCH: <strong>"{filters.search}"</strong>
              <button
                type="button"
                onClick={() => handleClearField("search")}
                aria-label="Remove search filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
          {filters.sector && (
            <span className="active-filter-tag">
              SECTOR: <strong>{filters.sector}</strong>
              <button
                type="button"
                onClick={() => handleClearField("sector")}
                aria-label="Remove sector filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
          {filters.agency && (
            <span className="active-filter-tag">
              AGENCY: <strong>{filters.agency}</strong>
              <button
                type="button"
                onClick={() => handleClearField("agency")}
                aria-label="Remove agency filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
          {filters.state && (
            <span className="active-filter-tag">
              STATE: <strong>{filters.state}</strong>
              <button
                type="button"
                onClick={() => handleClearField("state")}
                aria-label="Remove state filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
          {filters.ministry && (
            <span className="active-filter-tag">
              MINISTRY: <strong>{filters.ministry}</strong>
              <button
                type="button"
                onClick={() => handleClearField("ministry")}
                aria-label="Remove ministry filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
          {filters.report_month && (
            <span className="active-filter-tag">
              CYCLE: <strong>{filters.report_month}</strong>
              <button
                type="button"
                onClick={() => handleClearField("report_month")}
                aria-label="Remove report month filter"
                className="active-filter-remove"
              >
                ×
              </button>
            </span>
          )}
        </div>
      )}
    </section>
  );
};
