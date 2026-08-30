import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout.tsx";
import { LandingPage } from "@/pages/LandingPage.tsx";
import { DashboardPage } from "@/pages/DashboardPage.tsx";
import { ProjectsPage } from "@/pages/ProjectsPage.tsx";
import { ProjectDetailPage } from "@/pages/ProjectDetailPage.tsx";
import { AnalyticsPage } from "@/pages/AnalyticsPage.tsx";
import { IntelligencePage } from "@/pages/IntelligencePage.tsx";
import * as systemApi from "@/api/system.ts";
import * as projectApi from "@/api/projects.ts";
import * as riskApi from "@/api/risk.ts";

vi.mock("@/api/system.ts", () => ({
  fetchHealth: vi.fn(),
  fetchDatasetInfo: vi.fn(),
}));

vi.mock("@/api/projects.ts", () => ({
  fetchProjects: vi.fn(),
  fetchFilterOptions: vi.fn(),
  fetchQuickSearch: vi.fn(),
  fetchProjectDetail: vi.fn(),
  fetchLatestSnapshot: vi.fn(),
  fetchProjectTrajectory: vi.fn(),
  fetchCostRevisions: vi.fn(),
  fetchScheduleExtensions: vi.fn(),
}));

vi.mock("@/api/risk.ts", () => ({
  fetchRiskOptions: vi.fn(),
  fetchModelInfo: vi.fn(),
  fetchRiskSummary: vi.fn(),
  fetchRiskProjects: vi.fn(),
  fetchProjectRisk: vi.fn(),
  fetchProjectRiskHistory: vi.fn(),
}));

