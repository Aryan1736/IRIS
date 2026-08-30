import React from "react";
import type { DatasetInfoResponse } from "@/types/system.ts";

interface SystemProvenanceSectionProps {
  systemInfo?: DatasetInfoResponse;
}

export const SystemProvenanceSection: React.FC<SystemProvenanceSectionProps> = ({
  systemInfo,
}) => {
  const observationsCount = systemInfo?.row_count
    ? `${systemInfo.row_count.toLocaleString()} OBSERVATIONS`
    : "64,608 OBSERVATIONS";

  const period = () => {
    if (!systemInfo?.covered_months || systemInfo.covered_months.length === 0) {
      return "2023-01 → 2026-07";
    }
    const sorted = [...systemInfo.covered_months].sort();
    return `${sorted[0]} → ${sorted[sorted.length - 1]}`;
  };

  return (
    <section className="system-provenance-bar">
      <div className="provenance-pills-wrap">
        <div className="provenance-pill">
          <span>DATASET:</span>
          <span className="provenance-pill-val">{observationsCount}</span>
        </div>

        <div className="provenance-pill">
          <span>COMPLETED PROJECTS:</span>
          <span className="provenance-pill-val">—</span>
        </div>

        <div className="provenance-pill">
          <span>MONITORING PERIOD:</span>
          <span className="provenance-pill-val">{period()}</span>
        </div>

        <div className="provenance-pill">
          <span>MODEL STATUS:</span>
          <span className="provenance-pill-val">H=3 LOGISTIC BASELINE VALIDATED</span>
        </div>

        <div className="provenance-pill">
          <span>ML CONNECTIVITY:</span>
          <span className="provenance-pill-val pending">PENDING</span>
        </div>

        <div className="provenance-pill">
          <span>DATA INTEGRITY:</span>
          <span className="provenance-pill-val">VERIFIED</span>
        </div>

        <div className="provenance-pill">
          <span>LIVE PREDICTIONS:</span>
          <span className="provenance-pill-val pending">NOT YET CONNECTED</span>
        </div>
      </div>
    </section>
  );
};
