/**
 * Project TypeScript interfaces strictly mirroring FastAPI schemas in backend/app/schemas/
 */

export interface ProjectMonthObservationRead {
  id: number;
  project_code: string;
  legacy_ocms_code: string | null;
  pmgid: string | null;
  project_name: string;
  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;

  approval_date: string | null;
  start_date: string | null;
  original_completion_date: string | null;
  revised_completion_date: string | null;

  original_cost: number | null;
  revised_cost: number | null;
  cumulative_expenditure: number | null;
  physical_progress: number | null;

  report_month: string;

  approval_date_raw: string | null;
  start_date_raw: string | null;
  original_completion_date_raw: string | null;
  revised_completion_date_raw: string | null;
  original_cost_raw: string | null;
  revised_cost_raw: string | null;
  cumulative_expenditure_raw: string | null;
  physical_progress_raw: string | null;

  source_file: string | null;
  source_page: number | null;
  source_pages: string | null;
  source_row_number: number | null;
  source_serial_number: number | null;
  extraction_method: string | null;
  created_at?: string | null;
}

export interface ProjectSummaryItem {
  id: number;
  project_code: string;
  project_name: string;
  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;
  report_month: string;

  approval_date: string | null;
  original_completion_date: string | null;
  revised_completion_date: string | null;

  original_cost: number | null;
  revised_cost: number | null;
  cumulative_expenditure: number | null;
  physical_progress: number | null;
}

export interface PaginatedProjectsResponse {
  items: ProjectSummaryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FilterOptionsResponse {
  sectors: string[];
  states: string[];
  agencies: string[];
  ministries: string[];
  report_months: string[];
}

export interface QuickSearchResult {
  project_code: string;
  project_name: string;
  agency: string | null;
  latest_report_month: string;
}

export interface ProjectDetailResponse {
  project_code: string;
  project_name: string;
  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;
  first_reported_month: string;
  latest_report_month: string;
  total_observations_count: intNumber;
  latest_observation: ProjectMonthObservationRead;
}

type intNumber = number;

export interface ProjectTrajectoryPoint {
  report_month: string;
  original_cost: number | null;
  revised_cost: number | null;
  cumulative_expenditure: number | null;
  physical_progress: number | null;

  approval_date: string | null;
  start_date: string | null;
  original_completion_date: string | null;
  revised_completion_date: string | null;

  agency: string | null;
  ministry: string | null;
  sector: string | null;
  state: string | null;
}

export interface ProjectTrajectoryResponse {
  project_code: string;
  project_name: string;
  observations_count: number;
  trajectory: ProjectTrajectoryPoint[];
}

export interface CostRevisionPoint {
  report_month: string;
  original_cost: number | null;
  revised_cost: number | null;
  cumulative_expenditure: number | null;
  original_cost_raw: string | null;
  revised_cost_raw: string | null;
  cumulative_expenditure_raw: string | null;
}

export interface ProjectCostRevisionsResponse {
  project_code: string;
  project_name: string;
  revisions: CostRevisionPoint[];
  latest_original_cost: number | null;
  latest_revised_cost: number | null;
  cost_revision_ratio: number | null;
}

export interface ScheduleExtensionPoint {
  report_month: string;
  approval_date: string | null;
  start_date: string | null;
  original_completion_date: string | null;
  revised_completion_date: string | null;
  approval_date_raw: string | null;
  start_date_raw: string | null;
  original_completion_date_raw: string | null;
  revised_completion_date_raw: string | null;
}

export interface ProjectScheduleExtensionsResponse {
  project_code: string;
  project_name: string;
  timeline: ScheduleExtensionPoint[];
  latest_original_completion_date: string | null;
  latest_revised_completion_date: string | null;
  extensions?: ScheduleExtensionPoint[];
  latest_original_completion?: string | null;
  latest_revised_completion?: string | null;
}

export type SortByFields =
  | "report_month"
  | "project_name"
  | "project_code"
  | "original_cost"
  | "revised_cost"
  | "cumulative_expenditure"
  | "physical_progress"
  | "approval_date"
  | "original_completion_date"
  | "revised_completion_date";

export type SortOrder = "asc" | "desc";

export interface ProjectListQueryParams {
  page?: number;
  page_size?: number;
  project_code?: string;
  report_month?: string;
  sector?: string;
  state?: string;
  agency?: string;
  ministry?: string;
  search?: string;
  sort_by?: SortByFields;
  sort_order?: SortOrder;
}
