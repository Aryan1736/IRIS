import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Badge } from "@/components/ui/Badge.tsx";
import { Button } from "@/components/ui/Button.tsx";
import { Card } from "@/components/ui/Card.tsx";
import { StatMetric } from "@/components/ui/StatMetric.tsx";
import { TechnicalLabel } from "@/components/ui/TechnicalLabel.tsx";
import { EmptyState } from "@/components/ui/EmptyState.tsx";

describe("Foundational UI Components", () => {
  it("renders Badge with appropriate variants and dot", () => {
    render(<Badge variant="risk-high" dot>CRITICAL RISK</Badge>);
    const badge = screen.getByText("CRITICAL RISK");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("badge-risk-high");
  });

  it("renders Button and handles click events", () => {
    const handleClick = vi.fn();
    render(
      <Button variant="primary" onClick={handleClick}>
        EXECUTE AUDIT
      </Button>
    );
    const button = screen.getByRole("button", { name: "EXECUTE AUDIT" });
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("renders Card with title, subtitle, and children", () => {
    render(
      <Card title="PORTFOLIO SUMMARY" subtitle="DATA LINEAGE AUDIT">
        <p>Card Body Content</p>
      </Card>
    );
    expect(screen.getByText("PORTFOLIO SUMMARY")).toBeInTheDocument();
    expect(screen.getByText("DATA LINEAGE AUDIT")).toBeInTheDocument();
    expect(screen.getByText("Card Body Content")).toBeInTheDocument();
  });

  it("renders StatMetric with value, unit, and delta", () => {
    render(
      <StatMetric
        label="TOTAL CAPITAL EXPENDITURE"
        value="₹45,210"
        unit="CR"
        delta="+12.4%"
        deltaType="positive"
      />
    );
    expect(screen.getByText("TOTAL CAPITAL EXPENDITURE")).toBeInTheDocument();
    expect(screen.getByText("₹45,210")).toBeInTheDocument();
    expect(screen.getByText("CR")).toBeInTheDocument();
    expect(screen.getByText("+12.4%")).toBeInTheDocument();
  });

  it("renders TechnicalLabel with category and sublabel", () => {
    render(
      <TechnicalLabel label="MODEL VERSION" sublabel="CATBOOST-TREESHAP-V1" />
    );
    expect(screen.getByText("MODEL VERSION")).toBeInTheDocument();
    expect(screen.getByText("CATBOOST-TREESHAP-V1")).toBeInTheDocument();
  });

  it("renders EmptyState with custom title and description", () => {
    render(
      <EmptyState
        title="NO RECORDS MATCHING QUERY"
        description="Try adjusting sector or state filters."
      />
    );
    expect(screen.getByText("NO RECORDS MATCHING QUERY")).toBeInTheDocument();
    expect(screen.getByText("Try adjusting sector or state filters.")).toBeInTheDocument();
  });
});
