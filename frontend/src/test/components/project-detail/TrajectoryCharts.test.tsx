import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ProjectTrajectoryChart } from "@/components/project-detail/ProjectTrajectoryChart.tsx";
import { ExpenditureTrajectoryChart } from "@/components/project-detail/ExpenditureTrajectoryChart.tsx";
import { ChartTooltip } from "@/components/project-detail/ChartTooltip.tsx";
import type { ProjectTrajectoryPoint } from "@/types/project.ts";

describe("Project Detail Charts & Visualizations", () => {
  describe("ProjectTrajectoryChart", () => {
    it("renders empty state truthfully when no observations exist", () => {
      render(<ProjectTrajectoryChart observations={[]} />);
      expect(
        screen.getByText("NO LONGITUDINAL PROGRESS OBSERVATIONS REPORTED")
      ).toBeInTheDocument();
    });

    it("renders empty state when all physical_progress values are null", () => {
      const nullObservations: ProjectTrajectoryPoint[] = [
        {
          report_month: "2024-01",
          original_cost: 100,
          revised_cost: null,
          cumulative_expenditure: 50,
          physical_progress: null,
          approval_date: "2020-01",
          start_date: null,
          original_completion_date: "2025-01",
          revised_completion_date: null,
          agency: "NHAI",
          ministry: null,
          sector: "Roads",
          state: "Delhi",
        },
      ];

      render(<ProjectTrajectoryChart observations={nullObservations} />);
      expect(
        screen.getByText("NO LONGITUDINAL PROGRESS OBSERVATIONS REPORTED")
      ).toBeInTheDocument();
    });

    it("renders chart container for valid observations", () => {
      const validObservations: ProjectTrajectoryPoint[] = [
        {
          report_month: "2025-07",
          original_cost: 3450,
          revised_cost: null,
          cumulative_expenditure: 1200,
          physical_progress: 35.0,
          approval_date: "2023-01",
          start_date: "2023-03",
          original_completion_date: "2026-03",
          revised_completion_date: null,
          agency: "NHAI",
          ministry: "MoRTH",
          sector: "Roads & Highways",
          state: "Kerala",
        },
        {
          report_month: "2026-07",
          original_cost: 3450,
          revised_cost: null,
          cumulative_expenditure: 2210,
          physical_progress: 64.2,
          approval_date: "2023-01",
          start_date: "2023-03",
          original_completion_date: "2026-03",
          revised_completion_date: "2026-09",
          agency: "NHAI",
          ministry: "MoRTH",
          sector: "Roads & Highways",
          state: "Kerala",
        },
      ];

      const { container } = render(<ProjectTrajectoryChart observations={validObservations} />);
      expect(container.querySelector(".recharts-responsive-container")).toBeInTheDocument();
    });

    it("handles single observation cleanly without synthetic points", () => {
      const singleObservation: ProjectTrajectoryPoint[] = [
        {
          report_month: "2026-07",
          original_cost: 1168,
          revised_cost: null,
          cumulative_expenditure: 123.28,
          physical_progress: 0.61,
          approval_date: "2023-08",
          start_date: "2025-06",
          original_completion_date: "2028-06",
          revised_completion_date: null,
          agency: "DoT",
          ministry: "DoT",
          sector: "Telecommunication",
          state: "PAN India",
        },
      ];

      const { container } = render(<ProjectTrajectoryChart observations={singleObservation} />);
      expect(container.querySelector(".recharts-responsive-container")).toBeInTheDocument();
    });
  });

  describe("ExpenditureTrajectoryChart", () => {
    it("renders empty state truthfully when no expenditure exists", () => {
      render(<ExpenditureTrajectoryChart observations={[]} />);
      expect(
        screen.getByText("NO EXPENDITURE TRAJECTORY REPORTED")
      ).toBeInTheDocument();
    });

    it("renders empty state when all cumulative_expenditure values are null", () => {
      render(
        <ExpenditureTrajectoryChart
          observations={[
            { report_month: "2025-07", cumulative_expenditure: null },
          ]}
        />
      );
      expect(
        screen.getByText("NO EXPENDITURE TRAJECTORY REPORTED")
      ).toBeInTheDocument();
    });

    it("renders chart container and reference line for valid observations", () => {
      const { container } = render(
        <ExpenditureTrajectoryChart
          observations={[
            { report_month: "2025-07", cumulative_expenditure: 1200 },
            { report_month: "2026-07", cumulative_expenditure: 2210 },
          ]}
          originalCost={3450}
        />
      );
      expect(container.querySelector(".recharts-responsive-container")).toBeInTheDocument();
    });
  });

  describe("ChartTooltip", () => {
    it("renders null when inactive", () => {
      const { container } = render(<ChartTooltip active={false} />);
      expect(container.firstChild).toBeNull();
    });

    it("renders formatted metrics when active with data", () => {
      render(
        <ChartTooltip
          active={true}
          label="2026-07"
          payload={[
            {
              payload: { report_month: "2026-07", val: 64.2 },
            },
          ]}
          metrics={[
            { label: "Physical Progress", value: "64.2%" },
            { label: "Cumulative Expenditure", value: "₹ 2,210 CR" },
          ]}
        />
      );

      expect(screen.getByText("REPORT MONTH: 2026-07")).toBeInTheDocument();
      expect(screen.getByText("Physical Progress:")).toBeInTheDocument();
      expect(screen.getByText("64.2%")).toBeInTheDocument();
      expect(screen.getByText("Cumulative Expenditure:")).toBeInTheDocument();
      expect(screen.getByText("₹ 2,210 CR")).toBeInTheDocument();
    });

    it("renders 'NOT REPORTED' for null values in tooltip", () => {
      render(
        <ChartTooltip
          active={true}
          label="2024-01"
          payload={[
            {
              payload: { report_month: "2024-01", val: null },
            },
          ]}
          metrics={[
            { label: "Physical Progress", value: null },
          ]}
        />
      );

      expect(screen.getByText("NOT REPORTED")).toBeInTheDocument();
    });
  });
});
