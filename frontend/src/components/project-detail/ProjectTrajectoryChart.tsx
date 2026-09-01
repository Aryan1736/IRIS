import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import type { ProjectTrajectoryPoint } from "@/types/project.ts";
import { ChartTooltip } from "./ChartTooltip.tsx";

export interface ProjectTrajectoryChartProps {
  observations: ProjectTrajectoryPoint[];
}

export const ProjectTrajectoryChart: React.FC<ProjectTrajectoryChartProps> = ({
  observations,
}) => {
  const data = observations || [];

  const hasValidProgress = data.some(
    (d) => d.physical_progress !== null && d.physical_progress !== undefined
  );

  if (data.length === 0 || !hasValidProgress) {
    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
          fontSize: "11px",
          color: "var(--color-text-dim, #5F5E5C)",
          letterSpacing: "0.08em",
        }}
      >
        NO LONGITUDINAL PROGRESS OBSERVATIONS REPORTED
      </div>
    );
  }

  // Find baseline original cost for financial progress ratio calculations
  const baselineCost = data.find((d) => d.original_cost && d.original_cost > 0)?.original_cost || null;

  // Format data points for dual-trajectory rendering
  const chartData = data.map((d) => {
    const origCost = d.original_cost || baselineCost;
    const financialRatio =
      d.cumulative_expenditure !== null &&
      d.cumulative_expenditure !== undefined &&
      origCost &&
      origCost > 0
        ? Number(((d.cumulative_expenditure / origCost) * 100).toFixed(2))
        : null;

    return {
      report_month: d.report_month,
      physical_progress: d.physical_progress,
      financial_progress: financialRatio,
      cumulative_expenditure: d.cumulative_expenditure,
      original_cost: origCost,
    };
  });

  const firstMonth = data[0]?.report_month || "";
  const lastMonth = data[data.length - 1]?.report_month || "";

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 12, left: 12, bottom: 28 }}
        >
          {/* Clean horizontal baseline guidelines matching Stitch reference */}
          <CartesianGrid
            stroke="#727973"
            strokeOpacity={0.12}
            strokeDasharray="0"
            vertical={false}
          />
          <XAxis dataKey="report_month" hide />
          <YAxis
            domain={[0, (dataMax: number) => (dataMax > 100 ? Math.ceil(dataMax * 1.05) : 100)]}
            hide
          />
          <Tooltip
            content={
              <ChartTooltip
                titlePrefix="REPORT MONTH"
                metrics={(point) => [
                  {
                    label: "Physical Progress",
                    value:
                      point.physical_progress !== null && point.physical_progress !== undefined
                        ? `${point.physical_progress}%`
                        : "NOT REPORTED",
                    color: "#A9CFB7",
                  },
                  {
                    label: "Financial Progress",
                    value:
                      point.financial_progress !== null && point.financial_progress !== undefined
                        ? `${point.financial_progress}%`
                        : "NOT REPORTED",
                    color: "#FAF9F6",
                  },
                  ...(point.cumulative_expenditure !== null && point.cumulative_expenditure !== undefined
                    ? [
                        {
                          label: "Cumulative Expenditure",
                          value: `₹ ${Number(point.cumulative_expenditure).toLocaleString()} CR`,
                          color: "#E2E3DE",
                        },
                      ]
                    : []),
                ]}
              />
            }
          />
          {/* Primary Solid Line: Physical Progress */}
          <Line
            type="linear"
            dataKey="physical_progress"
            name="Physical Progress"
            stroke="#1A3C2B"
            strokeWidth={1.5}
            connectNulls={false}
            dot={{
              r: 2,
              fill: "#FAF9F6",
              stroke: "#1A3C2B",
              strokeWidth: 1,
            }}
            activeDot={{
              r: 4.5,
              fill: "#1A3C2B",
              stroke: "#FAF9F6",
              strokeWidth: 1.5,
            }}
            isAnimationActive={false}
          />
          {/* Secondary Dashed Line: Financial Progress */}
          <Line
            type="linear"
            dataKey="financial_progress"
            name="Financial Progress"
            stroke="#1A3C2B"
            strokeWidth={1}
            strokeDasharray="4 2"
            connectNulls={false}
            dot={{
              r: 1.5,
              fill: "#FAF9F6",
              stroke: "#1A3C2B",
              strokeWidth: 1,
            }}
            activeDot={{
              r: 3.5,
              fill: "#1A3C2B",
              stroke: "#FAF9F6",
              strokeWidth: 1.5,
            }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Start Month Label (Bottom-Left) */}
      {firstMonth && (
        <div
          style={{
            position: "absolute",
            bottom: "8px",
            left: "12px",
            fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
            fontSize: "10px",
            color: "var(--color-text-dim, #5F5E5C)",
            letterSpacing: "0.05em",
            userSelect: "none",
            pointerEvents: "none",
          }}
        >
          {firstMonth}
        </div>
      )}

      {/* End Month Label (Bottom-Right) */}
      {lastMonth && (
        <div
          style={{
            position: "absolute",
            bottom: "8px",
            right: "12px",
            fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
            fontSize: "10px",
            color: "var(--color-text-dim, #5F5E5C)",
            letterSpacing: "0.05em",
            userSelect: "none",
            pointerEvents: "none",
          }}
        >
          {lastMonth}
        </div>
      )}
    </div>
  );
};
