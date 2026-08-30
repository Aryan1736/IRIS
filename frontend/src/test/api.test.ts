import { describe, it, expect, vi, beforeEach } from "vitest";
import { buildQueryString } from "@/api/client.ts";
import { fetchProjects, fetchFilterOptions } from "@/api/projects.ts";
import { fetchRiskSummary } from "@/api/risk.ts";
import { fetchHealth } from "@/api/system.ts";

describe("API Client & Query String Utilities", () => {
  it("builds query strings omitting null, undefined, and empty string params", () => {
    const qs = buildQueryString({
      page: 1,
      page_size: 20,
      sector: "Road Transport and Highways",
      empty: "",
      nil: null,
      undef: undefined,
    });
    expect(qs).toBe("?page=1&page_size=20&sector=Road+Transport+and+Highways");
  });

  it("returns empty string when params are empty or null", () => {
    expect(buildQueryString()).toBe("");
    expect(buildQueryString({})).toBe("");
    expect(buildQueryString({ a: null, b: undefined })).toBe("");
  });
});

describe("API Module Contract Calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("fetchProjects makes GET request with correct params", async () => {
    const mockResponse = {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers(),
      json: async () => mockResponse,
    } as Response);

    const result = await fetchProjects({ page: 2, sector: "Power" });

    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/v1/projects?page=2&page_size=20&sector=Power",
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: "application/json" }),
      })
    );
    expect(result.page).toBe(1); // returned mock
  });

  it("fetchFilterOptions retrieves dynamic filter categories", async () => {
    const mockFilters = {
      sectors: ["Roads", "Power"],
      states: ["Maharashtra", "Gujarat"],
      agencies: ["NHAI"],
      ministries: ["MORTH"],
      report_months: ["2026-07"],
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers(),
      json: async () => mockFilters,
    } as Response);

    const result = await fetchFilterOptions();
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/v1/projects/filters/options",
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: "application/json" }),
      })
    );
    expect(result.sectors).toContain("Roads");
  });

  it("fetchRiskSummary calls /risk/summary with correct parameters", async () => {
    const mockSummary = {
      report_month: "2026-07",
      regime_filter: null,
      filters: {},
      project_count: 50,
      score_distribution: { minimum: 0.1, p25: 0.2, median: 0.3, p75: 0.5, p90: 0.7, p95: 0.8, maximum: 0.9, mean: 0.4 },
      top_risk_projects: [],
      regimes: [],
      sector_summary: [],
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers(),
      json: async () => mockSummary,
    } as Response);

    const result = await fetchRiskSummary({ report_month: "2026-07", top_n: 15 });

    expect(fetchSpy).toHaveBeenCalledWith(
      "/risk/summary?report_month=2026-07&top_n=15",
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: "application/json" }),
      })
    );
    expect(result.report_month).toBe("2026-07");
  });

  it("fetchHealth queries the system health endpoint", async () => {
    const mockHealth = {
      status: "healthy",
      app: "IRIS API",
      database: { connected: true },
      version: "0.1.0",
      environment: "development",
      timestamp: "2026-08-30T12:00:00Z",
    };

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers(),
      json: async () => mockHealth,
    } as Response);

    const result = await fetchHealth();
    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/v1/health",
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: "application/json" }),
      })
    );
    expect(result.status).toBe("healthy");
  });
});
