import React from "react";
import { Link } from "react-router-dom";
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
    : [];

  const agencies = filterOptions?.agencies && filterOptions.agencies.length > 0
    ? filterOptions.agencies.slice(0, 4)
    : [];

  const states = filterOptions?.states && filterOptions.states.length > 0
    ? filterOptions.states.filter((s) => !s.startsWith("Multi-States")).slice(0, 4)
    : [];

  return (
    <section className="dashboard-section">
      <div
        className="dashboard-section-header"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <div>
          <h2 className="dashboard-section-title">FROM PROJECTS TO PORTFOLIOS.</h2>
          <span className="dashboard-section-subtitle">ACTIVE MONITORED CATEGORIES</span>
        </div>
        <Link
          to="/projects"
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--color-primary-950)",
            textDecoration: "none",
            fontWeight: 600,
            transition: "opacity 150ms ease",
          }}
        >
          EXPLORE ALL PROJECTS →
        </Link>
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
            ) : sectors.length === 0 ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                DATA PENDING
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
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.85 }} />
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
            ) : agencies.length === 0 ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                DATA PENDING
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
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.85 }} />
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
            ) : states.length === 0 ? (
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-dim)" }}>
                DATA PENDING
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
                    <div className="progress-fill-primary" style={{ width: "100%", opacity: 0.85 }} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div style={{ paddingTop: "12px", borderTop: "1px solid var(--color-border-hairline)", marginTop: "16px" }}>
        <p
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--color-text-dim)",
            margin: 0,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          TAXONOMY AUDIT NOTE: LISTS DISPLAY DISTINCT AVAILABLE TAXONOMY OPTIONS, NOT PORTFOLIO FREQUENCY DISTRIBUTIONS.
        </p>
      </div>
    </section>
  );
};
