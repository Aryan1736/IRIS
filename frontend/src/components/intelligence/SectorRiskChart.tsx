import React from "react";
import type { SectorSummary } from "@/types/risk.ts";
import { IrisSectorRiskChart } from "@/components/common/charts/IrisSectorRiskChart.tsx";

interface SectorRiskChartProps {
  sectorSummary?: SectorSummary[];
}

export const SectorRiskChart: React.FC<SectorRiskChartProps> = ({ sectorSummary }) => {
  const sectors = sectorSummary ? [...sectorSummary] : [];

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <div className="intelligence-section-title-lockup">
          <h2 className="intelligence-section-title">04. Risk by Sector</h2>
          <span className="intelligence-section-subtitle">
            RETURNED SECTOR RISK PROFILES ({sectors.length} MONITORED SECTORS)
          </span>
        </div>
        <span className="intelligence-section-subtitle">
          SORT: DESCENDING MEAN RISK
        </span>
      </div>

      <div className="intelligence-sector-card" style={{ background: "#FFFFFF", border: "1px solid var(--color-border-hairline)", padding: "16px 20px" }}>
        <IrisSectorRiskChart
          sectorSummary={sectorSummary}
          height={Math.max(280, Math.min(600, sectors.length * 42))}
        />

        <div style={{ paddingTop: "12px", borderTop: "1px solid var(--color-border-hairline)", marginTop: "12px" }}>
          <span style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--color-text-muted)", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            TAXONOMY AUDIT NOTE: SECTOR RISK METRICS REFLECT ACTIVE RECORD-LEVEL EVALUATIONS FROM CANONICAL MONITORED PROJECTS.
          </span>
        </div>
      </div>
    </section>
  );
};
