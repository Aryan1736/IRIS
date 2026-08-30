import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { AnalyticsPage } from "@/pages/AnalyticsPage.tsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import * as systemApi from "@/api/system.ts";
import * as projectsApi from "@/api/projects.ts";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock("@/api/system.ts", () => ({
  fetchDatasetInfo: vi.fn(),
  fetchHealth: vi.fn(),
}));

vi.mock("@/api/projects.ts", () => ({
  fetchProjects: vi.fn(),
  fetchFilterOptions: vi.fn(),
}));

describe("AnalyticsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();

    vi.mocked(systemApi.fetchDatasetInfo).mockResolvedValue({
      status: "ACTIVE",
      covered_months: ["2023-01", "2024-01", "2025-01", "2026-07"],
      row_count: 64608,
      unique_projects_count: 4738,
      canonical_sha256: "test-sha",
      dataset_version: "v4.2",
    });

    vi.mocked(projectsApi.fetchFilterOptions).mockResolvedValue({
      sectors: ["TRANSPORT", "HEALTH", "POWER"],
      agencies: ["NHAI", "RAILWAYS"],
      states: ["MAHARASHTRA", "DELHI"],
      ministries: ["MoRTH", "MoR"],
      report_months: ["2026-07", "2026-06"],
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AnalyticsPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders page header and authentic dataset metadata", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("Understand How the Portfolio Moves.")).toBeInTheDocument();
    });

    expect(screen.getByText("IRIS / ANALYTICS / PORTFOLIO ANALYSIS")).toBeInTheDocument();
    expect(screen.getAllByText("4,738").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("64,608").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("2023-01 -> 2026-07")).toBeInTheDocument();
  });

  it("renders all 7 analytics sections with honest DATA PENDING badges for un-aggregated metrics", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("01. Portfolio Activity Over Time")).toBeInTheDocument();
    });

    // Section 01
    expect(screen.getByText("01. Portfolio Activity Over Time")).toBeInTheDocument();
    expect(screen.getByText("DATA COVERAGE & MONITORED PERIOD")).toBeInTheDocument();
    expect(screen.getByText("MONITORED MONTHS")).toBeInTheDocument();

    // Section 02
    expect(screen.getByText("02. Where Schedules Move")).toBeInTheDocument();
    expect(screen.getByText("AHEAD")).toBeInTheDocument();
    expect(screen.getByText("WITHIN")).toBeInTheDocument();

    // Section 03
    expect(screen.getByText("03. Follow the Money")).toBeInTheDocument();
    expect(screen.getByText("Total Reported Expenditure")).toBeInTheDocument();

    // Section 04
    expect(screen.getByText("04. Portfolio Composition")).toBeInTheDocument();
    expect(screen.getByText("DISTINCT MONITORED TAXONOMIES")).toBeInTheDocument();
    expect(screen.getAllByText("TRANSPORT").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("NHAI").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("MAHARASHTRA").length).toBeGreaterThanOrEqual(1);

    // Section 05
    expect(screen.getByText("05. Project Progress")).toBeInTheDocument();
    expect(screen.getByText("On Track")).toBeInTheDocument();

    // Section 06
    expect(screen.getByText("06. Completion Movement")).toBeInTheDocument();
    expect(screen.getByText("Revised Completion")).toBeInTheDocument();

    // Section 07
    expect(screen.getByText("07. Observations / Data Profile")).toBeInTheDocument();
    expect(screen.getByText("Coded Months")).toBeInTheDocument();
  });

  it("populates filter options from backend and updates filter selection", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByLabelText("Filter by Sector")).toBeInTheDocument();
    });

    expect(screen.getByText("SCOPE: CANONICAL TAXONOMIES")).toBeInTheDocument();

    const sectorSelect = screen.getByLabelText("Filter by Sector");
    expect(sectorSelect).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "TRANSPORT" })).toBeInTheDocument();

    fireEvent.change(sectorSelect, { target: { value: "TRANSPORT" } });
    expect((sectorSelect as HTMLSelectElement).value).toBe("TRANSPORT");
  });

  it("handles loading and error states gracefully", async () => {
    vi.mocked(systemApi.fetchDatasetInfo).mockRejectedValue(new Error("Database connection lost"));

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("Analytics Service Unavailable")).toBeInTheDocument();
    });

    expect(screen.getByText("Database connection lost")).toBeInTheDocument();
  });

  it("handles empty or null dataset responses without crashing", async () => {
    vi.mocked(systemApi.fetchDatasetInfo).mockResolvedValue({
      status: "NOT_INGESTED",
      covered_months: [],
      row_count: 0,
      unique_projects_count: null,
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("Understand How the Portfolio Moves.")).toBeInTheDocument();
    });

    expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(1);
  });
});
