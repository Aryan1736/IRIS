/**
 * IRIS Resilient API Client
 */

import { ApiError, ApiErrorResponse } from "@/types/api.ts";

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | null | undefined>;
}

export const API_BASE_URL = "/api/v1";
export const RISK_BASE_URL = "/risk";

/**
 * Builds a query string omitting null and undefined values.
 */
export function buildQueryString(params?: Record<string, string | number | boolean | null | undefined>): string {
  if (!params) return "";
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      searchParams.append(key, String(value));
    }
  }
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

/**
 * Generic JSON fetcher with error normalization.
 */
export async function apiClient<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers: customHeaders, ...customOptions } = options;
  const url = `${endpoint}${buildQueryString(params)}`;

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };

  if (customOptions.body && typeof customOptions.body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    ...customOptions,
    headers,
  });

  const requestId = response.headers.get("X-Request-ID") || undefined;

  if (!response.ok) {
    let errorCode = "HTTP_ERROR";
    let errorMessage = `Request failed with status ${response.status}: ${response.statusText}`;
    let details: Record<string, unknown> | undefined;

    try {
      const errorJson = (await response.json()) as ApiErrorResponse | { detail?: string | Record<string, unknown> };
      if ("error" in errorJson && errorJson.error) {
        errorCode = errorJson.error.code || errorCode;
        errorMessage = errorJson.error.message || errorMessage;
        details = errorJson.error.details as Record<string, unknown>;
      } else if ("detail" in errorJson && errorJson.detail) {
        if (typeof errorJson.detail === "string") {
          errorMessage = errorJson.detail;
        } else {
          details = errorJson.detail as Record<string, unknown>;
        }
      }
    } catch {
      // Non-JSON error body, preserve default message
    }

    throw new ApiError(response.status, errorMessage, errorCode, details, requestId);
  }

  // Handle empty 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
