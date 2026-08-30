import React from "react";

export const ScheduleIntelligenceSection: React.FC = () => {
  return (
    <section className="dashboard-section">
      <div className="dashboard-section-header">
        <h2 className="dashboard-section-title">WHERE SCHEDULES MOVE.</h2>
      </div>

      <div className="dashboard-grid-2-col">
        {/* Left: Schedule Extensions */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">SCHEDULE EXTENSIONS</span>
            <span className="card-tag-pending">CORAL SIGNAL: ACTIVE</span>
          </div>

          <div style={{ height: "180px", display: "flex", alignItems: "flex-end", gap: "6px", paddingTop: "20px" }}>
            <div style={{ flex: 1, backgroundColor: "rgba(186, 26, 26, 0.15)", height: "25%" }} />
            <div style={{ flex: 1, backgroundColor: "rgba(186, 26, 26, 0.25)", height: "40%" }} />
            <div style={{ flex: 1, backgroundColor: "rgba(186, 26, 26, 0.45)", height: "65%" }} />
            <div style={{ flex: 1, backgroundColor: "rgba(186, 26, 26, 0.65)", height: "50%" }} />
            <div style={{ flex: 1, backgroundColor: "var(--color-coral)", height: "85%" }} />
          </div>

          <p style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", fontStyle: "italic", margin: 0 }}>
            NOTE: Observed extension events represent historical reporting shifts, not necessarily terminal project failure.
          </p>
        </div>

        {/* Right: Demo Schedule Position */}
        <div className="dashboard-card-white">
          <div className="card-header-lockup">
            <span className="card-label">DEMO SCHEDULE POSITION</span>
            <span className="card-tag-pending">DEMO CLASSIFICATION</span>
          </div>

          <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="schedule-position-bar">
              <div
                className="schedule-segment"
                style={{ width: "45%", backgroundColor: "rgba(2, 38, 23, 0.85)", color: "#ffffff" }}
              >
                AHEAD
              </div>
              <div
                className="schedule-segment"
                style={{ width: "30%", backgroundColor: "rgba(2, 38, 23, 0.35)", color: "var(--color-primary-950)" }}
              >
                WITHIN
              </div>
              <div
                className="schedule-segment"
                style={{ width: "15%", backgroundColor: "rgba(186, 26, 26, 0.35)", color: "var(--color-coral)" }}
              >
                APPROACH
              </div>
              <div
                className="schedule-segment"
                style={{ width: "10%", backgroundColor: "var(--color-coral)", color: "#ffffff" }}
              >
                PAST
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", textTransform: "uppercase" }}>
              <span>ORIGINAL COMPLETION BOUNDARY</span>
              <span>REVISED COMPLETION BOUNDARY</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
