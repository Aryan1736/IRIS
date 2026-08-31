import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardPage } from "../../../pages/DashboardPage";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import * as systemApi from "@/api/system.ts";
import * as projectsApi from "@/api/projects.ts";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

// Mock the APIs
vi.mock("@/api/system.ts", () => ({
  fetchDatasetInfo: vi.fn(),
  fetchHealth: vi.fn(),
}));

vi.mock("@/api/projects.ts", () => ({
  fetchProjects: vi.fn(),
  fetchFilterOptions: vi.fn(),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();

    vi.mocked(systemApi.fetchHealth).mockResolvedValue({
      status: "healthy",
      database: "connected",
      version: "0.1.0",
      environment: "development",
      timestamp: "2026-08-30T12:00:00Z",
    });

    vi.mocked(systemApi.fetchDatasetInfo).mockResolvedValue({
      status: "ACTIVE",
      covered_months: ["2023-01", "2024-01", "2025-01", "2026-07"],
      row_count: 64608,
      unique_projects_count: 4738,
      canonical_sha256: "test-sha",
    });

    vi.mocked(projectsApi.fetchProjects).mockResolvedValue({
      items: [
        {
          id: 1,
          project_code: "PRJ-8821",
          project_name: "NH-66 FOUR LANING",
          agency: "NHAI",
          ministry: "MoRTH",
          sector: "ROADS",
          state: "MAHARASHTRA",
          report_month: "2026-07",
          approval_date: null,
          original_completion_date: null,
          revised_completion_date: null,
          original_cost: null,
          revised_cost: null,
          cumulative_expenditure: null,
          physical_progress: 72.5,
        },
      ],
      total: 1,
      page: 1,
      page_size: 5,
      total_pages: 1,
    });

    vi.mocked(projectsApi.fetchFilterOptions).mockResolvedValue({
      sectors: ["ROADS", "RAILWAYS", "POWER"],
      agencies: ["NHAI", "RVNL", "PGCIL"],
      states: ["MAHARASHTRA", "UTTAR PRADESH", "GUJARAT"],
      ministries: [],
      report_months: [],
    });
  });

  it("renders dashboard page intro, metrics, and all 6 sections with genuine data", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    // Intro lockup
    expect(screen.getByText("IRIS / PORTFOLIO OVERVIEW")).toBeInTheDocument();
    expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();

    // 6-Cell Metrics Bar
    await waitFor(() => {
      expect(screen.getAllByText("4,738").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("64,608").length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText("4 MOS")).toBeInTheDocument();
      expect(screen.getAllByText("2023-01 → 2026-07").length).toBeGreaterThanOrEqual(1);
    });

    // Section 01: Portfolio Movement
    expect(screen.getByText("PROJECT ACTIVITY OVER TIME.")).toBeInTheDocument();
    expect(screen.getByText("LONGITUDINAL OBSERVATION TIMELINE")).toBeInTheDocument();
    expect(screen.getByText("DEMO CLASSIFICATION — BACKEND PENDING")).toBeInTheDocument();

    // Section 02: Schedule Intelligence
    expect(screen.getByText("WHERE SCHEDULES MOVE.")).toBeInTheDocument();
    expect(screen.getByText("SCHEDULE EXTENSIONS")).toBeInTheDocument();

    // Section 03: Cost Intelligence
    expect(screen.getByText("FOLLOW THE MONEY.")).toBeInTheDocument();
    expect(screen.getByText("EXPENDITURE TRAJECTORY")).toBeInTheDocument();

    // Section 04: Early Warning
    expect(screen.getByText("SEE THE RISK BEFORE IT BECOMES THE OUTCOME.")).toBeInTheDocument();
    expect(screen.getByText("MODEL CONNECTIVITY: PENDING")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("NH-66 FOUR LANING")).toBeInTheDocument();
      expect(screen.getByText("PRJ-8821")).toBeInTheDocument();
    });

    // Section 05: Portfolio Composition
    expect(screen.getByText("FROM PROJECTS TO PORTFOLIOS.")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("ROADS").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("NHAI").length).toBeGreaterThanOrEqual(1);
    });

    // Section 06: Data and Model Status
    expect(screen.getByText("H=3 LOGISTIC BASELINE VALIDATED")).toBeInTheDocument();
    expect(screen.getByText("NOT YET CONNECTED")).toBeInTheDocument();
  });

  it("handles empty project list gracefully without falling back to mock projects", async () => {
    vi.mocked(projectsApi.fetchProjects).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 5,
      total_pages: 0,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("NO MONITORED PROJECTS RETURNED FROM BACKEND")).toBeInTheDocument();
    });
  });

  it("handles null dataset info gracefully with fallback dashes", async () => {
    vi.mocked(systemApi.fetchDatasetInfo).mockResolvedValue({
      status: "NOT_INGESTED",
      covered_months: [],
      row_count: 0,
      unique_projects_count: null,
      canonical_sha256: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(2);
    });
  });
});
