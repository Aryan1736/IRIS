import React from "react";
import { clsx } from "clsx";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  icon,
  className,
  ...props
}) => {
  return (
    <div
      className={clsx("empty-state hairline-all", className)}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "48px 24px",
        textAlign: "center",
        backgroundColor: "var(--color-surface-container-low)",
        borderRadius: "var(--radius-none)",
      }}
      {...props}
    >
      {icon && (
        <div
          style={{
            marginBottom: "16px",
            color: "var(--color-text-dim)",
          }}
        >
          {icon}
        </div>
      )}
      <h4
        style={{
          fontFamily: "var(--font-heading)",
          fontSize: "var(--font-size-base)",
          fontWeight: 600,
          color: "var(--color-text-main)",
          marginBottom: "6px",
        }}
      >
        {title}
      </h4>
      {description && (
        <p
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "var(--font-size-xs)",
            color: "var(--color-text-muted)",
            maxWidth: "400px",
            lineHeight: 1.5,
            marginBottom: action ? "16px" : "0px",
          }}
        >
          {description}
        </p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
};
