import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ProjectsPage } from "../../../pages/ProjectsPage";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import * as projectsApi from "@/api/projects.ts";
import * as systemApi from "@/api/system.ts";

describe("ProjectsPage", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.spyOn(projectsApi, "fetchProjects").mockResolvedValue({
      items: [
        {
          id: 1,
          project_code: "PRJ-TEST",
          project_name: "Test Project Highway",
          agency: "NHAI",
          ministry: "Ministry of Road Transport",
          sector: "Roads & Highways",
          state: "Maharashtra",
          report_month: "2024-02",
          approval_date: "2020-01",
          original_completion_date: "2024-12",
          revised_completion_date: null,
          original_cost: 1500.5,
          revised_cost: null,
          cumulative_expenditure: 850.2,
          physical_progress: 56.5,
        },
      ],
      total: 1,
      page: 1,
      page_size: 25,
      total_pages: 1,
    });

    vi.spyOn(projectsApi, "fetchFilterOptions").mockResolvedValue({
      sectors: ["Roads & Highways", "Railways"],
      agencies: ["NHAI", "RVNL"],
      states: ["Maharashtra", "Karnataka"],
      ministries: ["Ministry of Road Transport"],
      report_months: ["2024-01", "2024-02"],
    });

    vi.spyOn(systemApi, "fetchDatasetInfo").mockResolvedValue({
      status: "ACTIVE",
      covered_months: ["2023-01", "2024-02"],
      row_count: 64608,
      unique_projects_count: 4738,
      canonical_sha256: "abc",
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ProjectsPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders page layout, dynamic hero telemetry, and provenance footer", async () => {
    renderComponent();

    expect(screen.getByText("IRIS / PROJECTS / DISCOVERY")).toBeInTheDocument();
    expect(screen.getByText("PROJECTS. FIND THE SIGNAL.")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText("4,738").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("64,608").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("2023-01 → 2024-02").length).toBeGreaterThanOrEqual(1);
    });

    expect(screen.getByText("DATA INTEGRITY: VERIFIED")).toBeInTheDocument();
  });

  it("renders Section 01 Portfolio Snapshot with 7 real analytical cards", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("01.")).toBeInTheDocument();
    });

    expect(screen.getByText("PORTFOLIO SNAPSHOT & TAXONOMY TELEMETRY")).toBeInTheDocument();
    expect(screen.getByText("TOTAL PROJECTS")).toBeInTheDocument();
    expect(screen.getByText("MONITORED PERIOD")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE SECTORS")).toBeInTheDocument();
    expect(screen.getByText("STATES / REGIONS")).toBeInTheDocument();
  });

  it("renders Section 02 Project Directory with real project data and progress bar", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("Test Project Highway")).toBeInTheDocument();
    });

    expect(screen.getByText("02. PROJECT DIRECTORY")).toBeInTheDocument();
    expect(screen.getAllByText("SHOWING 1–1 OF 1 MATCHING OBSERVATIONS").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("PRJ-TEST")).toBeInTheDocument();
    expect(screen.getByText("56.5%")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "56.5");
  });

  it("opens project inspection console drawer when inspect is clicked and closes on Escape", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("INSPECT")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("INSPECT"));

    await waitFor(() => {
      expect(screen.getByText("PROJECT INSPECTION CONSOLE")).toBeInTheDocument();
    });

    expect(screen.getByText("FINANCIAL METRICS (RS CRORE)")).toBeInTheDocument();
    expect(screen.getByText("SCHEDULE TIMELINE")).toBeInTheDocument();
    expect(screen.getByText("OPEN FULL LONGITUDINAL ANALYSIS")).toBeInTheDocument();

    // Close on Escape
    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() => {
      expect(screen.queryByText("PROJECT INSPECTION CONSOLE")).not.toBeInTheDocument();
    });
  });
});
