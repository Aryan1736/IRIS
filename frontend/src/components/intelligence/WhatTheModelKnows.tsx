import React from "react";

export const WhatTheModelKnows: React.FC = () => {
  const features = [
    {
      title: "PROJECT TRAJECTORY",
      desc: "Historical patterns of milestone completion, longitudinal delays, and pacing against baseline schedule.",
    },
    {
      title: "STATIC PROJECT ATTRIBUTES",
      desc: "Inherent complexity, region, implementing agency, project type, and initial budget scale.",
    },
    {
      title: "SCHEDULE HISTORY",
      desc: "Frequency of schedule revisions, lag from original baseline, and critical milestone stability.",
    },
    {
      title: "EXPENDITURE HISTORY",
      desc: "Cumulative capital expenditure burn rate, cost revisions to date, and funding allocation trajectory.",
    },
    {
      title: "PROGRESS HISTORY",
      desc: "Physical progress percentage reported over time and progress-to-time ratio dynamics.",
    },
    {
      title: "REPORTING CONTINUITY",
      desc: "Data quality signals derived from continuous monthly reporting, legacy-to-modern transitions, and record completeness.",
    },
  ];

  return (
    <section className="intelligence-section">
      <div className="intelligence-section-header">
        <div className="intelligence-section-title-lockup">
          <h2 className="intelligence-section-title">09. What the Model Knows</h2>
          <span className="intelligence-section-subtitle">
            FEATURE FAMILIES & LONGITUDINAL SIGNAL ARCHITECTURE
          </span>
        </div>
        <span className="intelligence-section-subtitle">
          6 INPUT FAMILIES
        </span>
      </div>

      <div className="intelligence-features-grid">
        {features.map((f) => (
          <div key={f.title} className="intelligence-feature-card">
            <h3 className="intelligence-feature-card-title">{f.title}</h3>
            <p className="intelligence-feature-card-desc">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
