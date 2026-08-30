import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button } from "@/components/ui/Button.tsx";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught application error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "400px",
            padding: "48px 24px",
            textAlign: "center",
          }}
        >
          <div
            className="hairline-all"
            style={{
              maxWidth: "600px",
              padding: "32px",
              backgroundColor: "var(--color-surface-bright)",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
                color: "var(--color-risk-high)",
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                marginBottom: "8px",
              }}
            >
              [ SYSTEM EXCEPTION CAPTURED ]
            </div>
            <h2
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "var(--font-size-xl)",
                fontWeight: 700,
                color: "var(--color-text-main)",
                marginBottom: "12px",
              }}
            >
              Application Encountered an Unexpected State
            </h2>
            <p
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
                color: "var(--color-text-muted)",
                marginBottom: "24px",
                lineHeight: 1.6,
                backgroundColor: "var(--color-surface-container-low)",
                padding: "12px",
                textAlign: "left",
                overflowX: "auto",
              }}
            >
              {this.state.error?.message || "Unknown client error"}
            </p>
            <Button variant="primary" size="md" onClick={this.handleReset}>
              REINITIALIZE INTERFACE
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
