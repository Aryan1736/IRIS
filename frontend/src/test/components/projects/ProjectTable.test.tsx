import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ProjectTable } from "../../../components/projects/ProjectTable";
import { BrowserRouter } from "react-router-dom";

describe("ProjectTable", () => {
  const mockProjects = [
    {
      id: 1,
      project_code: "PRJ-2023-UTX",
      project_name: "Urban Transit Expansion",
      agency: "Metro Auth",
      ministry: "Ministry of Housing",
      sector: "Transport",
      state: "NY",
      report_month: "2024-02",
      approval_date: "2020-01",
      original_completion_date: "2024-12",
      revised_completion_date: null,
      original_cost: 1200.0,
      revised_cost: null,
      cumulative_expenditure: 550.0,
      physical_progress: 45.5,
    },
    {
      id: 2,
      project_code: "PRJ-2022-NGM",
      project_name: "Northern Grid",
      agency: null,
      ministry: null,
      sector: "Energy",
      state: null,
      report_month: "2024-01",
      approval_date: null,
      original_completion_date: null,
      revised_completion_date: null,
      original_cost: null,
      revised_cost: null,
      cumulative_expenditure: null,
      physical_progress: null, // Null physical progress
    },
  ];

  it("renders table headers", () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={[]} />
      </BrowserRouter>
    );

    expect(screen.getByText("PROJECT")).toBeInTheDocument();
    expect(screen.getByText("PROJECT CODE")).toBeInTheDocument();
    expect(screen.getByText("SECTOR")).toBeInTheDocument();
    expect(screen.getByText("AGENCY")).toBeInTheDocument();
    expect(screen.getByText("STATE / REGION")).toBeInTheDocument();
    expect(screen.getByText("LATEST REPORT")).toBeInTheDocument();
    expect(screen.getByText("PHYSICAL PROGRESS")).toBeInTheDocument();
  });

  it("renders project data correctly with authentic progress values and bars", () => {
    render(
      <BrowserRouter>
        <ProjectTable projects={mockProjects} />
      </BrowserRouter>
    );

    expect(screen.getByText("Urban Transit Expansion")).toBeInTheDocument();
    expect(screen.getByText("PRJ-2023-UTX")).toBeInTheDocument();
    expect(screen.getByText("Transport")).toBeInTheDocument();
    expect(screen.getByText("NY")).toBeInTheDocument();
    expect(screen.getByText("45.5%")).toBeInTheDocument();

    const progressbar = screen.getByRole("progressbar");
    expect(progressbar).toHaveAttribute("aria-valuenow", "45.5");

    expect(screen.getByText("Northern Grid")).toBeInTheDocument();
    expect(screen.getByText("PRJ-2022-NGM")).toBeInTheDocument();
    expect(screen.getByText("Energy")).toBeInTheDocument();

    // Check "—" fallback for null physical progress
    const fallbacks = screen.getAllByText("—");
    expect(fallbacks.length).toBeGreaterThan(0);
  });

  it("triggers onInspect callback when inspect button is clicked", () => {
    const onInspect = vi.fn();
    render(
      <BrowserRouter>
        <ProjectTable projects={mockProjects} onInspect={onInspect} />
      </BrowserRouter>
    );

    const inspectButtons = screen.getAllByText("INSPECT");
    fireEvent.click(inspectButtons[0]);
    expect(onInspect).toHaveBeenCalledWith(mockProjects[0]);
  });

  it("displays empty state with reset button when no projects provided", () => {
    const onReset = vi.fn();
    render(
      <BrowserRouter>
        <ProjectTable projects={[]} onResetFilters={onReset} />
      </BrowserRouter>
    );

    expect(screen.getByText("NO PROJECTS FOUND MATCHING CURRENT QUERY")).toBeInTheDocument();
    const resetBtn = screen.getByText("RESET SEARCH & CLEAR ALL FILTERS");
    fireEvent.click(resetBtn);
    expect(onReset).toHaveBeenCalled();
  });
});
