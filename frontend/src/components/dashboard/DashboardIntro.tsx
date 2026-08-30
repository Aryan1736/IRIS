import React from "react";

interface DashboardIntroProps {
  lastUpdated?: string;
}

export const DashboardIntro: React.FC<DashboardIntroProps> = ({
  lastUpdated = "2026-08-29",
}) => {
  return (
    <section className="dashboard-intro-section">
      <div className="dashboard-intro-left">
        <div className="dashboard-breadcrumb">IRIS / PORTFOLIO OVERVIEW</div>
        <h1 className="dashboard-main-title">INFRASTRUCTURE AT A GLANCE.</h1>
        <p className="dashboard-description">
          Continuous monitoring of strategic project activity, resource allocation, and timeline adherence across all managed sectors.
        </p>
      </div>
      <div className="dashboard-timestamp">
        LAST UPDATED {lastUpdated}
      </div>
    </section>
  );
};
