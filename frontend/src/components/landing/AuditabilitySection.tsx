import React from "react";

interface AuditRow {
  index: string;
  title: string;
}

const AUDIT_ROWS: AuditRow[] = [
  { index: "01", title: "SOURCE-FAITHFUL EXTRACTION" },
  { index: "02", title: "DATASET LINEAGE" },
  { index: "03", title: "LONGITUDINAL OBSERVATION RECORDS" },
  { index: "04", title: "REPORT-MONTH PROVENANCE" },
  { index: "05", title: "TRACEABLE PROJECT HISTORY" },
];

export const AuditabilitySection: React.FC = () => {
  return (
    <section
      className="bg-paper-solid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        position: "relative",
        zIndex: 10,
        width: "100%",
      }}
    >
      <div className="container-main">
        <h2
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "clamp(2.5rem, 5vw, 4.25rem)",
            fontWeight: 700,
            letterSpacing: "-0.03em",
            lineHeight: 0.95,
            textTransform: "uppercase",
            marginBottom: "64px",
            textAlign: "center",
            color: "var(--color-primary-900)",
          }}
        >
          BUILT FOR AUDITABILITY.
        </h2>

        {/* 5-Row Lineage Verification Table matching Image 7 */}
        <div
          className="hairline-all"
          style={{
            maxWidth: "960px",
            margin: "0 auto",
            backgroundColor: "#ffffff",
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            textTransform: "uppercase",
          }}
        >
          {AUDIT_ROWS.map((row, i) => (
            <div
              key={row.index}
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                padding: "26px 36px",
                borderBottom: i < AUDIT_ROWS.length - 1 ? "1px solid var(--color-border-hairline)" : "none",
                transition: "background-color 150ms ease",
              }}
            >
              <div
                style={{
                  width: "140px",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                }}
              >
                {row.index}
              </div>

              <div
                style={{
                  flex: 1,
                  fontWeight: 700,
                  fontSize: "13px",
                  letterSpacing: "0.08em",
                  color: "var(--color-text-main)",
                }}
              >
                {row.title}
              </div>

              <div
                style={{
                  color: "var(--color-primary-900)",
                  fontSize: "18px",
                  fontWeight: 700,
                }}
              >
                ✓
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
