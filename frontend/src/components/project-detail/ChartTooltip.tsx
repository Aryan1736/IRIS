import React from "react";

export interface TooltipMetric {
  label: string;
  value: string | number | null | undefined;
  unit?: string;
  color?: string;
}

export interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: Record<string, unknown>;
    value?: unknown;
    name?: string;
  }>;
  label?: string;
  titlePrefix?: string;
  metrics?: TooltipMetric[] | ((payload: Record<string, unknown>) => TooltipMetric[]);
}

export const ChartTooltip: React.FC<ChartTooltipProps> = ({
  active,
  payload,
  label,
  titlePrefix = "REPORT MONTH",
  metrics,
}) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const dataPoint = payload[0].payload;
  const currentLabel = label || (dataPoint.report_month as string) || "—";

  const resolvedMetrics: TooltipMetric[] = typeof metrics === "function"
    ? metrics(dataPoint)
    : metrics || [];

  return (
    <div
      style={{
        backgroundColor: "#1A1C1A",
        border: "1px solid #3A3A38",
        padding: "8px 12px",
        fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
        fontSize: "11px",
        color: "#FAF9F6",
        borderRadius: "0px",
        boxShadow: "none",
        lineHeight: 1.5,
        minWidth: "160px",
        pointerEvents: "none",
        zIndex: 50,
      }}
    >
      <div
        style={{
          borderBottom: "1px solid #3A3A38",
          paddingBottom: "4px",
          marginBottom: "6px",
          color: "#A9CFB7",
          fontWeight: 600,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
      >
        {titlePrefix}: {currentLabel}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "3px" }}>
        {resolvedMetrics.map((m, idx) => {
          const formattedVal = m.value !== null && m.value !== undefined
            ? `${m.value}${m.unit ? ` ${m.unit}` : ""}`
            : "NOT REPORTED";

          return (
            <div
              key={`metric-${idx}`}
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: "12px",
                color: m.color || "#FAF9F6",
              }}
            >
              <span style={{ color: "#9E9F9D", textTransform: "uppercase" }}>{m.label}:</span>
              <span style={{ fontWeight: 500 }}>{formattedVal}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
