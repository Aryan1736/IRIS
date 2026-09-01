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
  LabelList,
} from "recharts";
import type { TopRiskProject, RiskRecord } from "@/types/risk.ts";
import { IrisChartTooltip } from "./IrisChartTooltip.tsx";

interface IrisTopRiskRankingChartProps {
  projects: TopRiskProject[];
  onSelectProject?: (project: TopRiskProject | RiskRecord) => void;
  height?: number | string;
}

export const IrisTopRiskRankingChart: React.FC<IrisTopRiskRankingChartProps> = ({
  projects,
  onSelectProject,
  height = 300,
}) => {
  if (!projects || projects.length === 0) {
    return null;
  }

  // Format data for vertical layout (horizontal bars) sorted by rank
  const chartData = projects.map((p) => ({
    code: p.project_code,
    name: p.project_name || p.project_code,
    rankNum: p.risk_rank,
    rank: `#${p.risk_rank}`,
    calibratedRisk: Number((p.risk_probability * 100).toFixed(1)),
    rawProbability: Number((p.raw_probability * 100).toFixed(1)),
    percentile: `TOP ${Math.max(0.1, 100 - p.risk_percentile * 100).toFixed(1)}%`,
    regime: p.regime,
    agency: p.agency || p.sector || "—",
    projectRef: p,
  }));

  return (
    <div style={{ width: "100%", height, position: "relative" }} aria-label="Top Risk Projects Ranking Chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 8, right: 48, left: 24, bottom: 8 }}
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
            dataKey="code"
            stroke="#606460"
            tick={{ fill: "var(--color-primary-950)", fontSize: 11, fontFamily: "var(--font-mono)", fontWeight: 600 }}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
            width={72}
          />
          <Tooltip
            content={
              <IrisChartTooltip
                titlePrefix="PROJECT"
                customFormatter={(payload) => {
                  const entry = Array.isArray(payload) ? payload[0]?.payload : undefined;
                  if (!entry) return [];
                  return [
                    {
                      label: "PROJECT NAME",
                      value: entry.name.length > 28 ? `${entry.name.slice(0, 26)}...` : entry.name,
                      color: "#FFFFFF",
                    },
                    {
                      label: "CALIBRATED RISK",
                      value: `${entry.calibratedRisk}%`,
                      color: entry.rankNum <= 3 ? "#BA1A1A" : "#1A3C2B",
                      subtext: `Portfolio Rank ${entry.rank}`,
                    },
                    {
                      label: "RAW PROBABILITY",
                      value: `${entry.rawProbability}%`,
                      color: "#D1D4D1",
                    },
                    {
                      label: "PERCENTILE",
                      value: entry.percentile,
                      color: "#A0A4A0",
                    },
                    {
                      label: "REGIME",
                      value: entry.regime,
                      color: "#A0A4A0",
                    },
                  ];
                }}
              />
            }
          />
          <Bar
            dataKey="calibratedRisk"
            name="Calibrated Risk"
            isAnimationActive={false}
            onClick={(entry) => {
              if (onSelectProject && entry?.projectRef) {
                onSelectProject(entry.projectRef);
              }
            }}
            cursor="pointer"
          >
            <LabelList
              dataKey="calibratedRisk"
              position="right"
              formatter={(val: number) => `${val}%`}
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                fontWeight: 700,
                fill: "var(--color-primary-950)",
              }}
            />
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.code}`}
                fill={entry.rankNum <= 3 ? "#BA1A1A" : "#1A3C2B"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
