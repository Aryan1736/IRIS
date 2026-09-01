import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { IntelligencePage } from "@/pages/IntelligencePage.tsx";
import * as riskApi from "@/api/risk.ts";
import type {
  DashboardOptionsResponse,
  ModelInfoResponse,
  ProjectListResponse,
  SummaryResponse,
} from "@/types/risk.ts";

const mockOptions: DashboardOptionsResponse = {
  report_months: ["2026-03", "2026-04"],
  default_report_month: "2026-04",
  selected_report_month: "2026-04",
  regimes: ["MODERN"],
  sectors: ["Roads & Highways", "Railways"],
  agencies: ["NHAI", "RVNL"],
  ministries: ["Ministry of Road Transport & Highways"],
  states: ["Maharashtra", "Karnataka"],
};

const mockModelInfo: ModelInfoResponse = {
  serving_artifact_version: "iris_serving_v1_1",
  target: "target_effective_schedule_ext_3m",
  horizon_months: 3,
  status: "READY",
  models: [
    {
      regime: "MODERN",
      model_id: "logistic_static_only__unweighted",
      family: "L2-Regularized Logistic Regression",
      target: "target_effective_schedule_ext_3m",
      horizon_months: 3,
      features_count: 12,
      explanation_method: "LOGISTIC_COEFFICIENT_TIMES_TRANSFORMED_VALUE",
      calibration_policy: "Temporal Platt Scaling (active on 2026-04)",
      status: "READY",
    },
  ],
};

const mockSummary: SummaryResponse = {
  report_month: "2026-04",
  regime_filter: null,
  filters: {},
  project_count: 1625,
  score_distribution: {
    minimum: 0.000005,
    p25: 0.175,
    median: 0.401,
    p75: 0.606,
    p90: 0.690,
    p95: 0.719,
    maximum: 0.999,
    mean: 0.392,
  },
  top_risk_projects: [
    {
      project_code: "123456",
      project_name: "NH-48 Highway Expansion",
      agency: "NHAI",
      ministry: "Ministry of Road Transport & Highways",
      sector: "Roads & Highways",
      state: "Maharashtra",
      regime: "MODERN",
      model_id: "logistic_static_only__unweighted",
      raw_probability: 0.884,
      risk_probability: 0.999,
      calibration_active: true,
      risk_rank: 1,
      risk_percentile: 0.999,
      population_size: 1625,
    },
  ],
  regimes: [
    {
      regime: "MODERN",
      model_id: "logistic_static_only__unweighted",
      project_count: 1625,
      calibration_active: true,
    },
  ],
  sector_summary: [
    {
      sector: "Roads & Highways",
      project_count: 952,
      mean_risk_probability: 0.475,
      highest_risk_probability: 0.999,
    },
  ],
};

const mockProjects: ProjectListResponse = {
  report_month: "2026-04",
  filters: {},
  page: 1,
  page_size: 25,
  total: 1625,
  items: [
    {
      project_code: "123456",
      report_month: "2026-04",
      project_name: "NH-48 Highway Expansion",
      agency: "NHAI",
      ministry: "Ministry of Road Transport & Highways",
      sector: "Roads & Highways",
      state: "Maharashtra",
      regime: "MODERN",
      target: "target_effective_schedule_ext_3m",
      model_id: "logistic_static_only__unweighted",
      raw_probability: 0.884,
      risk_probability: 0.999,
      calibration_active: true,
      risk_percentile: 0.999,
      risk_rank: 1,
      population_size: 1625,
      top_positive_contributors: [
        {
          feature: "months_to_effective_schedule",
          display_name: "Months to effective schedule",
          value: "-42",
          contribution: 0.85,
          direction: "POSITIVE",
          rank: 1,
        },
      ],
      top_negative_contributors: [
        {
          feature: "sector",
          display_name: "Sector",
          value: "Roads & Highways",
          contribution: -0.28,
          direction: "NEGATIVE",
          rank: 1,
        },
      ],
      source_feature_values: {},
      version_metadata: {
        serving_contract_version: "1.1",
        serving_artifact_version: "iris_serving_v1_1",
        explanation_version: "v1",
        explanation_manifest_sha256: "abc",
        model_id: "logistic_static_only__unweighted",
        explanation_method: "LOGISTIC_COEFFICIENT_TIMES_TRANSFORMED_VALUE",
        contribution_space: "RAW_MARGIN_LOGIT",
        ranking_score_type: "OPERATIONAL_PROBABILITY",
      },
    },
  ],
};

