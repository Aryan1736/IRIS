import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { LandingPage } from "@/pages/LandingPage.tsx";

describe("LandingPage Component Composition", () => {
  it("renders all authoritative Stitch sections in order", () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    // 1. Hero Section
    const h1 = screen.getByRole("heading", { level: 1 });
    expect(h1).toHaveTextContent(/FROM/i);
    expect(h1).toHaveTextContent(/INFRASTRUCTURE/i);
    expect(h1).toHaveTextContent(/MONITORING/i);
    expect(h1).toHaveTextContent(/TO INTELLIGENCE/i);
    expect(screen.getByText(/SYSTEM STATUS/i)).toBeInTheDocument();

    // 2. Timeline Section
    const timelineHeading = screen.getByRole("heading", { level: 2, name: /INFRASTRUCTURE PROJECTS/i });
    expect(timelineHeading).toBeInTheDocument();
    expect(screen.getByText(/Longitudinal Observation Timeline/i)).toBeInTheDocument();

    // 3. Capabilities Section
    expect(screen.getByText(/MONITOR WHAT CHANGES/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "PROJECT DISCOVERY" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "PROJECT HISTORY" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "COST INTELLIGENCE" })).toBeInTheDocument();

    // 4. Data Foundation Section
    expect(screen.getByText(/EVERY PROJECT HAS A HISTORY/i)).toBeInTheDocument();
    expect(screen.getByText(/PROJECT CODE/i)).toBeInTheDocument();
    expect(screen.getByText(/DATA LINEAGE FLOW/i)).toBeInTheDocument();

    // 5. Predictive Section
    expect(screen.getByRole("heading", { name: /SEE THE RISK BEFORE IT/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /COST OVERRUN/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /SCHEDULE DELAY/i })).toBeInTheDocument();

    // 6. Evolution Section
    expect(screen.getByRole("heading", { name: /EVOLUTION OF/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "FROM PROJECTS TO PORTFOLIOS" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "ASK THE INFRASTRUCTURE PORTFOLIO." })).toBeInTheDocument();

    // 7. Auditability Section
    expect(screen.getByText(/BUILT FOR AUDITABILITY/i)).toBeInTheDocument();
    expect(screen.getByText(/SOURCE-FAITHFUL EXTRACTION/i)).toBeInTheDocument();

    // 8. CTA Section
    expect(screen.getByRole("heading", { name: /EXPLORE THE/i })).toBeInTheDocument();
  });
});
