import React from "react";

export interface IrisTooltipItem {
  label: string;
  value: string | number;
  color?: string;
  subtext?: string;
}

export interface IrisChartTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number | string;
    dataKey?: string;
    name?: string;
    payload?: Record<string, unknown>;
    color?: string;
  }>;
  label?: string | number;
  title?: string;
  titlePrefix?: string;
  items?: IrisTooltipItem[];
  customFormatter?: (payload: unknown, label: unknown) => IrisTooltipItem[];
}

export const IrisChartTooltip: React.FC<IrisChartTooltipProps> = ({
  active,
  payload,
  label,
  title,
  titlePrefix = "METRIC",
  items,
  customFormatter,
}) => {
  if (!active) return null;

  let displayItems: IrisTooltipItem[] = [];

  if (items && items.length > 0) {
    displayItems = items;
  } else if (customFormatter && payload) {
    displayItems = customFormatter(payload, label);
  } else if (payload && payload.length > 0) {
    displayItems = payload.map((entry) => ({
      label: (entry.name || entry.dataKey || "Value").toString().toUpperCase(),
      value: typeof entry.value === "number" ? entry.value.toLocaleString() : (entry.value || "—"),
      color: entry.color || "#FFFFFF",
    }));
  }

  const displayTitle = title || (label != null ? `${titlePrefix}: ${label}` : undefined);

  return (
    <div
      className="iris-chart-tooltip"
      style={{
        backgroundColor: "#111311",
        border: "1px solid #3A3D3A",
        padding: "10px 14px",
        fontFamily: "var(--font-mono, JetBrains Mono, monospace)",
        borderRadius: "0px",
        boxShadow: "0 6px 18px rgba(0, 0, 0, 0.35)",
        zIndex: 1000,
        minWidth: "180px",
        maxWidth: "280px",
        pointerEvents: "none",
      }}
    >
      {displayTitle && (
        <div
          style={{
            fontSize: "10px",
            color: "#A0A4A0",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            marginBottom: "8px",
            borderBottom: "1px solid #282B28",
            paddingBottom: "4px",
            fontWeight: 600,
          }}
        >
          {displayTitle}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
        {displayItems.map((item, idx) => (
          <div
            key={`tooltip-item-${idx}`}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
              gap: "12px",
              fontSize: "11px",
            }}
          >
            <span style={{ color: "#D1D4D1", textTransform: "uppercase", fontSize: "10px", letterSpacing: "0.04em" }}>
              {item.label}:
            </span>
            <div style={{ textAlign: "right" }}>
              <span style={{ color: item.color || "#FFFFFF", fontWeight: 700, fontSize: "12px" }}>
                {item.value}
              </span>
              {item.subtext && (
                <div style={{ fontSize: "9px", color: "#808480", marginTop: "1px" }}>
                  {item.subtext}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
