import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent, within } from "@testing-library/react";
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

describe("IRIS Cross-Page Integration & Full Navigation Graph", () => {
  beforeEach(() => {
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
      timeline: [],
      latest_original_completion_date: "2017-03-01",
      latest_revised_completion_date: "2026-12-01",
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
      top_risk_projects: [
        {
          project_code: "200101",
          project_name: "Western Dedicated Freight Corridor",
          agency: "DFCCIL",
          ministry: "Ministry of Railways",
          sector: "Railways",
          state: "Maharashtra",
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
              <Route
                path="*"
                element={
                  <div data-testid="unmapped-route">
                    <h1>404 — Page Unmapped</h1>
                    <a href="/dashboard">← RETURN TO OVERVIEW</a>
                    <a href="/projects">EXPLORE PROJECTS →</a>
                  </div>
                }
              />
            </Routes>
          </AppLayout>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  // 1. Landing Page Loads
  it("renders Landing Page at / with correct branding and hero content", () => {
    renderAppAt("/");

    const h1 = screen.getByRole("heading", { level: 1 });
    expect(h1).toHaveTextContent(/FROM/i);
    expect(h1).toHaveTextContent(/INFRASTRUCTURE/i);
    expect(h1).toHaveTextContent(/TO INTELLIGENCE/i);
  });

  // 2. Landing Page ENTER IRIS CTA points to /dashboard
  it("Landing page ENTER IRIS CTAs point to /dashboard", () => {
    renderAppAt("/");

    const enterIrisLinks = screen.getAllByRole("link", { name: "ENTER IRIS" });
    expect(enterIrisLinks.length).toBeGreaterThanOrEqual(2);
    enterIrisLinks.forEach((link) => {
      expect(link).toHaveAttribute("href", "/dashboard");
    });
  });

  // 3. Landing Page EXPLORE PROJECTS CTA points to /projects
  it("Landing page EXPLORE PROJECTS CTAs point to /projects", () => {
    renderAppAt("/");

    const exploreLinks = screen.getAllByRole("link", { name: /EXPLORE PROJECTS/i });
    expect(exploreLinks.length).toBeGreaterThanOrEqual(1);
    exploreLinks.forEach((link) => {
      expect(link).toHaveAttribute("href", "/projects");
    });
  });

  // 4. Header OVERVIEW link navigates and sets active state at /dashboard
  it("Header OVERVIEW link points to /dashboard and is active at /dashboard", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
    });

    const overviewNav = screen.getByRole("link", { name: "OVERVIEW" });
    expect(overviewNav).toHaveAttribute("href", "/dashboard");
    expect(overviewNav).toHaveStyle({ fontWeight: "600" });
  });

  // 5. Header 01. PROJECTS link points to /projects and is active at /projects
  it("Header 01. PROJECTS link points to /projects and is active at /projects", async () => {
    renderAppAt("/projects");

    await waitFor(() => {
      expect(screen.getByText("PROJECTS. FIND THE SIGNAL.")).toBeInTheDocument();
    });

    const projectsNav = screen.getByRole("link", { name: "01. PROJECTS" });
    expect(projectsNav).toHaveAttribute("href", "/projects");
    expect(projectsNav).toHaveStyle({ fontWeight: "600" });
  });

  // 6. Header 02. ANALYTICS link points to /analytics and is active at /analytics
  it("Header 02. ANALYTICS link points to /analytics and is active at /analytics", async () => {
    renderAppAt("/analytics");

    await waitFor(() => {
      expect(screen.getByText("UNDERSTAND HOW THE PORTFOLIO MOVES.")).toBeInTheDocument();
    });

    const analyticsNav = screen.getByRole("link", { name: "02. ANALYTICS" });
    expect(analyticsNav).toHaveAttribute("href", "/analytics");
    expect(analyticsNav).toHaveStyle({ fontWeight: "600" });
  });

  // 7. Header 03. INTELLIGENCE link points to /intelligence and is active at /intelligence
  it("Header 03. INTELLIGENCE link points to /intelligence and is active at /intelligence", async () => {
    renderAppAt("/intelligence");

    await waitFor(() => {
      expect(screen.getByText("SEE THE RISK BEFORE IT BECOMES THE OUTCOME.")).toBeInTheDocument();
    });

    const intelNav = screen.getByRole("link", { name: "03. INTELLIGENCE" });
    expect(intelNav).toHaveAttribute("href", "/intelligence");
    expect(intelNav).toHaveStyle({ fontWeight: "600" });
  });

  // 8. Brand Logo points to /
  it("Brand logo points to / from any application route", () => {
    renderAppAt("/projects");

    const homeLogo = screen.getByRole("link", { name: "IRIS Home" });
    expect(homeLogo).toHaveAttribute("href", "/");
  });

  // 9. /projects/:projectCode keeps 01. PROJECTS active in Header
  it("Project detail at /projects/200101 keeps 01. PROJECTS active in Header", async () => {
    renderAppAt("/projects/200101");

    await waitFor(() => {
      expect(screen.getByText("Western Dedicated Freight Corridor")).toBeInTheDocument();
    });

    const projectsNav = screen.getByRole("link", { name: "01. PROJECTS" });
    expect(projectsNav).toHaveStyle({ fontWeight: "600" });
  });

  // 10. Dashboard contextual links to /analytics
  it("Dashboard provides contextual links to /analytics from Schedule and Cost sections", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
    });

    const scheduleAnalyticsLink = screen.getByRole("link", { name: "VIEW SCHEDULE ANALYTICS →" });
    expect(scheduleAnalyticsLink).toHaveAttribute("href", "/analytics");

    const costAnalyticsLink = screen.getByRole("link", { name: "VIEW COST ANALYTICS →" });
    expect(costAnalyticsLink).toHaveAttribute("href", "/analytics");
  });

  // 11. Dashboard contextual link to /intelligence
  it("Dashboard provides contextual link to /intelligence from Early Warning section", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
    });

    const fullRiskLink = screen.getByRole("link", { name: "VIEW FULL RISK INTELLIGENCE →" });
    expect(fullRiskLink).toHaveAttribute("href", "/intelligence");
  });

  // 12. Dashboard contextual link to /projects
  it("Dashboard provides contextual link to /projects from Composition section and project rows", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
    });

    const exploreProjectsLink = screen.getByRole("link", { name: "EXPLORE ALL PROJECTS →" });
    expect(exploreProjectsLink).toHaveAttribute("href", "/projects");

    await waitFor(() => {
      expect(screen.getByText("INSPECT")).toBeInTheDocument();
    });

    const inspectLink = screen.getByRole("link", { name: "INSPECT" });
    expect(inspectLink).toHaveAttribute("href", "/projects/200101");
  });

  // 13. Project Detail bottom nav links
  it("Project detail bottom nav provides links to Projects, Dashboard, Analytics, and Intelligence", async () => {
    renderAppAt("/projects/200101");

    await waitFor(() => {
      expect(screen.getByText("Western Dedicated Freight Corridor")).toBeInTheDocument();
    });

    const backLink = screen.getByRole("link", { name: "← BACK TO PROJECTS" });
    expect(backLink).toHaveAttribute("href", "/projects");

    const dashboardLink = screen.getByRole("link", { name: "DASHBOARD OVERVIEW" });
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");

    const analyticsLink = screen.getByRole("link", { name: "PORTFOLIO ANALYTICS" });
    expect(analyticsLink).toHaveAttribute("href", "/analytics");

    const intelLink = screen.getByRole("link", { name: "RISK INTELLIGENCE" });
    expect(intelLink).toHaveAttribute("href", "/intelligence");
  });

  // 14. Footer links verification
  it("Footer provides verified links to Overview, Projects, Analytics, Intelligence, and Documentation", async () => {
    renderAppAt("/");

    const footer = screen.getByRole("contentinfo", { name: "Institutional Footer" });
    const overviewLink = within(footer).getByRole("link", { name: "OVERVIEW" });
    expect(overviewLink).toHaveAttribute("href", "/dashboard");

    const docLink = within(footer).getByRole("link", { name: "DOCUMENTATION" });
    expect(docLink).toHaveAttribute("href", "/#data");
  });

  // 15. User interaction: clicking a navigation item updates route
  it("Navigates between pages when clicking header navigation links", async () => {
    renderAppAt("/dashboard");

    await waitFor(() => {
      expect(screen.getByText("INFRASTRUCTURE AT A GLANCE.")).toBeInTheDocument();
    });

    const projectsNavLink = screen.getByRole("link", { name: "01. PROJECTS" });
    fireEvent.click(projectsNavLink);

    await waitFor(() => {
      expect(screen.getByText("PROJECTS. FIND THE SIGNAL.")).toBeInTheDocument();
    });
  });

  // 16. Fallback 404 handler
  it("Renders 404 on unmapped route with return CTAs", () => {
    renderAppAt("/unmapped/route");

    expect(screen.getByTestId("unmapped-route")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("404 — Page Unmapped");
  });
});
