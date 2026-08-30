import React from "react";

export const DataFoundationSection: React.FC = () => {
  return (
    <section
      id="data"
      className="bg-paper-solid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        position: "relative",
        width: "100%",
      }}
    >
      <div className="container-main">
        {/* Section Heading */}
        <div style={{ textAlign: "center", marginBottom: "64px" }}>
          <h2
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(2.5rem, 5vw, 4.25rem)",
              fontWeight: 700,
              letterSpacing: "-0.03em",
              lineHeight: 0.95,
              textTransform: "uppercase",
              color: "var(--color-primary-900)",
            }}
          >
            EVERY PROJECT HAS A HISTORY.
          </h2>
        </div>

        <div style={{ maxWidth: "1050px", margin: "0 auto" }}>
          {/* Identity Equation Block matching Image 4 */}
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "center",
              flexWrap: "wrap",
              gap: "24px",
              fontFamily: "var(--font-mono)",
              fontSize: "var(--font-size-sm)",
              textTransform: "uppercase",
            }}
          >
            {/* Project Code */}
            <div
              className="hairline-all"
              style={{
                backgroundColor: "#ffffff",
                padding: "36px 32px",
                textAlign: "center",
                width: "230px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  marginBottom: "12px",
                  letterSpacing: "0.15em",
                }}
              >
                IDENTIFIER
              </div>
              <div style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "0.08em" }}>
                PROJECT CODE
              </div>
            </div>

            <div
              style={{
                fontSize: "var(--font-size-2xl)",
                color: "var(--color-text-dim)",
                fontWeight: 400,
              }}
            >
              +
            </div>

            {/* Report Month */}
            <div
              className="hairline-all"
              style={{
                backgroundColor: "#ffffff",
                padding: "36px 32px",
                textAlign: "center",
                width: "230px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  color: "var(--color-text-dim)",
                  marginBottom: "12px",
                  letterSpacing: "0.15em",
                }}
              >
                TEMPORAL
              </div>
              <div style={{ fontWeight: 700, fontSize: "14px", letterSpacing: "0.08em" }}>
                REPORT MONTH
              </div>
            </div>

            <div
              style={{
                fontSize: "var(--font-size-2xl)",
                color: "var(--color-text-dim)",
                fontWeight: 400,
              }}
            >
              =
            </div>

            {/* Observation Result */}
            <div
              style={{
                backgroundColor: "#f2f7f4",
                border: "1px solid var(--color-primary-900)",
                padding: "36px 32px",
                textAlign: "center",
                width: "230px",
              }}
            >
              <div
                style={{
                  fontSize: "10px",
                  color: "var(--color-primary-700)",
                  marginBottom: "12px",
                  letterSpacing: "0.15em",
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

          {/* Lineage Flow Box matching Image 4 */}
          <div
            className="hairline-all"
            style={{
              marginTop: "64px",
              backgroundColor: "#ffffff",
              padding: "40px",
            }}
          >
            <div
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
                color: "var(--color-text-dim)",
                marginBottom: "32px",
                paddingBottom: "14px",
                borderBottom: "1px solid var(--color-border-hairline)",
                letterSpacing: "0.15em",
              }}
            >
              DATA LINEAGE FLOW
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "16px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
              }}
            >
              <div
                className="hairline-all"
                style={{
                  flex: 1,
                  minWidth: "140px",
                  padding: "18px 12px",
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
                  minWidth: "140px",
                  padding: "18px 12px",
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
                  minWidth: "140px",
                  padding: "18px 12px",
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
                  minWidth: "180px",
                  backgroundColor: "var(--color-primary-900)",
                  color: "#ffffff",
                  padding: "18px 12px",
                  textAlign: "center",
                  fontWeight: 700,
                  letterSpacing: "0.1em",
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
