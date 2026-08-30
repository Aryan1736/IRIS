import React from "react";
import type { ProjectScheduleExtensionsResponse } from "@/types/project.ts";

interface ScheduleMovementSectionProps {
  scheduleData?: ProjectScheduleExtensionsResponse;
  originalCompletion?: string | null;
  revisedCompletion?: string | null;
}

export const ScheduleMovementSection: React.FC<ScheduleMovementSectionProps> = ({
  scheduleData,
  originalCompletion,
  revisedCompletion,
}) => {
  const extensions = scheduleData?.extensions || [];
  const orig = originalCompletion || scheduleData?.latest_original_completion || "—";
  const rev = revisedCompletion || scheduleData?.latest_revised_completion || orig;

  // Calculate rough month difference if both are YYYY-MM
  const calculateMonthShift = (origDate: string, revDate: string) => {
    if (origDate === "—" || revDate === "—" || origDate === revDate) return "0 MONTHS";
    const origParts = origDate.split("-").map(Number);
    const revParts = revDate.split("-").map(Number);
    if (origParts.length >= 2 && revParts.length >= 2) {
      const origMonths = origParts[0] * 12 + origParts[1];
      const revMonths = revParts[0] * 12 + revParts[1];
      const diff = revMonths - origMonths;
      if (diff > 0) return `+${diff} MONTHS`;
      if (diff < 0) return `${diff} MONTHS`;
      return "0 MONTHS";
    }
    return "—";
  };

  const shiftText = calculateMonthShift(orig, rev);
  const isShifted = shiftText.startsWith("+");

  return (
    <section className="project-detail-section">
      <h2 className="project-section-title">WHERE THE SCHEDULE MOVES.</h2>

      <div className="detail-grid-2col">
        {/* Left: Commitment Overview */}
        <div className="detail-card">
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span className="overview-metric-label">Original Commitment</span>
            <span className="overview-metric-val">{orig}</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span className="overview-metric-label">Current Effective Commitment</span>
            <span className={`overview-metric-val ${isShifted ? "coral" : ""}`}>{rev}</span>
          </div>

          <div style={{ paddingTop: "16px", borderTop: "1px solid var(--color-border-hairline)" }}>
            <span className={`overview-metric-label ${isShifted ? "coral" : ""}`}>Schedule Shift</span>
            <div
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "32px",
                fontWeight: 700,
                color: isShifted ? "var(--color-coral)" : "var(--color-primary-950)",
              }}
            >
              {shiftText}
            </div>
          </div>
        </div>

        {/* Right: Revision History Table */}
        <div className="detail-card">
          <span className="overview-metric-label" style={{ marginBottom: "8px" }}>
            Revision History
          </span>

          {extensions.length === 0 ? (
            <div style={{ padding: "24px 0", textAlign: "center", color: "var(--color-text-dim)", fontFamily: "var(--font-mono)", fontSize: "11px" }}>
              NO SCHEDULE EXTENSION EVENTS RECORDED IN SOURCE DATA
            </div>
          ) : (
            <table className="detail-table">
              <thead>
                <tr>
                  <th>REPORT MONTH</th>
                  <th>ORIGINAL</th>
                  <th>REVISED</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {extensions.slice(0, 5).map((ext, idx) => (
                  <tr key={`${ext.report_month}-${idx}`}>
                    <td>{ext.report_month}</td>
                    <td>{ext.original_completion_date || "—"}</td>
                    <td style={{ color: ext.revised_completion_date ? "var(--color-coral)" : "inherit" }}>
                      {ext.revised_completion_date || "—"}
                    </td>
                    <td style={{ color: ext.revised_completion_date ? "var(--color-coral)" : "inherit" }}>
                      {ext.revised_completion_date ? "SHIFTED" : "UNCHANGED"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <p style={{ marginTop: "auto", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--color-text-dim)", fontStyle: "italic", margin: 0 }}>
            Observed schedule changes are based on reported project records.
          </p>
        </div>
      </div>
    </section>
  );
};
