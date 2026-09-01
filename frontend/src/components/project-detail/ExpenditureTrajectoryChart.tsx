import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";
import { ChartTooltip } from "./ChartTooltip.tsx";

export interface ExpenditureObservation {
  report_month: string;
  cumulative_expenditure: number | null;
}

export interface ExpenditureTrajectoryChartProps {
  observations: ExpenditureObservation[];
  originalCost?: number | null;
}

export const ExpenditureTrajectoryChart: React.FC<ExpenditureTrajectoryChartProps> = ({
  observations,
  originalCost,
}) => {
  const data = observations || [];

  // Check if there are any non-null cumulative expenditure values
  const hasValidExpenditure = data.some(
    (d) => d.cumulative_expenditure !== null && d.cumulative_expenditure !== undefined
  );

  if (data.length === 0 || !hasValidExpenditure) {
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
        NO EXPENDITURE TRAJECTORY REPORTED
      </div>
    );
  }

  // Format month tick labels (e.g., "2025-07" -> "07/25")
  const formatXAxisTick = (month: string) => {
    if (!month) return "";
    const parts = month.split("-");
    if (parts.length === 2) {
      return `${parts[1]}/${parts[0].slice(2)}`;
    }
    return month;
  };

  // Format currency tick labels for YAxis
  const formatYAxisTick = (val: number) => {
    if (val >= 1000) {
      return `₹ ${(val / 1000).toFixed(val % 1000 === 0 ? 0 : 1)}k`;
    }
    return `₹ ${val}`;
  };

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 24, right: 24, left: 0, bottom: 8 }}
        >
          <CartesianGrid
            stroke="#727973"
            strokeOpacity={0.15}
            strokeDasharray="3 3"
            vertical={false}
          />
          <XAxis
            dataKey="report_month"
            tickFormatter={formatXAxisTick}
            stroke="#727973"
            strokeWidth={1}
            tick={{
              fill: "#5F5E5C",
              fontSize: 10,
              fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
            }}
            tickLine={{ stroke: "#727973", strokeWidth: 1 }}
            axisLine={{ stroke: "#C1C8C1", strokeWidth: 1 }}
          />
          <YAxis
            tickFormatter={formatYAxisTick}
            stroke="#727973"
            strokeWidth={1}
            tick={{
              fill: "#5F5E5C",
              fontSize: 10,
              fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
            }}
            tickLine={{ stroke: "#727973", strokeWidth: 1 }}
            axisLine={{ stroke: "#C1C8C1", strokeWidth: 1 }}
            width={52}
          />
          {originalCost !== null && originalCost !== undefined && originalCost > 0 && (
            <ReferenceLine
              y={originalCost}
              stroke="#727973"
              strokeDasharray="4 4"
              strokeWidth={1}
              opacity={0.8}
              label={{
                value: "SANCTIONED COST REF",
                position: "insideTopRight",
                fill: "#5F5E5C",
                fontSize: 9,
                fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
                letterSpacing: "0.08em",
              }}
            />
          )}
          <Tooltip
            content={
              <ChartTooltip
                titlePrefix="REPORT MONTH"
                metrics={(point) => {
                  const exp = point.cumulative_expenditure as number | null;
                  const ratio = exp !== null && exp !== undefined && originalCost && originalCost > 0
                    ? ((exp / originalCost) * 100).toFixed(1)
                    : null;

                  return [
                    {
                      label: "Cumulative Expenditure",
                      value: exp !== null && exp !== undefined
                        ? `₹ ${Number(exp).toLocaleString()} CR`
                        : "NOT REPORTED",
                      color: "#A9CFB7",
                    },
                    ...(originalCost !== null && originalCost !== undefined
                      ? [
                          {
                            label: "Sanctioned Cost",
                            value: `₹ ${Number(originalCost).toLocaleString()} CR`,
                            color: "#FAF9F6",
                          },
                        ]
                      : []),
                    ...(ratio !== null
                      ? [
                          {
                            label: "Expenditure / Sanctioned",
                            value: `${ratio}%`,
                            color: "#EAB308",
                          },
                        ]
                      : []),
                  ];
                }}
              />
            }
          />
          <Line
            type="linear"
            dataKey="cumulative_expenditure"
            name="Cumulative Expenditure"
            stroke="#1A3C2B"
            strokeWidth={2}
            connectNulls={false}
            dot={{
              r: 3,
              fill: "#FAF9F6",
              stroke: "#1A3C2B",
              strokeWidth: 1.5,
            }}
            activeDot={{
              r: 5,
              fill: "#1A3C2B",
              stroke: "#FAF9F6",
              strokeWidth: 2,
            }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
