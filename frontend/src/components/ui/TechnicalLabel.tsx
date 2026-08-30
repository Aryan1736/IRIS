import React from "react";
import { clsx } from "clsx";

export interface TechnicalLabelProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  sublabel?: string;
  indicatorColor?: string;
}

export const TechnicalLabel: React.FC<TechnicalLabelProps> = ({
  label,
  sublabel,
  indicatorColor = "var(--color-primary-600)",
  className,
  ...props
}) => {
  return (
    <div
      className={clsx("technical-label", className)}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        fontFamily: "var(--font-mono)",
        fontSize: "var(--font-size-xs)",
        textTransform: "uppercase",
        letterSpacing: "0.1em",
        color: "var(--color-text-variant)",
      }}
      {...props}
    >
      <span
        style={{
          width: "6px",
          height: "6px",
          backgroundColor: indicatorColor,
          display: "inline-block",
        }}
      />
      <span style={{ fontWeight: 600 }}>{label}</span>
      {sublabel && (
        <>
          <span style={{ color: "var(--color-border-strong)" }}>//</span>
          <span style={{ color: "var(--color-text-dim)" }}>{sublabel}</span>
        </>
      )}
    </div>
  );
};
