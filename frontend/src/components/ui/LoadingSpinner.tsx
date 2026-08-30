import React from "react";

export interface LoadingSpinnerProps {
  label?: string;
  size?: "sm" | "md" | "lg";
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = "LOADING SYSTEM DATA...",
  size = "md",
}) => {
  const sizePx = {
    sm: 16,
    md: 24,
    lg: 36,
  }[size];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "12px",
        padding: "32px",
        minHeight: "160px",
      }}
    >
      <div
        style={{
          width: `${sizePx}px`,
          height: `${sizePx}px`,
          border: "2px solid var(--color-border-hairline)",
          borderTopColor: "var(--color-primary-900)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      {label && (
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "var(--font-size-xs)",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--color-text-dim)",
          }}
        >
          {label}
        </span>
      )}
    </div>
  );
};
