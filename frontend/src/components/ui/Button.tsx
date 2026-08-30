import React from "react";
import { clsx } from "clsx";

export type ButtonVariant = "primary" | "secondary" | "outline" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className,
  disabled,
  children,
  ...props
}) => {
  const baseStyles: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    fontFamily: "var(--font-mono)",
    fontWeight: 500,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    cursor: disabled || isLoading ? "not-allowed" : "pointer",
    opacity: disabled || isLoading ? 0.6 : 1,
    transition: "all 150ms ease-in-out",
    border: "1px solid transparent",
    borderRadius: "var(--radius-none)",
    outline: "none",
  };

  const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
    primary: {
      backgroundColor: "var(--color-primary-900)",
      color: "var(--color-text-inverse)",
      borderColor: "var(--color-primary-900)",
    },
    secondary: {
      backgroundColor: "var(--color-surface-container-high)",
      color: "var(--color-text-main)",
      borderColor: "var(--color-border-hairline)",
    },
    outline: {
      backgroundColor: "transparent",
      color: "var(--color-primary-900)",
      borderColor: "var(--color-primary-900)",
    },
    ghost: {
      backgroundColor: "transparent",
      color: "var(--color-text-main)",
      borderColor: "transparent",
    },
  };

  const sizeStyles: Record<ButtonSize, React.CSSProperties> = {
    sm: {
      padding: "4px 10px",
      fontSize: "var(--font-size-xs)",
    },
    md: {
      padding: "8px 16px",
      fontSize: "var(--font-size-sm)",
    },
    lg: {
      padding: "12px 24px",
      fontSize: "var(--font-size-base)",
    },
  };

  return (
    <button
      className={clsx("btn", className)}
      style={{
        ...baseStyles,
        ...variantStyles[variant],
        ...sizeStyles[size],
      }}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <span
          style={{
            width: "12px",
            height: "12px",
            border: "2px solid currentColor",
            borderTopColor: "transparent",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
            display: "inline-block",
          }}
        />
      )}
      {!isLoading && leftIcon}
      <span>{children}</span>
      {!isLoading && rightIcon}
    </button>
  );
};
