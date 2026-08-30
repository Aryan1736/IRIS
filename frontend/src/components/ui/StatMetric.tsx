import React from "react";
import { clsx } from "clsx";

export interface StatMetricProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: string | number;
  unit?: string;
  delta?: string;
  deltaType?: "positive" | "negative" | "neutral";
  helperText?: string;
}

export const StatMetric: React.FC<StatMetricProps> = ({
  label,
  value,
  unit,
  delta,
  deltaType = "neutral",
  helperText,
  className,
  ...props
}) => {
  const deltaColors = {
    positive: "var(--color-primary-600)",
    negative: "var(--color-risk-high)",
    neutral: "var(--color-text-muted)",
  };

  return (
    <div
      className={clsx("stat-metric", className)}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "4px",
      }}
      {...props}
    >
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "var(--font-size-xs)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "var(--color-text-variant)",
          fontWeight: 500,
        }}
      >
        {label}
      </span>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "6px",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "var(--font-size-3xl)",
            fontWeight: 700,
            color: "var(--color-text-main)",
            lineHeight: 1.1,
          }}
        >
          {value}
        </span>
        {unit && (
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "var(--font-size-xs)",
              color: "var(--color-text-muted)",
            }}
          >
            {unit}
          </span>
        )}
      </div>
      {(delta || helperText) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "var(--font-size-xs)",
            fontFamily: "var(--font-mono)",
            marginTop: "2px",
          }}
        >
          {delta && (
            <span style={{ color: deltaColors[deltaType], fontWeight: 600 }}>
              {delta}
            </span>
          )}
          {helperText && (
            <span style={{ color: "var(--color-text-dim)" }}>
              {helperText}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
