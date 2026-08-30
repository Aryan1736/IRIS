import React from "react";

export const EvolutionSection: React.FC = () => {
  const metadataTaxonomy = ["SECTOR", "STATE", "MINISTRY", "AGENCY", "PROJECT", "TIME"];

  return (
    <section
      id="intelligence"
      className="bg-paper-solid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        position: "relative",
        width: "100%",
      }}
    >
      <div className="container-main">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(12, 1fr)",
            gap: "56px",
            alignItems: "start",
          }}
        >
          {/* Left Column (4 Columns): Evolution Phases matching Image 6 */}
          <div
            style={{
              gridColumn: "span 4 / span 4",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <h2
              style={{
                fontFamily: "var(--font-heading)",
                fontSize: "clamp(2rem, 3.5vw, 3.25rem)",
                fontWeight: 700,
                letterSpacing: "-0.03em",
                lineHeight: 0.95,
                textTransform: "uppercase",
                marginBottom: "32px",
                color: "var(--color-primary-900)",
              }}
            >
              EVOLUTION OF
              <br />
              INTELLIGENCE
            </h2>

            <p
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "var(--font-size-base)",
                lineHeight: 1.6,
                opacity: 0.85,
                marginBottom: "48px",
                color: "var(--color-text-main)",
              }}
            >
              The IRIS architecture is designed to progressively build upon its source-faithful data
              foundation, moving from basic reporting to advanced predictive analytics.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "28px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
                textTransform: "uppercase",
              }}
            >
              {/* Phase 01 */}
              <div
                style={{
                  border: "1px solid #A4CBB8",
                  backgroundColor: "#ffffff",
                  padding: "24px",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-6px",
                    top: "-6px",
                    width: "14px",
                    height: "14px",
                    backgroundColor: "#A4CBB8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "8px",
                  }}
                >
                  1
                </div>
                <div style={{ color: "#5E9B7D", fontWeight: 600, fontSize: "10px", marginBottom: "8px", letterSpacing: "0.1em" }}>
                  PHASE 01 / ACTIVE
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  SOURCE DATA FOUNDATION
                </div>
              </div>

              {/* Phase 02 */}
              <div
                style={{
                  border: "1px solid #A4CBB8",
                  backgroundColor: "#ffffff",
                  padding: "24px",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-6px",
                    top: "-6px",
                    width: "14px",
                    height: "14px",
                    backgroundColor: "#A4CBB8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "8px",
                  }}
                >
                  2
                </div>
                <div style={{ color: "#5E9B7D", fontWeight: 600, fontSize: "10px", marginBottom: "8px", letterSpacing: "0.1em" }}>
                  PHASE 02 / ACTIVE
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  LONGITUDINAL PROCESSING
                </div>
              </div>

              {/* Phase 03 */}
              <div
                style={{
                  border: "1px solid #A4CBB8",
                  backgroundColor: "#ffffff",
                  padding: "24px",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    left: "-6px",
                    top: "-6px",
                    width: "14px",
                    height: "14px",
                    backgroundColor: "#A4CBB8",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#ffffff",
                    fontWeight: 700,
                    fontSize: "8px",
                  }}
                >
                  3
                </div>
                <div style={{ color: "#5E9B7D", fontWeight: 600, fontSize: "10px", marginBottom: "8px", letterSpacing: "0.1em" }}>
                  PHASE 03 / ACTIVE
                </div>
                <div style={{ fontWeight: 700, fontSize: "13px", color: "var(--color-primary-900)", letterSpacing: "0.08em" }}>
                  DECISION SUPPORT
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (8 Columns): Taxonomy & Terminal matching Image 6 */}
          <div style={{ gridColumn: "span 8 / span 8" }}>
            <div
              className="hairline-all"
              style={{
                backgroundColor: "#ffffff",
                height: "100%",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <div
                style={{
                  padding: "48px",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <h3
                  style={{
                    fontFamily: "var(--font-heading)",
                    fontSize: "var(--font-size-2xl)",
                    fontWeight: 700,
                    marginBottom: "28px",
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
                    gap: "12px",
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    marginBottom: "36px",
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
                        fontWeight: 500,
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
                    paddingTop: "36px",
                  }}
                >
                  <h3
                    style={{
                      fontFamily: "var(--font-heading)",
                      fontSize: "var(--font-size-2xl)",
                      fontWeight: 700,
                      marginBottom: "16px",
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
                      marginBottom: "28px",
                      color: "var(--color-text-main)",
                      lineHeight: 1.6,
                    }}
                  >
                    IRIS Intelligence provides an analytical layer over data, enabling natural language querying of
                    complex infrastructure portfolios.
                  </p>

                  {/* Terminal Visual Window */}
                  <div
                    className="hairline-all"
                    style={{
                      backgroundColor: "#FAF9F6",
                      padding: "28px",
                      fontFamily: "var(--font-mono)",
                      fontSize: "var(--font-size-xs)",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        marginBottom: "16px",
                        color: "var(--color-text-dim)",
                      }}
                    >
                      <span
                        style={{
                          width: "6px",
                          height: "6px",
                          borderRadius: "50%",
                          backgroundColor: "#A4CBB8",
                          display: "inline-block",
                        }}
                      />
                      <span style={{ letterSpacing: "0.15em", fontSize: "10px" }}>SYSTEM READY</span>
                    </div>

                    <div
                      style={{
                        marginBottom: "12px",
                        lineHeight: 1.6,
                        color: "var(--color-text-main)",
                        fontWeight: 500,
                        letterSpacing: "0.02em",
                      }}
                    >
                      &gt; Which road projects in Maharashtra have a cost overrun exceeding 10%?
                    </div>

                    <div style={{ display: "flex", alignItems: "center", marginTop: "8px" }}>
                      <span
                        style={{
                          width: "8px",
                          height: "14px",
                          backgroundColor: "#A4CBB8",
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
