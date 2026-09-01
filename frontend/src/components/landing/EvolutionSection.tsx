import React from "react";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

export const EvolutionSection: React.FC = () => {
  const metadataTaxonomy = ["SECTOR", "STATE", "MINISTRY", "AGENCY", "PROJECT", "TIME"];

  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 50,
  });

  return (
    <section
      id="intelligence"
      ref={sectionRef}
      className="landing-section landing-section-paper hairline-b"
    >
      <div className="container-main">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 1fr)",
            gap: "clamp(24px, 4vw, 56px)",
            alignItems: "start",
          }}
        >
          {/* Left Column (4 Columns on Desktop): Evolution Phases */}
          <div
            style={{
              gridColumn: "span 4 / span 4",
              display: "flex",
              flexDirection: "column",
            }}
            className="landing-reveal-item"
          >
            <div className="landing-section-badge">
              <span className="landing-section-badge-dot" />
              <span>[ 05 / EVOLUTION OF INTELLIGENCE ]</span>
            </div>

            <h2 className="landing-section-heading">
              EVOLUTION OF
              <br />
              INTELLIGENCE
            </h2>

            <p className="landing-section-desc" style={{ marginBottom: "40px" }}>
              The IRIS architecture is designed to progressively build upon its source-faithful data
              foundation, moving from basic reporting to advanced predictive analytics.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "20px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
                textTransform: "uppercase",
              }}
            >
              {/* Phase 01 */}
              <div
                style={{
                  border: "1px solid var(--color-primary-400)",
                  backgroundColor: "#ffffff",
                  padding: "24px 20px",
                  position: "relative",
                  boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-7px",
                    top: "-7px",
                    width: "16px",
                    height: "16px",
                    backgroundColor: "var(--color-primary-600)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "9px",
                  }}
                >
                  1
                </div>
                <div style={{ color: "var(--color-primary-700)", fontWeight: 700, fontSize: "10px", marginBottom: "6px", letterSpacing: "0.12em" }}>
                  PHASE 01 / COMPLETE
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  SOURCE DATA FOUNDATION
                </div>
              </div>

              {/* Phase 02 */}
              <div
                style={{
                  border: "1px solid var(--color-primary-400)",
                  backgroundColor: "#ffffff",
                  padding: "24px 20px",
                  position: "relative",
                  boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-7px",
                    top: "-7px",
                    width: "16px",
                    height: "16px",
                    backgroundColor: "var(--color-primary-600)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "9px",
                  }}
                >
                  2
                </div>
                <div style={{ color: "var(--color-primary-700)", fontWeight: 700, fontSize: "10px", marginBottom: "6px", letterSpacing: "0.12em" }}>
                  PHASE 02 / ACTIVE
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  LONGITUDINAL PROCESSING
                </div>
              </div>

              {/* Phase 03 */}
              <div
                style={{
                  border: "1px solid var(--color-primary-400)",
                  backgroundColor: "#ffffff",
                  padding: "24px 20px",
                  position: "relative",
                  boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-7px",
                    top: "-7px",
                    width: "16px",
                    height: "16px",
                    backgroundColor: "var(--color-primary-600)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "9px",
                  }}
                >
                  3
                </div>
                <div style={{ color: "var(--color-primary-700)", fontWeight: 700, fontSize: "10px", marginBottom: "6px", letterSpacing: "0.12em" }}>
                  PHASE 03 / OPERATIONAL
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  DECISION SUPPORT & ML
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (8 Columns): Taxonomy & Terminal */}
          <div
            style={{ gridColumn: "span 8 / span 8" }}
            className="landing-reveal-item"
          >
            <div
              className="hairline-all"
              style={{
                backgroundColor: "#ffffff",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                boxShadow: "0 1px 3px rgba(0, 0, 0, 0.02)",
              }}
            >
              <div
                style={{
                  padding: "clamp(24px, 4vw, 44px)",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <h3
                  style={{
                    fontFamily: "var(--font-heading)",
                    fontSize: "var(--font-size-2xl)",
                    fontWeight: 700,
                    marginBottom: "24px",
                    textTransform: "uppercase",
                    letterSpacing: "-0.02em",
                    color: "var(--color-primary-900)",
                  }}
                >
                  FROM PROJECTS TO PORTFOLIOS
                </h3>

                {/* Metadata Taxonomy Chips */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "10px",
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    marginBottom: "32px",
                  }}
                >
                  {metadataTaxonomy.map((tag) => (
                    <span
                      key={tag}
                      className="hairline-all"
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#FAF9F6",
                        color: "var(--color-text-main)",
                        letterSpacing: "0.12em",
                        fontWeight: 600,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Portfolio Intelligence Query Console */}
                <div
                  className="hairline-t"
                  style={{
                    paddingTop: "32px",
                  }}
                >
                  <h3
                    style={{
                      fontFamily: "var(--font-heading)",
                      fontSize: "var(--font-size-xl)",
                      fontWeight: 700,
                      marginBottom: "14px",
                      textTransform: "uppercase",
                      letterSpacing: "-0.02em",
                      color: "var(--color-primary-900)",
                    }}
                  >
                    ASK THE INFRASTRUCTURE PORTFOLIO.
                  </h3>

                  <p
                    style={{
                      fontFamily: "var(--font-sans)",
                      fontSize: "var(--font-size-base)",
                      opacity: 0.85,
                      marginBottom: "24px",
                      color: "var(--color-text-main)",
                      lineHeight: 1.6,
                    }}
                  >
                    IRIS Intelligence provides an analytical layer over source data, enabling precise querying
                    of complex multi-billion rupee infrastructure portfolios.
                  </p>

                  {/* Terminal Visual Window */}
                  <div
                    className="hairline-all"
                    style={{
                      backgroundColor: "#FAF9F6",
                      padding: "24px",
                      fontFamily: "var(--font-mono)",
                      fontSize: "var(--font-size-xs)",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        marginBottom: "14px",
                        color: "var(--color-text-dim)",
                      }}
                    >
                      <span
                        style={{
                          width: "6px",
                          height: "6px",
                          borderRadius: "50%",
                          backgroundColor: "#10b981",
                          display: "inline-block",
                        }}
                      />
                      <span style={{ letterSpacing: "0.15em", fontSize: "10px", fontWeight: 600 }}>SYSTEM READY</span>
                    </div>

                    <div
                      style={{
                        marginBottom: "10px",
                        lineHeight: 1.6,
                        color: "var(--color-text-main)",
                        fontWeight: 500,
                        letterSpacing: "0.02em",
                      }}
                    >
                      &gt; Which road projects in Maharashtra have an expenditure-to-cost divergence exceeding 15%?
                    </div>

                    <div style={{ display: "flex", alignItems: "center", marginTop: "8px" }}>
                      <span
                        style={{
                          width: "8px",
                          height: "14px",
                          backgroundColor: "var(--color-primary-900)",
                          display: "inline-block",
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
