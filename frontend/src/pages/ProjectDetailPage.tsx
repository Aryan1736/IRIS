import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  fetchProjectDetail,
  fetchLatestSnapshot,
  fetchProjectTrajectory,
  fetchCostRevisions,
  fetchScheduleExtensions,
} from "@/api/projects.ts";
import { ProjectDetailHeader } from "@/components/project-detail/ProjectDetailHeader.tsx";
import { LatestSnapshotStrip } from "@/components/project-detail/LatestSnapshotStrip.tsx";
import { ProjectTrajectorySection } from "@/components/project-detail/ProjectTrajectorySection.tsx";
import { ScheduleMovementSection } from "@/components/project-detail/ScheduleMovementSection.tsx";
import { ExpenditureTrajectorySection } from "@/components/project-detail/ExpenditureTrajectorySection.tsx";
import { ProjectSignalsSection } from "@/components/project-detail/ProjectSignalsSection.tsx";
import { SourceObservationTable } from "@/components/project-detail/SourceObservationTable.tsx";
import { ProjectProvenanceSection } from "@/components/project-detail/ProjectProvenanceSection.tsx";
import { ProjectDetailNav } from "@/components/project-detail/ProjectDetailNav.tsx";
import { Button } from "@/components/ui/Button.tsx";
import { Card } from "@/components/ui/Card.tsx";
import { TechnicalLabel } from "@/components/ui/TechnicalLabel.tsx";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner.tsx";

export const ProjectDetailPage: React.FC = () => {
  const { projectCode } = useParams<{ projectCode: string }>();

  const code = projectCode || "";

  const {
    data: project,
    isLoading: isProjectLoading,
    error: projectError,
  } = useQuery({
    queryKey: ["projectDetail", code],
    queryFn: () => fetchProjectDetail(code),
    enabled: Boolean(code),
  });

  const {
    data: snapshot,
    isLoading: isSnapshotLoading,
  } = useQuery({
    queryKey: ["latestSnapshot", code],
    queryFn: () => fetchLatestSnapshot(code),
    enabled: Boolean(code),
  });

  const {
    data: trajectory,
    isLoading: isTrajectoryLoading,
  } = useQuery({
    queryKey: ["projectTrajectory", code],
    queryFn: () => fetchProjectTrajectory(code),
    enabled: Boolean(code),
  });

  const {
    data: costRevisions,
  } = useQuery({
    queryKey: ["costRevisions", code],
    queryFn: () => fetchCostRevisions(code),
    enabled: Boolean(code),
  });

  const {
    data: scheduleExtensions,
  } = useQuery({
    queryKey: ["scheduleExtensions", code],
    queryFn: () => fetchScheduleExtensions(code),
    enabled: Boolean(code),
  });

  const isLoading = isProjectLoading || isSnapshotLoading || isTrajectoryLoading;

  // Handle 404 or Project Not Found
  if (projectError || (!isLoading && !project && code)) {
    return (
      <div className="bg-blueprint-grid" style={{ minHeight: "calc(100vh - 64px)", padding: "48px 24px" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto" }}>
          <TechnicalLabel label="AUDIT RECORD UNLOCATED" sublabel={`CODE: ${code}`} />
          <Card
            style={{ marginTop: "16px" }}
            padding="lg"
            title={`PROJECT NOT FOUND: ${code}`}
            subtitle="CANONICAL DATABASE LOOKUP"
          >
            <p
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "var(--font-size-base)",
                color: "var(--color-text-variant)",
                lineHeight: 1.6,
                marginBottom: "24px",
              }}
            >
              The requested project code <strong style={{ color: "var(--color-primary-950)", fontFamily: "var(--font-mono)" }}>{code}</strong> does not match any verified historical project record in the canonical PAIMANA monitoring dataset.
            </p>
            <Link to="/projects" style={{ textDecoration: "none" }}>
              <Button variant="primary" size="sm">
                ← RETURN TO PROJECT DISCOVERY
              </Button>
            </Link>
          </Card>
        </div>
      </div>
    );
  }

  // Handle Initial Loading
  if (isLoading) {
    return (
      <div className="bg-blueprint-grid" style={{ minHeight: "calc(100vh - 64px)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "16px" }}>
          <LoadingSpinner size="lg" />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--color-text-dim)", letterSpacing: "0.1em" }}>
            FETCHING CANONICAL PROJECT RECORD: {code}...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-blueprint-grid" style={{ minHeight: "calc(100vh - 64px)" }}>
      <div className="project-detail-container">
        {/* Breadcrumb */}
        <div className="project-breadcrumb">
          <Link to="/projects">IRIS / PROJECTS</Link>
          <span>/</span>
          <span>{code}</span>
        </div>

        {/* Project Header */}
        <ProjectDetailHeader project={project} projectCode={code} />

        {/* 6-Cell Overview Strip */}
        <LatestSnapshotStrip snapshot={snapshot} />

        {/* Section 01: Project Trajectory */}
        <ProjectTrajectorySection trajectoryData={trajectory} />

        {/* Section 02: Schedule Movement */}
        <ScheduleMovementSection
          scheduleData={scheduleExtensions}
          originalCompletion={snapshot?.original_completion_date}
          revisedCompletion={snapshot?.revised_completion_date}
        />

        {/* Section 03: Expenditure Trajectory */}
        <ExpenditureTrajectorySection
          costData={costRevisions}
          snapshot={snapshot}
        />

        {/* Section 04: Project Signals */}
        <ProjectSignalsSection snapshot={snapshot} project={project} />

        {/* Section 05: Monthly Observations */}
        <SourceObservationTable trajectoryData={trajectory} />

        {/* Section 06: Data Provenance */}
        <ProjectProvenanceSection project={project} snapshot={snapshot} projectCode={code} />

        {/* Section 07: Navigation */}
        <ProjectDetailNav />
      </div>
    </div>
  );
};
