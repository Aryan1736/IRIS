import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardPage } from "../../../pages/DashboardPage";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import * as systemApi from "@/api/system.ts";
import * as projectsApi from "@/api/projects.ts";
import * as riskApi from "@/api/risk.ts";

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
  fetchMonthlyObservations: vi.fn(),
}));

vi.mock("@/api/risk.ts", () => ({
  fetchRiskSummary: vi.fn(),
  fetchModelInfo: vi.fn(),
}));

describe("DashboardPage Real Data & Visual Fidelity", () => {
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
      ingested_at: "2026-08-30T10:00:00Z",
    });

    vi.mocked(projectsApi.fetchMonthlyObservations).mockResolvedValue([
      { report_month: "2023-01", observations: 1200 },
      { report_month: "2024-01", observations: 1400 },
      { report_month: "2025-01", observations: 1600 },
      { report_month: "2026-07", observations: 2100 },
    ]);

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

    vi.mocked(riskApi.fetchModelInfo).mockResolvedValue({
      serving_artifact_version: "iris_serving_v1_1",
      target: "target_effective_schedule_ext_3m",
      horizon_months: 3,
      status: "READY",
      models: [],
    });

    vi.mocked(riskApi.fetchRiskSummary).mockResolvedValue({
      report_month: "2026-04",
      regime_filter: null,
      filters: {},
      project_count: 1625,
      score_distribution: {
        minimum: 0.05,
        p25: 0.224,
        median: 0.389,
        p75: 0.582,
        p90: 0.710,
        p95: 0.841,
        maximum: 0.985,
        mean: 0.401,
      },
      top_risk_projects: [
        {
          project_code: "976809",
          project_name: "Amended BharatNet Program - ARP, NGL, MNP",
          agency: "BBNL",
          ministry: "Ministry of Communications",
          sector: "Telecommunication",
          state: "Arunachal Pradesh",
          regime: "MODERN",
          model_id: "tree_regime_modern",
          raw_probability: 0.88,
          risk_probability: 0.894,
          calibration_active: true,
          risk_rank: 1,
          risk_percentile: 99.9,
          population_size: 1625,
        },
      ],
      regimes: [],
      sector_summary: [],
    });
  });

  it("renders dashboard page intro, metrics, and all 6 sections with genuine backend data", async () => {
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

    // Section 01: Real Activity & Real Risk Quantiles
    expect(screen.getByText("PROJECT ACTIVITY OVER TIME.")).toBeInTheDocument();
    expect(screen.getByText("LONGITUDINAL OBSERVATION TIMELINE")).toBeInTheDocument();
    expect(screen.getByText("H=3 SCHEDULE EXTENSION RISK")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("22.4%")).toBeInTheDocument(); // P25
      expect(screen.getByText("38.9%")).toBeInTheDocument(); // Median
      expect(screen.getByText("58.2%")).toBeInTheDocument(); // P75
      expect(screen.getByText("84.1%")).toBeInTheDocument(); // P95
    });

    // Regression: Ensure 82%, 12%, 6% synthetic demo values are GONE
    expect(screen.queryByText("82%")).not.toBeInTheDocument();
    expect(screen.queryByText("12%")).not.toBeInTheDocument();
    expect(screen.queryByText("6%")).not.toBeInTheDocument();

    // Section 02: Schedule Intelligence (Honest Data Pending)
    expect(screen.getByText("WHERE SCHEDULES MOVE.")).toBeInTheDocument();

    // Section 03: Cost Intelligence (Honest Data Pending)
    expect(screen.getByText("FOLLOW THE MONEY.")).toBeInTheDocument();

    // Section 04: Early Warning with Real Evaluated Risk Project
    expect(screen.getByText("SEE THE RISK BEFORE IT BECOMES THE OUTCOME.")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Amended BharatNet Program - ARP, NGL, MNP")).toBeInTheDocument();
      expect(screen.getByText("976809")).toBeInTheDocument();
      expect(screen.getByText("89.4%")).toBeInTheDocument();
    });

    // Section 05: Portfolio Composition with Taxonomy Note
    expect(screen.getByText("FROM PROJECTS TO PORTFOLIOS.")).toBeInTheDocument();
    expect(screen.getByText(/TAXONOMY AUDIT NOTE/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("ROADS").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("NHAI").length).toBeGreaterThanOrEqual(1);
    });

    // Section 06: Data and Model Status
    expect(screen.getByText("LIVE SERVING READY")).toBeInTheDocument();
  });

  it("handles empty project list gracefully without falling back to mock projects", async () => {
    vi.mocked(riskApi.fetchRiskSummary).mockResolvedValue({
      report_month: "2026-04",
      regime_filter: null,
      filters: {},
      project_count: 0,
      score_distribution: {
        minimum: 0,
        p25: 0,
        median: 0,
        p75: 0,
        p90: 0,
        p95: 0,
        maximum: 0,
        mean: 0,
      },
      top_risk_projects: [],
      regimes: [],
      sector_summary: [],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("NO MONITORED PROJECTS RETURNED FROM SERVING LAYER")).toBeInTheDocument();
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
