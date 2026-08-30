import React from "react";
import type { FilterOptionsResponse } from "@/types/project.ts";

interface PortfolioCompositionSectionProps {
  filterOptions?: FilterOptionsResponse;
  isLoading?: boolean;
}

export const PortfolioCompositionSection: React.FC<PortfolioCompositionSectionProps> = ({
  filterOptions,
  isLoading = false,
}) => {
  const sectors = filterOptions?.sectors && filterOptions.sectors.length > 0
    ? filterOptions.sectors.slice(0, 4)
    : ["ROAD TRANSPORT & HIGHWAYS", "RAILWAYS", "POWER", "PETROLEUM"];

  const agencies = filterOptions?.agencies && filterOptions.agencies.length > 0
    ? filterOptions.agencies.slice(0, 4)
    : ["NHAI", "RVNL", "PGCIL", "NTPC"];

  const states = filterOptions?.states && filterOptions.states.length > 0
    ? filterOptions.states.filter((s) => !s.startsWith("Multi-States")).slice(0, 4)
    : ["MAHARASHTRA", "UTTAR PRADESH", "GUJARAT", "MADHYA PRADESH"];

  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">FROM PROJECTS TO PORTFOLIOS.</h2>
        <span className="dashboard-section-subtitle">ACTIVE MONITORED CATEGORIES</span>
      </div>

      <div className="dashboard-grid-3-col">
        {/* Sector Card */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">SECTOR</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
              {filterOptions?.sectors?.length ? `${filterOptions.sectors.length} MONITORED` : "PORTFOLIO"}
            </span>
          </div>

          <div className="progress-distribution-list">
            {isLoading ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                LOADING SECTORS...
              </span>
            ) : (
              sectors.map((sec) => (
                <div key={sec} className="progress-distribution-item">
                  <div className="progress-item-header">
                    <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {sec}
                    </span>
                    <span style={{ color: "var(--color-text-dim)", fontSize: "10px" }}>MONITORED</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.8 }} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Agency Card */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">AGENCY</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
              {filterOptions?.agencies?.length ? `${filterOptions.agencies.length} AGENCIES` : "IMPLEMENTING"}
            </span>
          </div>

          <div className="progress-distribution-list">
            {isLoading ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                LOADING AGENCIES...
              </span>
            ) : (
              agencies.map((agency) => (
                <div key={agency} className="progress-distribution-item">
                  <div className="progress-item-header">
                    <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {agency}
                    </span>
                    <span style={{ color: "var(--color-text-dim)", fontSize: "10px" }}>MONITORED</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.8 }} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* State Card */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">STATE</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)" }}>
              {filterOptions?.states?.length ? `${filterOptions.states.length} REGIONS` : "COVERAGE"}
            </span>
          </div>

          <div className="progress-distribution-list">
            {isLoading ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                LOADING STATES...
              </span>
            ) : (
              states.map((state) => (
                <div key={state} className="progress-distribution-item">
                  <div className="progress-item-header">
                    <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {state}
                    </span>
                    <span style={{ color: "var(--color-text-dim)", fontSize: "10px" }}>MONITORED</span>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.8 }} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
