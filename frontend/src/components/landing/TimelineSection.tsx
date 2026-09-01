import React, { useState } from "react";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

interface TimelineNodeData {
  month: string;
  reportMonthDisplay: string;
  observation: string;
  status: "ON TRACK" | "DELAY DETECTED" | "STABLE" | "COST OVERRUN" | "ACTIVE MONITORING";
  ringColor: string;
  dotColor: string;
  textColor: string;
  progressPct: string;
  costDelta: string;
  isSpecial?: boolean;
}

const TIMELINE_NODES: TimelineNodeData[] = [
  {
    month: "2024-01",
    reportMonthDisplay: "JAN 2024",
    observation: "Baseline Established across 1,800+ Flash Report records",
    status: "ON TRACK",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
    progressPct: "8.5%",
    costDelta: "±0.00 Cr",
  },
  {
    month: "2024-02",
    reportMonthDisplay: "FEB 2024",
    observation: "Initial Progress increment reported by implementing agency",
    status: "ON TRACK",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
    progressPct: "14.2%",
    costDelta: "+12.40 Cr",
  },
  {
    month: "2024-03",
    reportMonthDisplay: "MAR 2024",
    observation: "Schedule Revision: completion shifted forward by 8 months",
    status: "DELAY DETECTED",
    ringColor: "var(--color-gold)",
    dotColor: "var(--color-gold)",
    textColor: "var(--color-gold)",
    progressPct: "18.0%",
    costDelta: "+84.50 Cr",
    isSpecial: true,
  },
  {
    month: "2024-04",
    reportMonthDisplay: "APR 2024",
    observation: "Physical Progress stabilized following revised milestone schedule",
    status: "STABLE",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
    progressPct: "32.0%",
    costDelta: "+45.10 Cr",
  },
  {
    month: "2024-05",
    reportMonthDisplay: "MAY 2024",
    observation: "Cumulative expenditure surge exceeds physical completion trajectory",
    status: "COST OVERRUN",
    ringColor: "var(--color-error)",
    dotColor: "var(--color-error)",
    textColor: "var(--color-error)",
    progressPct: "41.5%",
    costDelta: "+310.00 Cr",
    isSpecial: true,
  },
  {
    month: "2024-06",
    reportMonthDisplay: "JUN 2024",
    observation: "Latest canonical flash report snapshot actively monitored in IRIS",
    status: "ACTIVE MONITORING",
    ringColor: "var(--color-primary-900)",
    dotColor: "var(--color-primary-900)",
    textColor: "var(--color-primary-900)",
    progressPct: "48.2%",
    costDelta: "+58.20 Cr",
    isSpecial: true,
  },
];

export const TimelineSection: React.FC = () => {
  const [selectedIndex, setSelectedIndex] = useState<number>(3);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const activeIndex = hoveredIndex !== null ? hoveredIndex : selectedIndex;
  const activeNode = TIMELINE_NODES[activeIndex] || TIMELINE_NODES[3];

  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 50,
  });

  return (
    <section
      id="problem"
      ref={sectionRef}
      className="landing-section landing-section-paper hairline-b"
    >
      <div className="container-main">
        {/* Section Header */}
        <div style={{ marginBottom: "48px" }} className="landing-reveal-item">
          <div className="landing-section-badge">
            <span className="landing-section-badge-dot" />
            <span>[ 01 / LONGITUDINAL TRAJECTORY ]</span>
          </div>

          <h2 className="landing-section-heading">
            INFRASTRUCTURE PROJECTS
            <br />
            DON'T CHANGE IN A SINGLE MOMENT.
          </h2>

          <p className="landing-section-desc">
            Infrastructure project health degrades gradually across consecutive flash reports. IRIS
            maps every monthly observation into a continuous, audit-faithful longitudinal timeline to
            identify early divergence before failure becomes irreversible.
          </p>
        </div>

        {/* Timeline Interactive Shell */}
        <div className="timeline-card-shell landing-reveal-item">
          {/* Header Bar */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              paddingBottom: "18px",
              borderBottom: "1px solid var(--color-border-hairline)",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
            }}
          >
            <span style={{ color: "var(--color-text-dim)", fontWeight: 600 }}>
              LONGITUDINAL OBSERVATION TIMELINE
            </span>
            <span style={{ color: "var(--color-primary-900)", fontWeight: 700 }}>
              2024-01 / 2024-06
            </span>
          </div>

          {/* Timeline Scrubber Graphic */}
          <div className="timeline-track-wrapper">
            {/* Horizontal Track Lines */}
            <div className="timeline-horizontal-bar" />
            <div
              className="timeline-horizontal-progress"
              style={{
                width: `${(activeIndex / (TIMELINE_NODES.length - 1)) * 92}%`,
              }}
            />

            {/* Nodes */}
            <div
              style={{
                position: "relative",
                zIndex: 3,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              {TIMELINE_NODES.map((node, index) => {
                const isCurrent = index === activeIndex;

                return (
                  <div
                    key={node.month}
                    className={`timeline-node-item ${isCurrent ? "active" : ""}`}
                    onClick={() => setSelectedIndex(index)}
                    onMouseEnter={() => setHoveredIndex(index)}
                    onMouseLeave={() => setHoveredIndex(null)}
                    style={{ textAlign: "center" }}
                  >
                    <div
                      className="timeline-node-circle"
                      style={{
                        borderColor: isCurrent ? node.ringColor : "var(--color-border-hairline)",
                      }}
                    >
                      <div
                        className="timeline-node-inner-dot"
                        style={{
                          backgroundColor: isCurrent ? node.dotColor : "var(--color-text-dim)",
                        }}
                      />
                    </div>

                    <div
                      style={{
                        marginTop: "12px",
                        fontFamily: "var(--font-mono)",
                        fontSize: "11px",
                        fontWeight: isCurrent ? 700 : 400,
                        color: isCurrent ? "var(--color-primary-900)" : "var(--color-text-dim)",
                        letterSpacing: "0.05em",
                        transition: "color 150ms ease",
                      }}
                    >
                      {node.month}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Observation Readout Strip */}
          <div
            style={{
              marginTop: "28px",
              padding: "24px 28px",
              backgroundColor: "#faf9f6",
              border: "1px solid var(--color-border-hairline)",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "20px",
              alignItems: "center",
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "4px",
                }}
              >
                REPORT MONTH
              </div>
              <div
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 700,
                  color: "var(--color-primary-900)",
                }}
              >
                {activeNode.reportMonthDisplay}
              </div>
            </div>

            <div style={{ gridColumn: "span 2" }}>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "4px",
                }}
              >
                AUDITABLE OBSERVATION
              </div>
              <div
                style={{
                  fontFamily: "var(--font-sans)",
                  fontSize: "var(--font-size-sm)",
                  color: "var(--color-text-main)",
                  lineHeight: 1.5,
                }}
              >
                {activeNode.observation}
              </div>
            </div>

            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "4px",
                }}
              >
                STATUS SIGNAL
              </div>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  fontWeight: 700,
                  color: activeNode.textColor,
                  letterSpacing: "0.08em",
                }}
              >
                <span
                  style={{
                    width: "7px",
                    height: "7px",
                    borderRadius: "50%",
                    backgroundColor: "currentColor",
                    display: "inline-block",
                  }}
                />
                <span>{activeNode.status}</span>
              </div>
            </div>

            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  marginBottom: "4px",
                }}
              >
                PROGRESS / DELTA
              </div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "12px",
                  fontWeight: 600,
                  color: "var(--color-text-main)",
                }}
              >
                {activeNode.progressPct} ({activeNode.costDelta})
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