describe("IntelligencePage Component", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    vi.spyOn(riskApi, "fetchRiskOptions").mockResolvedValue(mockOptions);
    vi.spyOn(riskApi, "fetchModelInfo").mockResolvedValue(mockModelInfo);
    vi.spyOn(riskApi, "fetchRiskSummary").mockResolvedValue(mockSummary);
    vi.spyOn(riskApi, "fetchRiskProjects").mockResolvedValue(mockProjects);
    vi.spyOn(riskApi, "fetchProjectRiskRecord").mockResolvedValue(mockProjects.items[0]);
    vi.spyOn(riskApi, "fetchProjectRiskHistory").mockResolvedValue({
      project_code: "123456",
      regime_filter: null,
      count: 1,
      items: mockProjects.items,
    });
  });

  const renderComponent = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <IntelligencePage />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders page intro, uppercase headline, and model governance telemetry", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("LIVE SERVING ACTIVE")).toBeInTheDocument();
    });

    expect(screen.getByText("SEE THE RISK BEFORE IT BECOMES THE OUTCOME.")).toBeInTheDocument();
    expect(screen.getByText("IRIS / INTELLIGENCE / EARLY WARNING")).toBeInTheDocument();
    expect(screen.getByText("SERVING READY")).toBeInTheDocument();
    expect(screen.getByText("H=3 MONTHS")).toBeInTheDocument();
    expect(screen.getByText("WALK-FORWARD")).toBeInTheDocument();
    expect(screen.getByText("2026-04")).toBeInTheDocument();
  });

  it("renders Section 01 overview with horizontal quantile band and real KPI metrics", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("1,625")).toBeInTheDocument();
    });

    expect(screen.getByText("01. Portfolio Risk Overview")).toBeInTheDocument();
    expect(screen.getByText("EARLY WARNING RISK PROFILE & EVALUATED POPULATION")).toBeInTheDocument();
    expect(screen.getAllByText("1,625").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("39.2%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("40.1%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("71.9%").length).toBeGreaterThanOrEqual(1);
  });

  it("renders Section 02 top risk bars and ranked projects table with authentic probabilities", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getAllByText("#1").length).toBeGreaterThanOrEqual(1);
    });

    expect(screen.getByText("02. Highest-Risk Projects")).toBeInTheDocument();
    expect(screen.getAllByText("123456").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("NH-48 Highway Expansion").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("99.9%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("RAW: 88.4%").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("CALIBRATION ACTIVE")).toBeInTheDocument();
    expect(screen.getAllByText("MODERN").length).toBeGreaterThanOrEqual(1);
  });

  it("renders Section 03 score distribution quantiles", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("MEDIAN (P50)")).toBeInTheDocument();
    });

    expect(screen.getByText("03. Model Output Distribution")).toBeInTheDocument();
    expect(screen.getByText("MINIMUM")).toBeInTheDocument();
    expect(screen.getByText("P95 (95TH)")).toBeInTheDocument();
  });

  it("renders Section 04 Sector Risk, Section 05 Regime, Section 06 Driver Intelligence, Section 08 Governance, Section 09 What the Model Knows, Section 10 Audit Trail", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("04. Risk by Sector")).toBeInTheDocument();
    });

    expect(screen.getByText("05. Risk by Regime")).toBeInTheDocument();
    expect(screen.getByText("06. Risk Driver Intelligence")).toBeInTheDocument();
    expect(screen.getByText("08. Model Governance")).toBeInTheDocument();
    expect(screen.getByText("09. What the Model Knows")).toBeInTheDocument();
    expect(screen.getByText("10. Model Status / Audit Trail")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("iris_serving_v1_1")).toBeInTheDocument();
    });
  });

  it("opens inspection drawer, closes on Escape, and renders signed contributors", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getAllByText("INSPECT").length).toBeGreaterThanOrEqual(1);
    });

    fireEvent.click(screen.getAllByText("INSPECT")[0]);

    await waitFor(() => {
      expect(screen.getByText("PROJECT RISK INSPECTION CONSOLE")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText("+0.85")).toBeInTheDocument();
    });

    expect(screen.getByText("Signed Feature Drivers (Model Contributions)")).toBeInTheDocument();
    expect(screen.getByText("-0.28")).toBeInTheDocument();
    expect(screen.getByText("VIEW FULL PROJECT →")).toBeInTheDocument();

    // Verify closing on Escape
    fireEvent.keyDown(window, { key: "Escape" });
    await waitFor(() => {
      expect(screen.queryByText("PROJECT RISK INSPECTION CONSOLE")).not.toBeInTheDocument();
    });
  });

  it("allows selecting a different report month and refetches data", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("LIVE SERVING ACTIVE")).toBeInTheDocument();
    });

    const select = screen.getByLabelText("Evaluation Month");
    fireEvent.change(select, { target: { value: "2026-03" } });

    await waitFor(() => {
      expect(riskApi.fetchRiskSummary).toHaveBeenCalledWith(
        expect.objectContaining({ report_month: "2026-03" })
      );
    });
  });
});
