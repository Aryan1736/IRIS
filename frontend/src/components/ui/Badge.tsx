import React from "react";
import { clsx } from "clsx";

export type BadgeVariant =
  | "primary"
  | "risk-high"
  | "risk-medium"
  | "risk-low"
  | "neutral"
  | "outline";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: "sm" | "md";
  dot?: boolean;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "neutral",
  size = "md",
  dot = false,
  className,
  children,
  ...props
}) => {
  const variantClass = {
    primary: "badge-primary",
    "risk-high": "badge-risk-high",
    "risk-medium": "badge-risk-medium",
    "risk-low": "badge-risk-low",
    neutral: "badge-neutral",
    outline: "bg-transparent border-gray-300 text-gray-700",
  }[variant];

  const sizeClass = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-0.5";

  return (
    <span
      className={clsx("badge", variantClass, sizeClass, className)}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        fontFamily: "var(--font-mono)",
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        borderRadius: "var(--radius-sm)",
        fontWeight: 500,
      }}
      {...props}
    >
      {dot && (
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "var(--radius-full)",
            backgroundColor: "currentColor",
            display: "inline-block",
          }}
        />
      )}
      {children}
    </span>
  );
};
