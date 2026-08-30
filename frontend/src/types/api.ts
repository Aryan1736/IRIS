/**
 * Generic API types, parameter filters, and error responses.
 */

export interface ErrorDetail {
  loc?: (string | number)[];
  msg: string;
  type?: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: ErrorDetail[] | Record<string, unknown>;
  };
  request_id?: string;
}

export class ApiError extends Error {
  public status: number;
  public code: string;
  public details?: ErrorDetail[] | Record<string, unknown>;
  public requestId?: string;

  constructor(status: number, message: string, code = "API_ERROR", details?: ErrorDetail[] | Record<string, unknown>, requestId?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
  }
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}
