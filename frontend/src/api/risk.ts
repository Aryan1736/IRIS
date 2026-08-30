/**
 * Risk Intelligence API Endpoints
 */

import { apiClient, RISK_BASE_URL } from "./client.ts";
import type {
  DashboardOptionsResponse,
  HistoryResponse,
  ModelInfoResponse,
  ProjectListResponse,
  Regime,
  RiskListQueryParams,
  RiskRecord,
  RiskSummaryQueryParams,
  SummaryResponse,
} from "@/types/risk.ts";

/**
 * Retrieve risk dashboard options (report months, default month, regimes, metadata values).
 */
export async function fetchRiskOptions(reportMonth?: string): Promise<DashboardOptionsResponse> {
  return apiClient<DashboardOptionsResponse>(`${RISK_BASE_URL}/options`, {
    params: { report_month: reportMonth },
  });
}

/**
 * Retrieve portfolio-level risk summary, score distribution, quantiles, and sector summaries.
 */
export async function fetchRiskSummary(params: RiskSummaryQueryParams): Promise<SummaryResponse> {
  return apiClient<SummaryResponse>(`${RISK_BASE_URL}/summary`, {
    params: {
      report_month: params.report_month,
      regime: params.regime,
      top_n: params.top_n ?? 10,
      sector: params.sector,
      agency: params.agency,
      ministry: params.ministry,
      state: params.state,
      search: params.search,
    },
  });
}

/**
 * List ranked projects with calibrated probabilities and signed TreeSHAP/logistic contributors.
 */
export async function fetchRiskProjects(params: RiskListQueryParams): Promise<ProjectListResponse> {
  return apiClient<ProjectListResponse>(`${RISK_BASE_URL}/projects`, {
    params: {
      report_month: params.report_month,
      page: params.page ?? 1,
      page_size: params.page_size ?? 25,
      regime: params.regime,
      min_risk_probability: params.min_risk_probability,
      max_risk_probability: params.max_risk_probability,
      sector: params.sector,
      agency: params.agency,
      ministry: params.ministry,
      state: params.state,
      search: params.search,
    },
  });
}

/**
 * Retrieve model governance, feature metadata, explanation methods, and calibration policies.
 */
export async function fetchModelInfo(): Promise<ModelInfoResponse> {
  return apiClient<ModelInfoResponse>(`${RISK_BASE_URL}/model-info`);
}

/**
 * Retrieve exact project-month risk record with full explainability contributors.
 */
export async function fetchProjectRiskRecord(projectCode: string, reportMonth: string): Promise<RiskRecord> {
  return apiClient<RiskRecord>(`${RISK_BASE_URL}/project/${encodeURIComponent(projectCode)}`, {
    params: { report_month: reportMonth },
  });
}

/**
 * Retrieve exact project risk history across all evaluated months.
 */
export async function fetchProjectRiskHistory(projectCode: string, regime?: Regime): Promise<HistoryResponse> {
  return apiClient<HistoryResponse>(`${RISK_BASE_URL}/project/${encodeURIComponent(projectCode)}/history`, {
    params: { regime },
  });
}
