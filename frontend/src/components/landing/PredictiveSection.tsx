import React from "react";

export const PredictiveSection: React.FC = () => {
  return (
    <section
      id="predictive"
      className="bg-mosaic-grid hairline-b"
      style={{
        paddingTop: "8rem",
        paddingBottom: "8rem",
        width: "100%",
      }}
    >
      <div className="container-main">
        {/* Section Heading */}
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
            SEE THE RISK BEFORE IT
            <br />
            BECOMES THE OUTCOME.
          </h2>
        </div>

        {/* 4 Architectural Cards with Grid Hairlines matching Image 5 */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "1px",
            backgroundColor: "var(--color-border-hairline)",
            border: "1px solid var(--color-border-hairline)",
          }}
        >
          {/* PI-01: Cost Overrun Prediction */}
          <div
            style={{
              backgroundColor: "#ffffff",
              padding: "36px 28px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: "260px",
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid var(--color-border-hairline)",
                  letterSpacing: "0.15em",
                }}
              >
                [ PI-01 ]
              </div>
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 700,
                  marginBottom: "16px",
                  textTransform: "uppercase",
                  letterSpacing: "-0.01em",
                  color: "var(--color-primary-900)",
                  lineHeight: 1.2,
                }}
              >
                COST OVERRUN
                <br />
                PREDICTION
              </h3>
            </div>

            <div
              className="hairline-all"
              style={{
                height: "90px",
                marginTop: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#ffffff",
                padding: "16px",
              }}
            >
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  gap: "6px",
                }}
              >
                <div style={{ width: "100%", height: "10px", backgroundColor: "#D9E8DF" }} />
                <div style={{ width: "100%", height: "10px", backgroundColor: "#A4CBB8" }} />
                <div style={{ width: "100%", height: "10px", backgroundColor: "#FF8A65" }} />
              </div>
            </div>
          </div>

          {/* PI-02: Schedule Delay Prediction */}
          <div
            style={{
              backgroundColor: "#ffffff",
              padding: "36px 28px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: "260px",
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid var(--color-border-hairline)",
                  letterSpacing: "0.15em",
                }}
              >
                [ PI-02 ]
              </div>
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 700,
                  marginBottom: "16px",
                  textTransform: "uppercase",
                  letterSpacing: "-0.01em",
                  color: "var(--color-primary-900)",
                  lineHeight: 1.2,
                }}
              >
                SCHEDULE DELAY
                <br />
                PREDICTION
              </h3>
            </div>

            <div
              className="hairline-all"
              style={{
                height: "90px",
                marginTop: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#ffffff",
                padding: "16px 20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  alignItems: "flex-end",
                  height: "100%",
                  width: "100%",
                }}
              >
                <div style={{ flex: 1, height: "45%", backgroundColor: "#D9E8DF" }} />
                <div style={{ flex: 1, height: "100%", backgroundColor: "#A4CBB8" }} />
                <div style={{ flex: 1, height: "65%", backgroundColor: "#FF8A65" }} />
              </div>
            </div>
          </div>

          {/* PI-03: Project Risk Scoring */}
          <div
            style={{
              backgroundColor: "#ffffff",
              padding: "36px 28px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: "260px",
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid var(--color-border-hairline)",
                  letterSpacing: "0.15em",
                }}
              >
                [ PI-03 ]
              </div>
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 700,
                  marginBottom: "16px",
                  textTransform: "uppercase",
                  letterSpacing: "-0.01em",
                  color: "var(--color-primary-900)",
                  lineHeight: 1.2,
                }}
              >
                PROJECT RISK
                <br />
                SCORING
              </h3>
            </div>

            <div
              className="hairline-all"
              style={{
                height: "90px",
                marginTop: "20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#ffffff",
              }}
            >
              <div
                style={{
                  width: "48px",
                  height: "48px",
                  borderRadius: "50%",
                  border: "3px solid #FF8A65",
                  borderTopColor: "#A4CBB8",
                  borderRightColor: "#A4CBB8",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  fontWeight: 600,
                  color: "var(--color-text-dim)",
                }}
              >
                84
              </div>
            </div>
          </div>

          {/* PI-04: Early Warning Signals */}
          <div
            style={{
              backgroundColor: "#ffffff",
              padding: "36px 28px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              minHeight: "260px",
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--color-text-dim)",
                  marginBottom: "20px",
                  paddingBottom: "12px",
                  borderBottom: "1px solid var(--color-border-hairline)",
                  letterSpacing: "0.15em",
                }}
              >
                [ PI-04 ]
              </div>
              <h3
                style={{
                  fontFamily: "var(--font-heading)",
                  fontSize: "var(--font-size-base)",
                  fontWeight: 700,
                  marginBottom: "16px",
                  textTransform: "uppercase",
                  letterSpacing: "-0.01em",
                  color: "var(--color-primary-900)",
                  lineHeight: 1.2,
                }}
              >
                EARLY WARNING
                <br />
                SIGNALS
              </h3>
            </div>

            <div
              className="hairline-all"
              style={{
                height: "90px",
                marginTop: "20px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "#ffffff",
                padding: "16px",
                gap: "5px",
              }}
            >
              <div style={{ width: "100%", height: "4px", backgroundColor: "#FFE0D6" }} />
              <div style={{ width: "100%", height: "4px", backgroundColor: "#FFCCBC" }} />
              <div style={{ width: "100%", height: "4px", backgroundColor: "#FFA88E" }} />
              <div style={{ width: "100%", height: "4px", backgroundColor: "#FF8A65" }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
