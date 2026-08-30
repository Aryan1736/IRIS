/**
 * System & Health API Endpoints
 */

import { apiClient, API_BASE_URL } from "./client.ts";
import type { DatasetInfoResponse, DatasetServingStatus, HealthResponse } from "@/types/system.ts";

/**
 * Health check endpoint verifying app and database connectivity.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>(`${API_BASE_URL}/health`);
}

/**
 * Detailed database health check.
 */
export async function fetchHealthDb(): Promise<HealthResponse> {
  return apiClient<HealthResponse>(`${API_BASE_URL}/health/db`);
}

/**
 * System dataset metadata and serving verification.
 */
export async function fetchDatasetInfo(): Promise<DatasetInfoResponse> {
  return apiClient<DatasetInfoResponse>(`${API_BASE_URL}/system/dataset-info`);
}

/**
 * System dataset serving status check.
 */
export async function fetchServingStatus(): Promise<DatasetServingStatus> {
  return apiClient<DatasetServingStatus>(`${API_BASE_URL}/system/serving-status`);
}
