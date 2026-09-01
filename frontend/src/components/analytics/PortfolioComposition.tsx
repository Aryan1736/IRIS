import React from "react";
import type { FilterOptionsResponse } from "@/types/project.ts";

interface PortfolioCompositionProps {
  filterOptions?: FilterOptionsResponse;
}

export const PortfolioComposition: React.FC<PortfolioCompositionProps> = ({
  filterOptions,
}) => {
  const sectors = filterOptions?.sectors || [];
  const agencies = filterOptions?.agencies || [];
  const states = filterOptions?.states || [];

  return (
    <section className="analytics-section">
      <div className="analytics-section-header">
        <h2 className="analytics-section-title">04. Portfolio Composition</h2>
        <span className="analytics-section-subtitle">DISTINCT MONITORED TAXONOMIES</span>
      </div>

      <div className="analytics-grid-3col">
        {/* Sectors Column */}
        <div className="analytics-composition-card">
          <div className="analytics-composition-header">
            <span className="analytics-composition-title">Sector</span>
            <span className="analytics-composition-count">{sectors.length} DISTINCT OPTIONS</span>
          </div>

          <div className="analytics-category-list">
            {sectors.length === 0 ? (
              <div className="analytics-category-item">—</div>
            ) : (
              sectors.map((sec) => (
                <div key={sec} className="analytics-category-item">
                  <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {sec}
                  </span>
                  <span className="analytics-category-tag">INDEXED</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Agencies Column */}
        <div className="analytics-composition-card">
          <div className="analytics-composition-header">
            <span className="analytics-composition-title">Agency</span>
            <span className="analytics-composition-count">{agencies.length} DISTINCT OPTIONS</span>
          </div>

          <div className="analytics-category-list">
            {agencies.length === 0 ? (
              <div className="analytics-category-item">—</div>
            ) : (
              agencies.map((ag) => (
                <div key={ag} className="analytics-category-item">
                  <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {ag}
                  </span>
                  <span className="analytics-category-tag">INDEXED</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* States Column */}
        <div className="analytics-composition-card">
          <div className="analytics-composition-header">
            <span className="analytics-composition-title">State / Region</span>
            <span className="analytics-composition-count">{states.length} DISTINCT OPTIONS</span>
          </div>

          <div className="analytics-category-list">
            {states.length === 0 ? (
              <div className="analytics-category-item">—</div>
            ) : (
              states.map((st) => (
                <div key={st} className="analytics-category-item">
                  <span style={{ maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {st}
                  </span>
                  <span className="analytics-category-tag">INDEXED</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div style={{ paddingTop: "12px", borderTop: "1px solid var(--color-border-hairline)", marginTop: "8px" }}>
        <span className="analytics-metric-subtext">
          TAXONOMY AUDIT NOTE: LISTS DISPLAY DISTINCT AVAILABLE TAXONOMY FILTER OPTIONS FROM CANONICAL RECORDS, NOT PORTFOLIO FREQUENCY DISTRIBUTIONS.
        </span>
      </div>
    </section>
  );
};
