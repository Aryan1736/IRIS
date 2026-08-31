import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ProjectDetailPage } from "../../../pages/ProjectDetailPage";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import * as projectsApi from "@/api/projects.ts";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

// Mock the projects API
vi.mock("@/api/projects.ts", () => ({
  fetchProjectDetail: vi.fn(),
  fetchLatestSnapshot: vi.fn(),
  fetchProjectTrajectory: vi.fn(),
  fetchCostRevisions: vi.fn(),
  fetchScheduleExtensions: vi.fn(),
}));

describe("ProjectDetailPage", () => {
  beforeEach(() => {
    queryClient.clear();
    vi.clearAllMocks();

    vi.mocked(projectsApi.fetchProjectDetail).mockResolvedValue({
      project_code: "705635",
      project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
      agency: "NHAI",
      ministry: "MoRTH",
      sector: "Roads & Highways",
      state: "Kerala",
      first_reported_month: "2025-07",
      latest_report_month: "2026-07",
      total_observations_count: 13,
      latest_observation: {
        id: 101,
        project_code: "705635",
        legacy_ocms_code: null,
        pmgid: null,
        project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
        agency: "NHAI",
        ministry: "MoRTH",
        sector: "Roads & Highways",
        state: "Kerala",
        approval_date: "2023-01",
        start_date: "2023-03",
        original_completion_date: "2026-03",
        revised_completion_date: "2026-09",
        original_cost: 3450,
        revised_cost: null,
        cumulative_expenditure: 2210,
        physical_progress: 64.2,
        report_month: "2026-07",
        approval_date_raw: "01/2023",
        start_date_raw: "03/2023",
        original_completion_date_raw: "03/2026",
        revised_completion_date_raw: "09/2026",
        original_cost_raw: "3450",
        revised_cost_raw: null,
        cumulative_expenditure_raw: "2210",
        physical_progress_raw: "64.2",
        source_file: "REPORT_2026_07.pdf",
        source_page: 42,
        source_pages: "42",
        source_row_number: 14,
        source_serial_number: 142,
        extraction_method: "table6-eight-column-v1",
      },
    });

    vi.mocked(projectsApi.fetchLatestSnapshot).mockResolvedValue({
      id: 101,
      project_code: "705635",
      legacy_ocms_code: null,
      pmgid: null,
      project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
      agency: "NHAI",
      ministry: "MoRTH",
      sector: "Roads & Highways",
      state: "Kerala",
      approval_date: "2023-01",
      start_date: "2023-03",
      original_completion_date: "2026-03",
      revised_completion_date: "2026-09",
      original_cost: 3450,
      revised_cost: null,
      cumulative_expenditure: 2210,
      physical_progress: 64.2,
      report_month: "2026-07",
      approval_date_raw: "01/2023",
      start_date_raw: "03/2023",
      original_completion_date_raw: "03/2026",
      revised_completion_date_raw: "09/2026",
      original_cost_raw: "3450",
      revised_cost_raw: null,
      cumulative_expenditure_raw: "2210",
      physical_progress_raw: "64.2",
      source_file: "REPORT_2026_07.pdf",
      source_page: 42,
      source_pages: "42",
      source_row_number: 14,
      source_serial_number: 142,
      extraction_method: "table6-eight-column-v1",
    });

    vi.mocked(projectsApi.fetchProjectTrajectory).mockResolvedValue({
      project_code: "705635",
      project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
      observations_count: 2,
      trajectory: [
        {
          report_month: "2025-07",
          original_cost: 3450,
          revised_cost: null,
          cumulative_expenditure: 1200,
          physical_progress: 35.0,
          approval_date: "2023-01",
          start_date: "2023-03",
          original_completion_date: "2026-03",
          revised_completion_date: null,
          agency: "NHAI",
          ministry: "MoRTH",
          sector: "Roads & Highways",
          state: "Kerala",
        },
        {
          report_month: "2026-07",
          original_cost: 3450,
          revised_cost: null,
          cumulative_expenditure: 2210,
          physical_progress: 64.2,
          approval_date: "2023-01",
          start_date: "2023-03",
          original_completion_date: "2026-03",
          revised_completion_date: "2026-09",
          agency: "NHAI",
          ministry: "MoRTH",
          sector: "Roads & Highways",
          state: "Kerala",
        },
      ],
    });

    vi.mocked(projectsApi.fetchCostRevisions).mockResolvedValue({
      project_code: "705635",
      project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
      revisions: [
        {
          report_month: "2026-07",
          original_cost: 3450,
          revised_cost: null,
          cumulative_expenditure: 2210,
          original_cost_raw: "3450",
          revised_cost_raw: null,
          cumulative_expenditure_raw: "2210",
        },
      ],
      latest_original_cost: 3450,
      latest_revised_cost: null,
      cost_revision_ratio: null,
    });

    vi.mocked(projectsApi.fetchScheduleExtensions).mockResolvedValue({
      project_code: "705635",
      project_name: "TRIVANDRUM — KANYAKUMARI HIGHWAY",
      timeline: [
        {
          report_month: "2026-07",
          approval_date: "2023-01",
          start_date: "2023-03",
          original_completion_date: "2026-03",
          revised_completion_date: "2026-09",
          approval_date_raw: "01/2023",
          start_date_raw: "03/2023",
          original_completion_date_raw: "03/2026",
          revised_completion_date_raw: "09/2026",
        },
      ],
      latest_original_completion_date: "2026-03",
      latest_revised_completion_date: "2026-09",
    });
  });

  it("renders project detail header, snapshot metrics, trajectory, and all sections", async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/projects/705635"]}>
          <Routes>
            <Route path="/projects/:projectCode" element={<ProjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    // Header & Identity
    await waitFor(() => {
      expect(screen.getByText("TRIVANDRUM — KANYAKUMARI HIGHWAY")).toBeInTheDocument();
      expect(screen.getAllByText("705635").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("NHAI").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Kerala").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("Roads & Highways").length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText("13").length).toBeGreaterThanOrEqual(1);
    });

    // 6-Cell Overview Strip
    expect(screen.getAllByText("₹ 3,450 CR").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("2026-03").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("NOT REPORTED")).toBeInTheDocument();
    expect(screen.getAllByText("2026-09").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("64.2%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("₹ 2,210 CR").length).toBeGreaterThanOrEqual(1);

    // Section 01: Project History / Trajectory
    expect(screen.getByText("EVERY PROJECT HAS A HISTORY.")).toBeInTheDocument();
    expect(screen.getByText("PROJECT CODE + REPORT MONTH = OBSERVATION")).toBeInTheDocument();

    // Section 02: Schedule Movement
    expect(screen.getByText("WHERE THE SCHEDULE MOVES.")).toBeInTheDocument();
    expect(screen.getByText("+6 MONTHS")).toBeInTheDocument();

    // Section 03: Expenditure Trajectory
    expect(screen.getByText("FOLLOW THE MONEY.")).toBeInTheDocument();
    expect(screen.getByText("64.1%")).toBeInTheDocument(); // 2210 / 3450

    // Section 04: Project Signals (Factual without invented risk classifications)
    expect(screen.getByText("SEE THE SIGNALS.")).toBeInTheDocument();
    expect(screen.getByText("EXTENSION HISTORY")).toBeInTheDocument();
    expect(screen.getAllByText("2026-09").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("₹ 2,210 CR").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("64.2%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("13 OBSERVATIONS")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();

    // Section 05: Monthly Observations
    expect(screen.getByText("SOURCE RECORD.")).toBeInTheDocument();
    expect(screen.getByText("2 MONTHLY OBSERVATIONS")).toBeInTheDocument();

    // Section 06: Data Provenance
    expect(screen.getByText("BUILT FOR AUDITABILITY.")).toBeInTheDocument();
    expect(screen.getByText("REPORT_2026_07.pdf")).toBeInTheDocument();
    expect(screen.getByText("table6-eight-column-v1")).toBeInTheDocument();

    // Section 07: Navigation
    expect(screen.getByText("← BACK TO PROJECTS")).toBeInTheDocument();
  });

  it("handles 404 project not found gracefully", async () => {
    vi.mocked(projectsApi.fetchProjectDetail).mockRejectedValue(new Error("Project not found"));

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/projects/UNKNOWN-999"]}>
          <Routes>
            <Route path="/projects/:projectCode" element={<ProjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("PROJECT NOT FOUND: UNKNOWN-999")).toBeInTheDocument();
      expect(screen.getByText("← RETURN TO PROJECT DISCOVERY")).toBeInTheDocument();
    });
  });

  it("handles null and empty snapshot data gracefully with dashes", async () => {
    vi.mocked(projectsApi.fetchProjectDetail).mockResolvedValue({
      project_code: "999999",
      project_name: "UNPOPULATED METRIC PROJECT",
      agency: null,
      ministry: null,
      sector: null,
      state: null,
      first_reported_month: "2026-07",
      latest_report_month: "2026-07",
      total_observations_count: 1,
      latest_observation: {
        id: 202,
        project_code: "999999",
        legacy_ocms_code: null,
        pmgid: null,
        project_name: "UNPOPULATED METRIC PROJECT",
        agency: null,
        ministry: null,
        sector: null,
        state: null,
        approval_date: null,
        start_date: null,
        original_completion_date: null,
        revised_completion_date: null,
        original_cost: null,
        revised_cost: null,
        cumulative_expenditure: null,
        physical_progress: null,
        report_month: "2026-07",
        approval_date_raw: null,
        start_date_raw: null,
        original_completion_date_raw: null,
        revised_completion_date_raw: null,
        original_cost_raw: null,
        revised_cost_raw: null,
        cumulative_expenditure_raw: null,
        physical_progress_raw: null,
        source_file: null,
        source_page: null,
        source_pages: null,
        source_row_number: null,
        source_serial_number: null,
        extraction_method: null,
      },
    });

    vi.mocked(projectsApi.fetchLatestSnapshot).mockResolvedValue({
      id: 202,
      project_code: "999999",
      legacy_ocms_code: null,
      pmgid: null,
      project_name: "UNPOPULATED METRIC PROJECT",
      agency: null,
      ministry: null,
      sector: null,
      state: null,
      approval_date: null,
      start_date: null,
      original_completion_date: null,
      revised_completion_date: null,
      original_cost: null,
      revised_cost: null,
      cumulative_expenditure: null,
      physical_progress: null,
      report_month: "2026-07",
      approval_date_raw: null,
      start_date_raw: null,
      original_completion_date_raw: null,
      revised_completion_date_raw: null,
      original_cost_raw: null,
      revised_cost_raw: null,
      cumulative_expenditure_raw: null,
      physical_progress_raw: null,
      source_file: null,
      source_page: null,
      source_pages: null,
      source_row_number: null,
      source_serial_number: null,
      extraction_method: null,
    });

    vi.mocked(projectsApi.fetchProjectTrajectory).mockResolvedValue({
      project_code: "999999",
      project_name: "UNPOPULATED METRIC PROJECT",
      observations_count: 0,
      trajectory: [],
    });

    vi.mocked(projectsApi.fetchCostRevisions).mockResolvedValue({
      project_code: "999999",
      project_name: "UNPOPULATED METRIC PROJECT",
      revisions: [],
      latest_original_cost: null,
      latest_revised_cost: null,
      cost_revision_ratio: null,
    });

    vi.mocked(projectsApi.fetchScheduleExtensions).mockResolvedValue({
      project_code: "999999",
      project_name: "UNPOPULATED METRIC PROJECT",
      timeline: [],
      latest_original_completion_date: null,
      latest_revised_completion_date: null,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/projects/999999"]}>
          <Routes>
            <Route path="/projects/:projectCode" element={<ProjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText("UNPOPULATED METRIC PROJECT")).toBeInTheDocument();
      expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(4);
      expect(screen.getByText("NO SCHEDULE EXTENSION EVENTS RECORDED IN SOURCE DATA")).toBeInTheDocument();
      expect(screen.getByText("NO OBSERVATION RECORDS RECORDED")).toBeInTheDocument();
    });
  });
});
