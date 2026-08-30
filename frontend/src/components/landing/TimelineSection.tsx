import React, { useState } from "react";

interface TimelineNodeData {
  month: string;
  reportMonthDisplay: string;
  observation: string;
  status: "ON TRACK" | "DELAY DETECTED" | "STABLE" | "COST OVERRUN" | "ACTIVE MONITORING";
  ringColor: string;
  dotColor: string;
  textColor: string;
  isSpecial?: boolean;
}

const TIMELINE_NODES: TimelineNodeData[] = [
  {
    month: "2024-01",
    reportMonthDisplay: "JAN 24",
    observation: "Baseline Established",
    status: "ON TRACK",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
  },
  {
    month: "2024-02",
    reportMonthDisplay: "FEB 24",
    observation: "Initial Progress 14%",
    status: "ON TRACK",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
  },
  {
    month: "2024-03",
    reportMonthDisplay: "MAR 24",
    observation: "Schedule Revision",
    status: "DELAY DETECTED",
    ringColor: "var(--color-gold)",
    dotColor: "var(--color-gold)",
    textColor: "var(--color-gold)",
    isSpecial: true,
  },
  {
    month: "2024-04",
    reportMonthDisplay: "APR 24",
    observation: "Progress 32%",
    status: "STABLE",
    ringColor: "rgba(58, 58, 56, 0.25)",
    dotColor: "rgba(58, 58, 56, 0.6)",
    textColor: "var(--color-text-dim)",
  },
  {
    month: "2024-05",
    reportMonthDisplay: "MAY 24",
    observation: "Expenditure Spike",
    status: "COST OVERRUN",
    ringColor: "#FF8A65",
    dotColor: "#FF8A65",
    textColor: "#FF8A65",
    isSpecial: true,
  },
  {
    month: "2024-06",
    reportMonthDisplay: "JUN 24",
    observation: "Latest Status Check",
    status: "ACTIVE MONITORING",
    ringColor: "var(--color-primary-900)",
    dotColor: "var(--color-primary-900)",
    textColor: "var(--color-primary-900)",
    isSpecial: true,
  },
];

export const TimelineSection: React.FC = () => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section
      id="problem"
      className="bg-paper-solid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        position: "relative",
        width: "100%",
      }}
    >
      <div className="container-main">
        <div style={{ marginBottom: "64px" }}>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
              fontWeight: 700,
              letterSpacing: "-0.03em",
              lineHeight: 0.95,
              textTransform: "uppercase",
              maxWidth: "1050px",
              color: "var(--color-primary-900)",
            }}
          >
            INFRASTRUCTURE PROJECTS
            <br />
            DON'T CHANGE IN A SINGLE
            <br />
            MOMENT.
          </h2>
        </div>

        {/* Timeline Container on crisp white surface matching Image 2 */}
        <div
          className="hairline-all"
          style={{
            backgroundColor: "#ffffff",
          }}
        >
          {/* Header Bar */}
          <div
            className="hairline-b"
            style={{
              padding: "16px 24px",
              fontFamily: "var(--font-mono)",
              fontSize: "var(--font-size-xs)",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              backgroundColor: "#ffffff",
            }}
          >
            <span style={{ color: "var(--color-text-dim)", letterSpacing: "0.15em" }}>
              LONGITUDINAL OBSERVATION TIMELINE
            </span>
            <span style={{ color: "var(--color-text-dim)", letterSpacing: "0.15em" }}>
              2024-01 / 2024-06
            </span>
          </div>

          {/* Timeline Graphic Canvas */}
          <div
            style={{
              padding: "96px 48px",
              backgroundColor: "#ffffff",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: "260px",
              overflowX: "auto",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "relative",
                width: "820px",
                minWidth: "820px",
                height: "64px",
                display: "flex",
                alignItems: "center",
              }}
            >
              {/* Baseline continuous line */}
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  height: "1px",
                  backgroundColor: "rgba(58, 58, 56, 0.15)",
                  width: "100%",
                }}
              />

              {/* Concentric Circular Nodes Container */}
              <div
                style={{
                  position: "absolute",
                  width: "100%",
                  display: "flex",
                  justifyContent: "space-between",
                  paddingLeft: "16px",
                  paddingRight: "16px",
                }}
              >
                {TIMELINE_NODES.map((node, index) => {
                  const isHovered = hoveredIndex === index;

                  return (
                    <div
                      key={node.month}
                      onMouseEnter={() => setHoveredIndex(index)}
                      onMouseLeave={() => setHoveredIndex(null)}
                      style={{
                        position: "relative",
                        cursor: "pointer",
                      }}
                    >
                      {/* Concentric Double Circle Node */}
                      <div
                        style={{
                          width: "18px",
                          height: "18px",
                          borderRadius: "50%",
                          backgroundColor: "#ffffff",
                          border: `2px solid ${node.ringColor}`,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          position: "relative",
                          zIndex: 10,
                          transition: "transform 150ms ease",
                          transform: isHovered ? "scale(1.25)" : "scale(1)",
                        }}
                      >
                        <div
                          style={{
                            width: "6px",
                            height: "6px",
                            borderRadius: "50%",
                            backgroundColor: node.dotColor,
                          }}
                        />
                      </div>

                      {/* Month Label */}
                      <div
                        style={{
                          position: "absolute",
                          top: "28px",
                          left: "50%",
                          transform: "translateX(-50%)",
                          fontFamily: "var(--font-mono)",
                          fontSize: "11px",
                          textAlign: "center",
                          width: "80px",
                          fontWeight: node.isSpecial ? 600 : 400,
                          color: node.textColor,
                          letterSpacing: "0.05em",
                        }}
                      >
                        {node.month}
                      </div>

                      {/* Hover Tooltip Panel */}
                      {isHovered && (
                        <div
                          className="hairline-all"
                          style={{
                            position: "absolute",
                            bottom: "100%",
                            left: "50%",
                            transform: "translateX(-50%)",
                            marginBottom: "16px",
                            backgroundColor: "#ffffff",
                            color: "var(--color-text-main)",
                            borderColor: node.ringColor,
                            padding: "12px 16px",
                            width: "200px",
                            fontFamily: "var(--font-mono)",
                            fontSize: "10px",
                            zIndex: 30,
                            boxShadow: "none",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              borderBottom: "1px solid var(--color-border-hairline)",
                              paddingBottom: "6px",
                              marginBottom: "6px",
                            }}
                          >
                            <span style={{ opacity: 0.6 }}>REPORT MONTH</span>
                            <span style={{ fontWeight: 700 }}>{node.reportMonthDisplay}</span>
                          </div>

                          <div style={{ marginBottom: "6px" }}>
                            <div style={{ opacity: 0.6, marginBottom: "2px" }}>OBSERVATION</div>
                            <div style={{ fontWeight: 500 }}>{node.observation}</div>
                          </div>

                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: "6px",
                              fontWeight: 600,
                              color: node.textColor,
                            }}
                          >
                            <span
                              style={{
                                width: "6px",
                                height: "6px",
                                borderRadius: "50%",
                                backgroundColor: "currentColor",
                                display: "inline-block",
                              }}
                            />
                            <span>{node.status}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
