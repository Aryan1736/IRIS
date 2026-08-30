/**
 * Project API Endpoints
 */

import { apiClient, API_BASE_URL } from "./client.ts";
import type {
  FilterOptionsResponse,
  PaginatedProjectsResponse,
  ProjectCostRevisionsResponse,
  ProjectDetailResponse,
  ProjectListQueryParams,
  ProjectMonthObservationRead,
  ProjectScheduleExtensionsResponse,
  ProjectTrajectoryResponse,
  QuickSearchResult,
} from "@/types/project.ts";

/**
 * List projects with pagination, sorting, and multi-field filtering.
 */
export async function fetchProjects(params: ProjectListQueryParams = {}): Promise<PaginatedProjectsResponse> {
  return apiClient<PaginatedProjectsResponse>(`${API_BASE_URL}/projects`, {
    params: {
      page: params.page ?? 1,
      page_size: params.page_size ?? 20,
      project_code: params.project_code,
      report_month: params.report_month,
      sector: params.sector,
      state: params.state,
      agency: params.agency,
      ministry: params.ministry,
      search: params.search,
      sort_by: params.sort_by,
      sort_order: params.sort_order,
    },
  });
}

/**
 * Retrieve dynamic filter options (sectors, states, agencies, ministries, months).
 */
export async function fetchFilterOptions(): Promise<FilterOptionsResponse> {
  return apiClient<FilterOptionsResponse>(`${API_BASE_URL}/projects/filters/options`);
}

/**
 * Lightweight autocomplete/quick search for projects.
 */
export async function fetchQuickSearch(query: string, limit = 10): Promise<QuickSearchResult[]> {
  return apiClient<QuickSearchResult[]>(`${API_BASE_URL}/projects/search/quick`, {
    params: { q: query, limit },
  });
}

/**
 * Retrieve project high-level summary and latest observation by project code.
 */
export async function fetchProjectDetail(projectCode: string): Promise<ProjectDetailResponse> {
  return apiClient<ProjectDetailResponse>(`${API_BASE_URL}/projects/${encodeURIComponent(projectCode)}`);
}

/**
 * Retrieve complete 31-field latest observation snapshot.
 */
export async function fetchLatestSnapshot(projectCode: string): Promise<ProjectMonthObservationRead> {
  return apiClient<ProjectMonthObservationRead>(
    `${API_BASE_URL}/projects/${encodeURIComponent(projectCode)}/latest-snapshot`
  );
}

/**
 * Retrieve full chronological timeline of monthly observations.
 */
export async function fetchProjectTrajectory(projectCode: string): Promise<ProjectTrajectoryResponse> {
  return apiClient<ProjectTrajectoryResponse>(
    `${API_BASE_URL}/projects/${encodeURIComponent(projectCode)}/trajectory`
  );
}

/**
 * Retrieve historical original vs revised cost vs cumulative expenditure observations.
 */
export async function fetchCostRevisions(projectCode: string): Promise<ProjectCostRevisionsResponse> {
  return apiClient<ProjectCostRevisionsResponse>(
    `${API_BASE_URL}/projects/${encodeURIComponent(projectCode)}/cost-revisions`
  );
}

/**
 * Retrieve historical milestone schedule extensions and completion dates.
 */
export async function fetchScheduleExtensions(projectCode: string): Promise<ProjectScheduleExtensionsResponse> {
  return apiClient<ProjectScheduleExtensionsResponse>(
    `${API_BASE_URL}/projects/${encodeURIComponent(projectCode)}/schedule-extensions`
  );
}
