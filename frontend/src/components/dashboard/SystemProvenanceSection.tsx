import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { DatasetInfoResponse } from "@/types/system.ts";
import { fetchModelInfo } from "@/api/risk.ts";

interface SystemProvenanceSectionProps {
  systemInfo?: DatasetInfoResponse;
}

export const SystemProvenanceSection: React.FC<SystemProvenanceSectionProps> = ({
  systemInfo,
}) => {
  const { data: modelInfo } = useQuery({
    queryKey: ["modelInfo"],
    queryFn: fetchModelInfo,
    staleTime: 10 * 60 * 1000,
  });

  const observationsCount = systemInfo?.row_count != null
    ? `${systemInfo.row_count.toLocaleString()} OBSERVATIONS`
    : "DATA PENDING";

  const period = () => {
    if (!systemInfo?.covered_months || systemInfo.covered_months.length === 0) {
      return "DATA PENDING";
    }
    const sorted = [...systemInfo.covered_months].sort();
    return `${sorted[0]} → ${sorted[sorted.length - 1]}`;
  };

  const isModelReady = modelInfo?.status === "READY";

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
          <span className="provenance-pill-val">
            {isModelReady ? "H=3 LOGISTIC / TREESHAP READY" : "H=3 LOGISTIC BASELINE"}
          </span>
        </div>

        <div className="provenance-pill">
          <span>ML CONNECTIVITY:</span>
          <span className={`provenance-pill-val ${isModelReady ? "" : "pending"}`}>
            {isModelReady ? "LIVE SERVING READY" : "PENDING"}
          </span>
        </div>

        <div className="provenance-pill">
          <span>DATASET STATUS:</span>
          <span className="provenance-pill-val">
            {systemInfo?.status || "ACTIVE"}
          </span>
        </div>

        <div className="provenance-pill">
          <span>LIVE PREDICTIONS:</span>
          <span className={`provenance-pill-val ${isModelReady ? "" : "pending"}`}>
            {isModelReady ? "ACTIVE SERVING" : "NOT YET CONNECTED"}
          </span>
        </div>
      </div>
    </section>
  );
};
