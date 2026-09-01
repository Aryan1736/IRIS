import React from "react";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

export const DataFoundationSection: React.FC = () => {
  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 50,
  });

  return (
    <section
      id="data"
      ref={sectionRef}
      className="landing-section landing-section-paper hairline-b"
    >
      <div className="container-main">
        {/* Section Heading */}
        <div style={{ textAlign: "center", marginBottom: "56px" }} className="landing-reveal-item">
          <div className="landing-section-badge" style={{ justifyContent: "center" }}>
            <span className="landing-section-badge-dot" />
            <span>[ 03 / DATA FOUNDATION ]</span>
          </div>

          <h2 className="landing-section-heading" style={{ maxWidth: "800px", margin: "0 auto 20px" }}>
            EVERY PROJECT HAS A HISTORY.
          </h2>

          <p className="landing-section-desc" style={{ margin: "0 auto" }}>
            Longitudinal intelligence requires immutability. An infrastructure project is not a single
            static database row — it is a sequence of source-faithful monthly observations.
          </p>
        </div>

        <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
          {/* Identity Equation Block */}
          <div className="equation-diagram-wrapper landing-reveal-item">
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "center",
                flexWrap: "wrap",
                gap: "20px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-sm)",
                textTransform: "uppercase",
              }}
            >
              {/* Project Code */}
              <div className="equation-step-card">
                <div
                  style={{
                    fontSize: "10px",
                    color: "var(--color-text-dim)",
                    marginBottom: "8px",
                    letterSpacing: "0.15em",
                  }}
                >
                  IDENTIFIER
                </div>
                <div style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "0.08em", color: "var(--color-primary-900)" }}>
                  PROJECT CODE
                </div>
              </div>

              <div className="equation-operator-node">+</div>

              {/* Report Month */}
              <div className="equation-step-card">
                <div
                  style={{
                    fontSize: "10px",
                    color: "var(--color-text-dim)",
                    marginBottom: "8px",
                    letterSpacing: "0.15em",
                  }}
                >
                  TEMPORAL
                </div>
                <div style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "0.08em", color: "var(--color-primary-900)" }}>
                  REPORT MONTH
                </div>
              </div>

              <div className="equation-operator-node">=</div>

              {/* Observation Result */}
              <div
                className="equation-step-card"
                style={{
                  backgroundColor: "var(--color-primary-50)",
                  borderColor: "var(--color-primary-600)",
                }}
              >
                <div
                  style={{
                    fontSize: "10px",
                    color: "var(--color-primary-700)",
                    marginBottom: "8px",
                    letterSpacing: "0.15em",
                    fontWeight: 600,
                  }}
                >
                  OUTPUT
                </div>
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: "14px",
                    color: "var(--color-primary-900)",
                    letterSpacing: "0.08em",
                  }}
                >
                  OBSERVATION
                </div>
              </div>
            </div>
          </div>

          {/* Lineage Flow Box */}
          <div
            className="equation-diagram-wrapper landing-reveal-item"
            style={{
              marginTop: "24px",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                color: "var(--color-text-dim)",
                marginBottom: "24px",
                paddingBottom: "12px",
                borderBottom: "1px solid var(--color-border-hairline)",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span>DATA LINEAGE FLOW</span>
              <span style={{ fontSize: "10px", color: "var(--color-primary-700)" }}>FAIL-CLOSED PIPELINE</span>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "14px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
              }}
            >
              <div
                className="hairline-all"
                style={{
                  flex: 1,
                  minWidth: "130px",
                  padding: "16px 12px",
                  textAlign: "center",
                  backgroundColor: "#ffffff",
                  letterSpacing: "0.08em",
                  fontWeight: 600,
                }}
              >
                OBSERVATION N
              </div>

              <div style={{ color: "var(--color-text-dim)", fontWeight: 600 }}>→</div>

              <div
                className="hairline-all"
                style={{
                  flex: 1,
                  minWidth: "130px",
                  padding: "16px 12px",
                  textAlign: "center",
                  backgroundColor: "#ffffff",
                  letterSpacing: "0.08em",
                  fontWeight: 600,
                }}
              >
                OBSERVATION N+1
              </div>

              <div style={{ color: "var(--color-text-dim)", fontWeight: 600 }}>→</div>

              <div
                className="hairline-all"
                style={{
                  flex: 1,
                  minWidth: "130px",
                  padding: "16px 12px",
                  textAlign: "center",
                  backgroundColor: "#ffffff",
                  letterSpacing: "0.08em",
                  fontWeight: 600,
                }}
              >
                OBSERVATION N+2
              </div>

              <div
                style={{
                  color: "var(--color-text-dim)",
                  fontWeight: 700,
                  fontSize: "var(--font-size-base)",
                  padding: "0 4px",
                }}
              >
                ⇒
              </div>

              <div
                style={{
                  flex: 1.2,
                  minWidth: "170px",
                  backgroundColor: "var(--color-primary-900)",
                  color: "#ffffff",
                  padding: "16px 12px",
                  textAlign: "center",
                  fontWeight: 700,
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                }}
              >
                LONGITUDINAL HISTORY
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
