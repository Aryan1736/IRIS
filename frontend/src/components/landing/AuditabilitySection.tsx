import React from "react";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

interface AuditRow {
  index: string;
  title: string;
  description: string;
}

const AUDIT_ROWS: AuditRow[] = [
  {
    index: "01",
    title: "SOURCE-FAITHFUL EXTRACTION",
    description: "Original PDF flash report tables extracted without synthetic normalization or backfilling.",
  },
  {
    index: "02",
    title: "DATASET LINEAGE",
    description: "Every record contains file hash, physical PDF page numbers, and exact row provenance.",
  },
  {
    index: "03",
    title: "LONGITUDINAL OBSERVATION RECORDS",
    description: "Multi-month project histories preserved through strict (project_code, report_month) keys.",
  },
  {
    index: "04",
    title: "REPORT-MONTH PROVENANCE",
    description: "Zero date extrapolation — unprinted dates remain source-absent rather than invented.",
  },
  {
    index: "05",
    title: "TRACEABLE PROJECT HISTORY",
    description: "Adjacent-month quality checks enforce continuity across expenditure and progress jumps.",
  },
];

export const AuditabilitySection: React.FC = () => {
  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 40,
  });

  return (
    <section
      ref={sectionRef}
      className="landing-section landing-section-paper hairline-b"
      style={{
        zIndex: 10,
      }}
    >
      <div className="container-main">
        {/* Section Header */}
        <div style={{ textAlign: "center", marginBottom: "56px" }} className="landing-reveal-item">
          <div className="landing-section-badge" style={{ justifyContent: "center" }}>
            <span className="landing-section-badge-dot" />
            <span>[ 06 / VERIFIABLE PROVENANCE ]</span>
          </div>

          <h2 className="landing-section-heading">
            BUILT FOR AUDITABILITY.
          </h2>

          <p className="landing-section-desc" style={{ margin: "0 auto" }}>
            Every metric, trajectory, and predictive signal in IRIS is verifiable back to the
            exact page, table, and row of the source monthly flash reports.
          </p>
        </div>

        {/* 5-Row Lineage Verification Table */}
        <div
          className="hairline-all landing-reveal-item"
          style={{
            maxWidth: "1000px",
            margin: "0 auto",
            backgroundColor: "#ffffff",
            fontFamily: "var(--font-mono)",
            fontSize: "13px",
            textTransform: "uppercase",
            boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
          }}
        >
          {AUDIT_ROWS.map((row) => (
            <div key={row.index} className="audit-row-item">
              <div
                style={{
                  width: "100px",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                  fontWeight: 600,
                }}
              >
                [ {row.index} ]
              </div>

              <div style={{ flex: 1 }}>
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: "13px",
                    letterSpacing: "0.06em",
                    color: "var(--color-primary-900)",
                    marginBottom: "4px",
                  }}
                >
                  {row.title}
                </div>
                <div
                  style={{
                    fontFamily: "var(--font-sans)",
                    fontSize: "12px",
                    color: "var(--color-text-dim)",
                    textTransform: "none",
                    letterSpacing: "normal",
                  }}
                >
                  {row.description}
                </div>
              </div>

              <div
                style={{
                  color: "#10b981",
                  fontSize: "18px",
                  fontWeight: 700,
                  paddingLeft: "16px",
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
