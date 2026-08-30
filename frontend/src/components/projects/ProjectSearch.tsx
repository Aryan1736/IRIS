import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchFilterOptions } from "@/api/projects.ts";
import { Search, ChevronDown } from "lucide-react";

export interface Filters {
  search?: string;
  sector?: string;
  agency?: string;
  state?: string;
  report_month?: string;
}

interface ProjectSearchProps {
  filters: Filters;
  onFilterChange: (filters: Filters) => void;
}

export const ProjectSearch: React.FC<ProjectSearchProps> = ({ filters, onFilterChange }) => {
  const { data: options } = useQuery({
    queryKey: ["filterOptions"],
    queryFn: fetchFilterOptions,
  });

  const [searchInput, setSearchInput] = useState(filters.search || "");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      onFilterChange({ ...filters, search: searchInput || undefined });
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleChange = (key: keyof Filters, value: string) => {
    onFilterChange({ ...filters, [key]: value || undefined });
  };

  const handleClear = () => {
    setSearchInput("");
    onFilterChange({});
  };

  const hasActiveFilters = Boolean(
    filters.sector || filters.agency || filters.state || filters.report_month || filters.search
  );

  return (
    <section className="search-section">
      <div className="search-section-label">PROJECT SEARCH</div>

      {/* Main Search Input */}
      <div className="search-input-wrapper">
        <span className="search-input-icon">
          <Search size={18} />
        </span>
        <input
          className="search-input"
          placeholder="Search project name, project code, agency, sector..."
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
      </div>

      {/* Filters Bar */}
      <div className="filters-bar">
        <span className="filters-label">FILTERS:</span>

        {/* Sector Select */}
        <div className="filter-select-wrapper">
          <select
            className="filter-select"
            value={filters.sector || ""}
            onChange={(e) => handleChange("sector", e.target.value)}
          >
            <option value="">SECTOR</option>
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
            className="filter-select"
            value={filters.agency || ""}
            onChange={(e) => handleChange("agency", e.target.value)}
          >
            <option value="">AGENCY</option>
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
            className="filter-select"
            value={filters.state || ""}
            onChange={(e) => handleChange("state", e.target.value)}
          >
            <option value="">STATE</option>
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

        {/* Report Period Select */}
        <div className="filter-select-wrapper">
          <select
            className="filter-select"
            value={filters.report_month || ""}
            onChange={(e) => handleChange("report_month", e.target.value)}
          >
            <option value="">REPORT PERIOD</option>
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
    </section>
  );
};
