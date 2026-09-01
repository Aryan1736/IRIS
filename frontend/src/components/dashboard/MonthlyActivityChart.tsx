import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Brush,
} from "recharts";
import type { MonthlyObservationPoint } from "@/api/projects.ts";
import { IrisChartTooltip } from "@/components/common/charts/IrisChartTooltip.tsx";

interface MonthlyActivityChartProps {
  data: MonthlyObservationPoint[];
  isLoading?: boolean;
  height?: number | string;
}

export const MonthlyActivityChart: React.FC<MonthlyActivityChartProps> = ({
  data,
  isLoading = false,
  height = 220,
}) => {
  if (isLoading) {
    return (
      <div
        style={{
          height: typeof height === "number" ? `${height}px` : height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "var(--font-mono)",
          fontSize: "11px",
          color: "var(--color-text-dim)",
          textTransform: "uppercase",
        }}
      >
        LOADING TEMPORAL OBSERVATION TIMELINE...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div
        style={{
          height: typeof height === "number" ? `${height}px` : height,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          border: "1px dashed var(--color-border-hairline)",
          padding: "24px",
          textAlign: "center",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            fontWeight: 600,
            color: "var(--color-coral)",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}
        >
          DATA PENDING
        </span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--color-text-dim)",
            textTransform: "uppercase",
          }}
        >
          NO LONGITUDINAL OBSERVATIONS AVAILABLE FOR TEMPORAL RECONSTRUCTION
        </span>
      </div>
    );
  }

  // Compute running cumulative observations strictly from returned monthly records
  let runningSum = 0;
  const chartData = data.map((d) => {
    runningSum += d.observations;
    return {
      report_month: d.report_month,
      observations: d.observations,
      cumulative: runningSum,
    };
  });

  return (
    <div style={{ width: "100%", height, position: "relative" }} aria-label="Monthly Activity Chart">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 12, right: 16, bottom: 8, left: -10 }} syncId="iris-activity-timeline">
          <CartesianGrid stroke="#E2E3DF" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="report_month"
            stroke="#606460"
            tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "#606460" }}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
            interval="preserveStartEnd"
          />
          <YAxis
            stroke="#606460"
            tick={{ fontFamily: "var(--font-mono)", fontSize: 10, fill: "#606460" }}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
            domain={["auto", "auto"]}
            tickFormatter={(val: number) => val.toLocaleString()}
          />
          <Tooltip
            content={
              <IrisChartTooltip
                titlePrefix="REPORT MONTH"
                customFormatter={(payload) => {
                  const entry = Array.isArray(payload) ? payload[0]?.payload : undefined;
                  if (!entry) return [];
                  return [
                    {
                      label: "MONTHLY OBSERVATIONS",
                      value: Number(entry.observations).toLocaleString(),
                      color: "#FFFFFF",
                    },
                    {
                      label: "CUMULATIVE OBSERVED",
                      value: Number(entry.cumulative).toLocaleString(),
                      color: "#A9CFB7",
                    },
                  ];
                }}
              />
            }
          />
          <Area
            type="linear"
            dataKey="observations"
            fill="rgba(26, 60, 43, 0.08)"
            stroke="none"
            isAnimationActive={false}
          />
          <Line
            type="linear"
            dataKey="observations"
            name="Observations"
            stroke="#1A3C2B"
            strokeWidth={1.75}
            dot={{ r: 2, fill: "#1A3C2B" }}
            activeDot={{ r: 4.5, fill: "#BA1A1A", stroke: "#FFFFFF", strokeWidth: 1.5 }}
            connectNulls={false}
            isAnimationActive={false}
          />
          {chartData.length > 18 && (
            <Brush dataKey="report_month" height={18} stroke="#1A3C2B" />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
