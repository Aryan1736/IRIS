/**
 * System & Health status types mirroring backend/app/schemas/system.py and health.py
 */

export interface DatabaseStatus {
  connected: boolean;
  pool_size?: number;
  latency_ms?: number;
}

export interface HealthResponse {
  status: "healthy" | "unhealthy" | "degraded";
  app: string;
  database: DatabaseStatus;
  version: string;
  environment: string;
  timestamp: string;
}

export interface DatasetInfoResponse {
  status: "ACTIVE" | "NOT_INGESTED" | "INGESTED_UNVERIFIED" | "SUPERSEDED" | "ARCHIVED";
  dataset_version?: string | null;
  canonical_sha256?: string | null;
  covered_months: string[];
  row_count: number;
  unique_projects_count: number | null;
  source_version_identifier?: string | null;
  ingested_at?: string | null;
}

export interface DatasetServingStatus {
  is_serving: boolean;
  dataset_loaded: boolean;
  message: string;
}
