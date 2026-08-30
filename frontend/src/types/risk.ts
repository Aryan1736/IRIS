/**
 * Risk Intelligence & Model Serving types strictly mirroring src/serving/schemas.py
 */

export type Regime = "LEGACY" | "MODERN";

export type ExplanationMethod =
  | "CATBOOST_NATIVE_TREESHAP"
  | "LOGISTIC_COEFFICIENT_TIMES_TRANSFORMED_VALUE";

export interface Contributor {
  feature: string;
  display_name: string;
  value: string | null;
  contribution: number;
  direction: "POSITIVE" | "NEGATIVE";
  rank: number;
}

export interface VersionMetadata {
  serving_contract_version: string;
  serving_artifact_version: string;
  explanation_version: string;
  explanation_manifest_sha256: string;
  model_id: string;
  explanation_method: ExplanationMethod;
  contribution_space: "RAW_MARGIN_LOGIT";
  ranking_score_type: "OPERATIONAL_PROBABILITY";
}

export interface RiskRecord {
  project_code: string;
  report_month: string;
  project_name: string | null;
  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;
  regime: Regime;
  target: "target_effective_schedule_ext_3m";
  model_id: string;
  raw_probability: number;
  risk_probability: number;
  calibration_active: boolean;
  risk_percentile: number;
  risk_rank: number;
  population_size: number;
  top_positive_contributors: Contributor[];
  top_negative_contributors: Contributor[];
  source_feature_values: Record<string, string | null>;
  version_metadata: VersionMetadata;
}

export interface ScoreDistribution {
  minimum: number;
  p25: number;
  median: number;
  p75: number;
  p90: number;
  p95: number;
  maximum: number;
  mean: number;
}

export interface TopRiskProject {
  project_code: string;
  project_name: string | null;
  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;
  regime: Regime;
  model_id: string;
  raw_probability: number;
  risk_probability: number;
  calibration_active: boolean;
  risk_rank: number;
  risk_percentile: number;
  population_size: number;
}

export interface RegimeMetadata {
  regime: Regime;
  model_id: string;
  project_count: number;
  calibration_active: boolean;
}

export interface SectorSummary {
  sector: string | null;
  project_count: number;
  mean_risk_probability: number;
  highest_risk_probability: number;
}

export interface DashboardOptionsResponse {
  report_months: string[];
  default_report_month: string;
  selected_report_month: string;
  regimes: Regime[];
  sectors: string[];
  agencies: string[];
  ministries: string[];
  states: string[];
}

export interface RiskFilters {
  regime?: Regime | null;
  min_risk_probability?: number | null;
  max_risk_probability?: number | null;
  sector?: string | null;
  agency?: string | null;
  ministry?: string | null;
  state?: string | null;
  search?: string | null;
}

export interface SummaryResponse {
  report_month: string;
  regime_filter: Regime | null;
  filters: RiskFilters;
  project_count: number;
  score_distribution: ScoreDistribution;
  top_risk_projects: TopRiskProject[];
  regimes: RegimeMetadata[];
  sector_summary: SectorSummary[];
}

export interface ProjectListResponse {
  report_month: string;
  filters: RiskFilters;
  page: number;
  page_size: number;
  total: number;
  items: RiskRecord[];
}

export interface HistoryResponse {
  project_code: string;
  regime_filter: Regime | null;
  count: number;
  items: RiskRecord[];
}

export interface ModelDetail {
  regime: Regime;
  model_id: string;
  family: string;
  target: "target_effective_schedule_ext_3m";
  horizon_months: number;
  features_count: number;
  explanation_method: ExplanationMethod;
  calibration_policy: string;
  status: "READY" | "NOT_TRAINED" | "MODEL_NOT_DEPLOYED";
}

export interface ModelInfoResponse {
  serving_artifact_version: string;
  target: "target_effective_schedule_ext_3m";
  horizon_months: number;
  status: "READY" | "NOT_TRAINED" | "MODEL_NOT_DEPLOYED";
  models: ModelDetail[];
}

export interface RiskSummaryQueryParams {
  report_month: string;
  regime?: Regime;
  top_n?: number;
  sector?: string;
  agency?: string;
  ministry?: string;
  state?: string;
  search?: string;
}

export interface RiskListQueryParams {
  report_month: string;
  page?: number;
  page_size?: number;
  regime?: Regime;
  min_risk_probability?: number;
  max_risk_probability?: number;
  sector?: string;
  agency?: string;
  ministry?: string;
  state?: string;
  search?: string;
}
