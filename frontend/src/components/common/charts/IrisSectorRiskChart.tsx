import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import type { SectorSummary } from "@/types/risk.ts";
import { IrisChartTooltip } from "./IrisChartTooltip.tsx";

interface IrisSectorRiskChartProps {
  sectorSummary?: SectorSummary[];
  height?: number | string;
}

export const IrisSectorRiskChart: React.FC<IrisSectorRiskChartProps> = ({
  sectorSummary,
  height = 360,
}) => {
  const sectors = sectorSummary ? [...sectorSummary] : [];
  // Sort descending by mean_risk_probability
  sectors.sort((a, b) => b.mean_risk_probability - a.mean_risk_probability);

  if (sectors.length === 0) {
    return (
      <div style={{ padding: "32px", textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-muted)" }}>
        NO SECTOR RISK PROFILES REPORTED FOR CURRENT EVALUATION SCOPE.
      </div>
    );
  }

  const chartData = sectors.map((s, idx) => {
    const sectorName = s.sector || "UNKNOWN";
    return {
      sector: sectorName.length > 22 ? `${sectorName.slice(0, 20)}...` : sectorName,
      fullSector: sectorName,
      rank: idx + 1,
      meanRisk: Number((s.mean_risk_probability * 100).toFixed(1)),
      maxRisk: Number((s.highest_risk_probability * 100).toFixed(1)),
      projectCount: s.project_count,
    };
  });

  return (
    <div style={{ width: "100%", height, position: "relative" }} aria-label="Sector Risk Breakdown Chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 8, right: 32, left: 24, bottom: 8 }}
        >
          <CartesianGrid stroke="#E2E3DF" strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            domain={[0, 100]}
            stroke="#606460"
            tick={{ fill: "#606460", fontSize: 10, fontFamily: "var(--font-mono)" }}
            tickFormatter={(val: number) => `${val}%`}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
          />
          <YAxis
            type="category"
            dataKey="sector"
            stroke="#606460"
            tick={{ fill: "var(--color-primary-950)", fontSize: 11, fontFamily: "var(--font-sans)", fontWeight: 500 }}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
            width={130}
          />
          <Tooltip
            content={
              <IrisChartTooltip
                titlePrefix="SECTOR"
                customFormatter={(payload) => {
                  const entry = Array.isArray(payload) ? payload[0]?.payload : undefined;
                  if (!entry) return [];
                  return [
                    {
                      label: "SECTOR",
                      value: entry.fullSector,
                      color: "#FFFFFF",
                    },
                    {
                      label: "MONITORED PROJECTS",
                      value: `${entry.projectCount.toLocaleString()} PROJECTS`,
                      color: "#D1D4D1",
                    },
                    {
                      label: "MEAN RISK",
                      value: `${entry.meanRisk}%`,
                      color: entry.rank <= 2 ? "#BA1A1A" : "#1A3C2B",
                    },
                    {
                      label: "MAX OBSERVED RISK",
                      value: `${entry.maxRisk}%`,
                      color: "#A0A4A0",
                    },
                  ];
                }}
              />
            }
          />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              paddingBottom: "8px",
            }}
          />
          <Bar
            dataKey="meanRisk"
            name="Mean Risk %"
            fill="#1A3C2B"
            isAnimationActive={false}
          >
            {chartData.map((entry) => (
              <Cell
                key={`cell-mean-${entry.fullSector}`}
                fill={entry.rank <= 2 ? "#BA1A1A" : "#1A3C2B"}
              />
            ))}
          </Bar>
          <Bar
            dataKey="maxRisk"
            name="Max Observed Risk %"
            fill="#C4C6C2"
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
