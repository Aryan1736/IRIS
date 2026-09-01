import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ProjectSearch } from "../../../components/projects/ProjectSearch";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

// Mock the API call
vi.mock("@/api/projects.ts", () => ({
  fetchFilterOptions: vi.fn(() =>
    Promise.resolve({
      sectors: ["Transport", "Energy"],
      agencies: ["Metro Auth", "EPA"],
      states: ["NY", "WA"],
      ministries: ["Ministry of Power"],
      report_months: ["2024-01", "2024-02"],
    })
  ),
}));

describe("ProjectSearch", () => {
  it("renders search input and taxonomy filter options", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{}} onFilterChange={() => {}} />
      </QueryClientProvider>
    );

    expect(screen.getByPlaceholderText(/SEARCH PROJECT NAME/i)).toBeInTheDocument();
    expect(screen.getByText("SECTOR (ALL)")).toBeInTheDocument();
    expect(screen.getByText("AGENCY (ALL)")).toBeInTheDocument();
    expect(screen.getByText("STATE / REGION (ALL)")).toBeInTheDocument();
  });

  it("calls onFilterChange when search input changes with debounce", async () => {
    const onFilterChange = vi.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{}} onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/SEARCH PROJECT NAME/i), {
      target: { value: "Metro" },
    });

    await waitFor(() => {
      expect(onFilterChange).toHaveBeenCalledWith({ search: "Metro" });
    });
  });

  it("shows active filter criteria pills and CLEAR FILTERS button when filters are active", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{ sector: "Transport" }} onFilterChange={() => {}} />
      </QueryClientProvider>
    );
    expect(screen.getByText("CLEAR FILTERS")).toBeInTheDocument();
    expect(screen.getByText("ACTIVE CRITERIA:")).toBeInTheDocument();
    expect(screen.getAllByText("Transport").length).toBeGreaterThanOrEqual(1);
  });

  it("clears filters when CLEAR FILTERS is clicked", () => {
    const onFilterChange = vi.fn();
    render(
      <QueryClientProvider client={queryClient}>
        <ProjectSearch filters={{ sector: "Transport" }} onFilterChange={onFilterChange} />
      </QueryClientProvider>
    );

    fireEvent.click(screen.getByText("CLEAR FILTERS"));
    expect(onFilterChange).toHaveBeenCalledWith({});
  });
});
