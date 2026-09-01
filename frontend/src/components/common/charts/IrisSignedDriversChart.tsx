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
  ReferenceLine,
} from "recharts";
import type { Contributor } from "@/types/risk.ts";
import { IrisChartTooltip } from "./IrisChartTooltip.tsx";

interface IrisSignedDriversChartProps {
  positiveContributors?: Contributor[];
  negativeContributors?: Contributor[];
  height?: number | string;
  isIllustrative?: boolean;
}

export const IrisSignedDriversChart: React.FC<IrisSignedDriversChartProps> = ({
  positiveContributors = [],
  negativeContributors = [],
  height = 240,
  isIllustrative = false,
}) => {
  // If illustrative (e.g. for Section 06 educational diagram), provide real representative feature families
  const posList = isIllustrative && positiveContributors.length === 0
    ? [
        { feature: "months_to_effective_schedule", display_name: "Tight Months to Schedule", value: "-14", contribution: 1.42, direction: "POSITIVE" as const, rank: 1 },
        { feature: "cumulative_expenditure_lag", display_name: "Expenditure Pacing Lag", value: "32%", contribution: 0.86, direction: "POSITIVE" as const, rank: 2 },
        { feature: "schedule_revision_history", display_name: "Prior Extension Count", value: "3", contribution: 0.54, direction: "POSITIVE" as const, rank: 3 },
      ]
    : positiveContributors;

  const negList = isIllustrative && negativeContributors.length === 0
    ? [
        { feature: "physical_progress_acceleration", display_name: "Physical Progress Momentum", value: "88%", contribution: -0.92, direction: "NEGATIVE" as const, rank: 1 },
        { feature: "sector_historical_stability", display_name: "Sector Benchmark Stability", value: "Railways", contribution: -0.48, direction: "NEGATIVE" as const, rank: 2 },
      ]
    : negativeContributors;

  const combined = [
    ...negList.map((c) => ({
      feature: c.feature,
      name: c.display_name || c.feature,
      contribution: Number(c.contribution.toFixed(2)),
      direction: c.direction,
      value: c.value,
      type: "Risk Reducing (-Δ)",
    })),
    ...posList.map((c) => ({
      feature: c.feature,
      name: c.display_name || c.feature,
      contribution: Number(c.contribution.toFixed(2)),
      direction: c.direction,
      value: c.value,
      type: "Risk Increasing (+Δ)",
    })),
  ];

  if (combined.length === 0) {
    return (
      <div style={{ padding: "24px", textAlign: "center", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--color-text-muted)" }}>
        NO SIGNED FEATURE CONTRIBUTIONS RECORDED.
      </div>
    );
  }

  // Calculate symmetrical or auto domain around 0
  const maxAbs = Math.max(0.5, ...combined.map((c) => Math.abs(c.contribution)));
  const domainLimit = Number((Math.ceil(maxAbs * 10) / 10).toFixed(1));

  return (
    <div style={{ width: "100%", height, position: "relative" }} aria-label="Signed Feature Driver Contributions Chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={combined}
          margin={{ top: 12, right: 32, left: 40, bottom: 12 }}
        >
          <CartesianGrid stroke="#E2E3DF" strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            domain={[-domainLimit, domainLimit]}
            stroke="#606460"
            tick={{ fill: "#606460", fontSize: 10, fontFamily: "var(--font-mono)" }}
            tickFormatter={(val: number) => (val > 0 ? `+${val}` : `${val}`)}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke="#606460"
            tick={{ fill: "var(--color-primary-950)", fontSize: 11, fontFamily: "var(--font-mono)", fontWeight: 500 }}
            tickLine={{ stroke: "#D1D4D1" }}
            axisLine={{ stroke: "#D1D4D1" }}
            width={160}
          />
          <ReferenceLine
            x={0}
            stroke="#0D0E0D"
            strokeWidth={1.5}
            label={{
              value: "0.0 BASELINE",
              position: "top",
              fill: "#0D0E0D",
              fontSize: 9,
              fontFamily: "var(--font-mono)",
              fontWeight: 700,
            }}
          />
          <Tooltip
            content={
              <IrisChartTooltip
                titlePrefix="FEATURE DRIVER"
                customFormatter={(payload) => {
                  const entry = Array.isArray(payload) ? payload[0]?.payload : undefined;
                  if (!entry) return [];
                  return [
                    {
                      label: "FEATURE NAME",
                      value: entry.name,
                      color: "#FFFFFF",
                    },
                    {
                      label: "MARGIN CONTRIBUTION",
                      value: `${entry.contribution > 0 ? "+" : ""}${entry.contribution}`,
                      color: entry.contribution >= 0 ? "#BA1A1A" : "#1A3C2B",
                      subtext: entry.type,
                    },
                    ...(entry.value ? [{ label: "REPORTED VALUE", value: entry.value, color: "#D1D4D1" }] : []),
                    {
                      label: "LOGIT SHIFT",
                      value: entry.contribution >= 0 ? "ELEVATES RISK" : "REDUCES RISK",
                      color: entry.contribution >= 0 ? "#BA1A1A" : "#1A3C2B",
                    },
                  ];
                }}
              />
            }
          />
          <Bar dataKey="contribution" name="Margin Contribution" isAnimationActive={false}>
            {combined.map((entry) => (
              <Cell
                key={`cell-${entry.feature}`}
                fill={entry.contribution >= 0 ? "#BA1A1A" : "#1A3C2B"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