describe("IRIS Cross-Page Integration & Routing", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(systemApi.fetchHealth).mockResolvedValue({
      status: "healthy",
      app: "IRIS API",
      database: { connected: true },
      version: "0.1.0",
      environment: "development",
      timestamp: "2026-08-30T12:00:00Z",
    });

    vi.mocked(systemApi.fetchDatasetInfo).mockResolvedValue({
      status: "ACTIVE",
      dataset_version: "2026.07.1",
      canonical_sha256: "abc123sha",
      covered_months: ["2023-01", "2026-07"],
      row_count: 45000,
      unique_projects_count: 2189,
      source_version_identifier: "paimana_core_2026_07",
      ingested_at: "2026-08-30T10:00:00Z",
    });

    vi.mocked(projectApi.fetchFilterOptions).mockResolvedValue({
      sectors: ["Roads & Highways", "Railways"],
      agencies: ["NHAI", "RVNL"],
      ministries: ["Ministry of Road Transport & Highways"],
      states: ["Maharashtra", "Karnataka"],
      report_months: ["2026-07"],
    });

    vi.mocked(projectApi.fetchProjects).mockResolvedValue({
      items: [
        {
          id: 1,
          project_code: "200101",
          project_name: "Western Dedicated Freight Corridor",
          agency: "DFCCIL",
          ministry: "Ministry of Railways",
          sector: "Railways",
          state: "Maharashtra",
          original_cost: 28181.0,
          revised_cost: 51200.0,
          cumulative_expenditure: 46000.0,
          physical_progress: 92.4,
          approval_date: "2008-02-01",
          original_completion_date: "2017-03-01",
          revised_completion_date: "2026-12-01",
          report_month: "2026-07",
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    });

    vi.mocked(projectApi.fetchProjectDetail).mockImplementation(async (code: string) => {
      if (code === "200101") {
        return {
          project_code: "200101",
          project_name: "Western Dedicated Freight Corridor",
          agency: "DFCCIL",
          ministry: "Ministry of Railways",
          sector: "Railways",
          state: "Maharashtra",
          first_reported_month: "2023-01",
          latest_report_month: "2026-07",
          total_observations_count: 42,
          latest_observation: {
            id: 1,
            project_code: "200101",
            legacy_ocms_code: null,
            pmgid: null,
            project_name: "Western Dedicated Freight Corridor",
            agency: "DFCCIL",
            ministry: "Ministry of Railways",
            sector: "Railways",
            state: "Maharashtra",
            approval_date: "2008-02-01",
            start_date: "2009-01-01",
            original_completion_date: "2017-03-01",
            revised_completion_date: "2026-12-01",
            original_cost: 28181.0,
            revised_cost: 51200.0,
            cumulative_expenditure: 46000.0,
            physical_progress: 92.4,
            report_month: "2026-07",
            approval_date_raw: "02/2008",
            start_date_raw: "01/2009",
            original_completion_date_raw: "03/2017",
            revised_completion_date_raw: "12/2026",
            original_cost_raw: "28181.0",
            revised_cost_raw: "51200.0",
            cumulative_expenditure_raw: "46000.0",
            physical_progress_raw: "92.4",
            source_file: "Flash_Report_July_2026.pdf",
            source_page: 42,
            source_pages: "42",
            source_row_number: 1,
            source_serial_number: 1,
            extraction_method: "table6-eight-column-v1",
          },
        };
      }
      throw new Error("Project not found");
    });

    vi.mocked(projectApi.fetchLatestSnapshot).mockResolvedValue({
      id: 1,
      project_code: "200101",
      legacy_ocms_code: null,
      pmgid: null,
      project_name: "Western Dedicated Freight Corridor",
      agency: "DFCCIL",
      ministry: "Ministry of Railways",
      sector: "Railways",
      state: "Maharashtra",
      approval_date: "2008-02-01",
      start_date: "2009-01-01",
      original_completion_date: "2017-03-01",
      revised_completion_date: "2026-12-01",
      original_cost: 28181.0,
      revised_cost: 51200.0,
      cumulative_expenditure: 46000.0,
      physical_progress: 92.4,
      report_month: "2026-07",
      approval_date_raw: "02/2008",
      start_date_raw: "01/2009",
      original_completion_date_raw: "03/2017",
      revised_completion_date_raw: "12/2026",
      original_cost_raw: "28181.0",
      revised_cost_raw: "51200.0",
      cumulative_expenditure_raw: "46000.0",
      physical_progress_raw: "92.4",
      source_file: "Flash_Report_July_2026.pdf",
      source_page: 42,
      source_pages: "42",
      source_row_number: 1,
      source_serial_number: 1,
      extraction_method: "table6-eight-column-v1",
    });

    vi.mocked(projectApi.fetchProjectTrajectory).mockResolvedValue({
      project_code: "200101",
      project_name: "Western Dedicated Freight Corridor",
      observations_count: 1,
      trajectory: [
        {
          report_month: "2026-07",
          original_cost: 28181.0,
          revised_cost: 51200.0,
          cumulative_expenditure: 46000.0,
          physical_progress: 92.4,
          approval_date: "2008-02-01",
          start_date: "2009-01-01",
          original_completion_date: "2017-03-01",
          revised_completion_date: "2026-12-01",
          agency: "DFCCIL",
          ministry: "Ministry of Railways",
          sector: "Railways",
          state: "Maharashtra",
        },
      ],
    });

    vi.mocked(projectApi.fetchCostRevisions).mockResolvedValue({
      project_code: "200101",
      project_name: "Western Dedicated Freight Corridor",
      revisions: [],
      latest_original_cost: 28181.0,
      latest_revised_cost: 51200.0,
      cost_revision_ratio: 1.81,
    });

    vi.mocked(projectApi.fetchScheduleExtensions).mockResolvedValue({
      project_code: "200101",
      project_name: "Western Dedicated Freight Corridor",
      extensions: [],
      latest_original_completion: "2017-03-01",
      latest_revised_completion: "2026-12-01",
    });

    vi.mocked(riskApi.fetchRiskOptions).mockResolvedValue({
      report_months: ["2026-04"],
      default_report_month: "2026-04",
      selected_report_month: "2026-04",
      regimes: ["MODERN"],
      sectors: ["Railways"],
      agencies: ["DFCCIL"],
      ministries: ["Ministry of Railways"],
      states: ["Maharashtra"],
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
        minimum: 0.01,
        p25: 0.2,
        median: 0.4,
        p75: 0.6,
        p90: 0.7,
        p95: 0.8,
        maximum: 0.99,
        mean: 0.39,
      },
      top_risk_projects: [],
      regimes: [],
      sector_summary: [],
    });

    vi.mocked(riskApi.fetchRiskProjects).mockResolvedValue({
      report_month: "2026-04",
      filters: {},
      page: 1,
      page_size: 25,
      total: 0,
      items: [],
    });
  });

  const renderAppAt = (initialEntry: string) => {
    const qc = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    return render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={[initialEntry]}>
          <AppLayout>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/projects/:projectCode" element={<ProjectDetailPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/intelligence" element={<IntelligencePage />} />
              <Route path="*" element={<div>404 NOT FOUND</div>} />
            </Routes>
          </AppLayout>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it("renders Landing Page at / and navigates to /dashboard via ENTER IRIS", async () => {
    renderAppAt("/");

    const h1 = screen.getByRole("heading", { level: 1 });
    expect(h1).toHaveTextContent(/FROM/i);
    expect(h1).toHaveTextContent(/INFRASTRUCTURE/i);
    expect(h1).toHaveTextContent(/TO INTELLIGENCE/i);

    const enterBtns = screen.getAllByRole("link", { name: "ENTER IRIS" });
    expect(enterBtns[0]).toHaveAttribute("href", "/dashboard");
  });

  it("renders Dashboard Overview at /dashboard", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
      expect(screen.getByText("PROJECT ACTIVITY OVER TIME.")).toBeInTheDocument();
    });
  });

  it("renders Project Discovery at /projects with 01. PROJECTS active", async () => {
    renderAppAt("/projects");

    await waitFor(() => {
      expect(screen.getByText("PROJECTS. FIND THE SIGNAL.")).toBeInTheDocument();
    });

    const projectsNav = screen.getByRole("link", { name: "01. PROJECTS" });
    expect(projectsNav).toHaveStyle({ fontWeight: "600" });
  });

  it("renders Project Detail at /projects/200101 and keeps 01. PROJECTS active", async () => {
    renderAppAt("/projects/200101");

    await waitFor(() => {
      expect(screen.getByText("Western Dedicated Freight Corridor")).toBeInTheDocument();
      expect(screen.getAllByText("200101").length).toBeGreaterThanOrEqual(1);
    });

    const projectsNav = screen.getByRole("link", { name: "01. PROJECTS" });
    expect(projectsNav).toHaveStyle({ fontWeight: "600" });

    expect(screen.getByText("← BACK TO PROJECTS")).toBeInTheDocument();
    expect(screen.getByText("DASHBOARD OVERVIEW")).toBeInTheDocument();
  });

  it("renders Portfolio Analytics at /analytics with 02. ANALYTICS active", async () => {
    renderAppAt("/analytics");

    await waitFor(() => {
      expect(screen.getByText("Understand How the Portfolio Moves.")).toBeInTheDocument();
    });

    const analyticsNav = screen.getByRole("link", { name: "02. ANALYTICS" });
    expect(analyticsNav).toHaveStyle({ fontWeight: "600" });
  });

  it("renders Early Warning Intelligence at /intelligence with 03. INTELLIGENCE active", async () => {
    renderAppAt("/intelligence");

    await waitFor(() => {
      expect(screen.getByText("See the Risk Before It Becomes the Outcome.")).toBeInTheDocument();
    });

    const intelNav = screen.getByRole("link", { name: "03. INTELLIGENCE" });
    expect(intelNav).toHaveStyle({ fontWeight: "600" });
  });

  it("renders truthful 404 state when project record is not found", async () => {
    vi.mocked(projectApi.fetchProjectDetail).mockRejectedValueOnce(new Error("Project not found"));

    renderAppAt("/projects/INVALID_PROJECT");

    await waitFor(() => {
      expect(screen.getByText("PROJECT NOT FOUND: INVALID_PROJECT")).toBeInTheDocument();
    });

    expect(screen.getByText("← RETURN TO PROJECT DISCOVERY")).toBeInTheDocument();
  });

  it("renders fallback 404 when route is unmapped", () => {
    renderAppAt("/unknown/route");

    expect(screen.getByText("404 NOT FOUND")).toBeInTheDocument();
  });
});
