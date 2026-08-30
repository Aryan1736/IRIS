import React from "react";

interface Capability {
  index: string;
  title: string;
  description: string;
}

const CAPABILITIES: Capability[] = [
  {
    index: "01",
    title: "PROJECT DISCOVERY",
    description: "Search and inspect infrastructure projects across the monitored portfolio.",
  },
  {
    index: "02",
    title: "PROJECT HISTORY",
    description: "Trace how each project evolves across reporting periods.",
  },
  {
    index: "03",
    title: "COST INTELLIGENCE",
    description: "Track cost changes and identify patterns associated with escalation.",
  },
  {
    index: "04",
    title: "SCHEDULE INTELLIGENCE",
    description: "Analyse completion timelines and emerging schedule risks.",
  },
  {
    index: "05",
    title: "RISK & EARLY WARNING",
    description: "Surface projects requiring attention before risks become critical.",
  },
  {
    index: "06",
    title: "PORTFOLIO INTELLIGENCE",
    description: "Compare projects, sectors, agencies, and infrastructure portfolios.",
  },
];

export const CapabilitiesSection: React.FC = () => {
  return (
    <section
      id="capabilities"
      className="bg-mosaic-grid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        width: "100%",
      }}
    >
      <div className="container-main">
        {/* Section Heading */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "64px",
          }}
        >
          <span
            style={{
              width: "8px",
              height: "8px",
              backgroundColor: "var(--color-mint-subtle)",
              borderRadius: "var(--radius-none)",
              display: "inline-block",
            }}
          />
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(2rem, 4vw, 3.25rem)",
              fontWeight: 700,
              letterSpacing: "-0.03em",
              lineHeight: 0.95,
              textTransform: "uppercase",
              color: "var(--color-primary-900)",
            }}
          >
            MONITOR WHAT CHANGES
          </h2>
        </div>

        {/* 6-Grid Capabilities with Hairline Grid Borders matching Image 3 */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1px",
            backgroundColor: "var(--color-border-hairline)",
            border: "1px solid var(--color-border-hairline)",
          }}
        >
          {CAPABILITIES.map((cap) => (
            <div
              key={cap.index}
              style={{
                backgroundColor: "#ffffff",
                padding: "48px 40px",
                transition: "background-color 150ms ease",
              }}
            >
              {/* Card Index & Hairline Divider */}
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  marginBottom: "28px",
                  paddingBottom: "14px",
                  borderBottom: "1px solid var(--color-border-hairline)",
                  letterSpacing: "0.15em",
                }}
              >
                [ {cap.index} ]
              </div>

              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-xl)",
                  fontWeight: 700,
                  marginBottom: "16px",
                  textTransform: "uppercase",
                  letterSpacing: "-0.02em",
                  color: "var(--color-primary-900)",
                }}
              >
                {cap.title}
              </h3>

              <p
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "var(--font-size-base)",
                  lineHeight: 1.6,
                  color: "var(--color-text-main)",
                  opacity: 0.85,
                }}
              >
                {cap.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
