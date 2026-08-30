import React from "react";
import { clsx } from "clsx";

export interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "title"> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  padding?: "none" | "sm" | "md" | "lg";
  headerBorder?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  padding = "md",
  headerBorder = true,
  className,
  children,
  style,
  ...props
}) => {
  const paddingMap = {
    none: "0px",
    sm: "var(--space-3)",
    md: "var(--space-6)",
    lg: "var(--space-8)",
  };

  return (
    <div
      className={clsx("card hairline-all", className)}
      style={{
        backgroundColor: "var(--color-surface-bright)",
        borderRadius: "var(--radius-none)",
        boxShadow: "var(--shadow-card)",
        ...style,
      }}
      {...props}
    >
      {(title || action) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "var(--space-4) var(--space-6)",
            borderBottom: headerBorder ? "1px solid var(--color-border-hairline)" : "none",
            backgroundColor: "var(--color-surface-container-low)",
          }}
        >
          <div>
            {typeof title === "string" ? (
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 600,
                  color: "var(--color-text-main)",
                }}
              >
                {title}
              </h3>
            ) : (
              title
            )}
            {subtitle && (
              <p
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "var(--font-size-xs)",
                  color: "var(--color-text-muted)",
                  marginTop: "2px",
                }}
              >
                {subtitle}
              </p>
            )}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div style={{ padding: paddingMap[padding] }}>{children}</div>
    </div>
  );
};
