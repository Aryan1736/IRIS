import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within, waitFor } from "@testing-library/react";
import { App } from "@/App.tsx";
import * as systemApi from "@/api/system.ts";

describe("IRIS Frontend App Shell", () => {
  beforeEach(() => {
    vi.spyOn(systemApi, "fetchHealth").mockResolvedValue({
      status: "healthy",
      database: "connected",
      version: "0.1.0",
      environment: "development",
      timestamp: "2026-08-30T12:00:00Z",
    });
  });

  it("renders the institutional header with IRIS brand, numbered navigation, and telemetry", async () => {
    render(<App />);

    // Scope header
    const header = screen.getByRole("banner");
    expect(within(header).getByText("IRIS")).toBeInTheDocument();
    expect(within(header).getByText("PAIMANA / MoSPI")).toBeInTheDocument();

    // Scope navigation inside header
    const nav = within(header).getByRole("navigation", { name: "Main Navigation" });
    expect(within(nav).getByRole("link", { name: "OVERVIEW" })).toBeInTheDocument();
    expect(within(nav).getByRole("link", { name: "01. PROJECTS" })).toBeInTheDocument();
    expect(within(nav).getByRole("link", { name: "02. ANALYTICS" })).toBeInTheDocument();
    expect(within(nav).getByRole("link", { name: "03. INTELLIGENCE" })).toBeInTheDocument();

    // Header CTA button
    expect(within(header).getByRole("link", { name: "ENTER IRIS" })).toBeInTheDocument();

    // Async telemetry state resolves to SYSTEM / ONLINE
    await waitFor(() => {
      expect(screen.getByText("SYSTEM / ONLINE")).toBeInTheDocument();
    });
  });
});
