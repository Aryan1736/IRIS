import React from "react";
import { Link } from "react-router-dom";

export const HeroSection: React.FC = () => {
  return (
    <section
      className="bg-mosaic-grid hairline-b"
      style={{
        paddingTop: "11rem",
        paddingBottom: "8rem",
        width: "100%",
      }}
    >
      <div
        className="container-main"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 1fr)",
          gap: "48px",
          alignItems: "start",
        }}
      >
        {/* Left Telemetry Sidebar (2 Columns) */}
        <div
          style={{
            gridColumn: "span 2 / span 2",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            textTransform: "uppercase",
            letterSpacing: "0.15em",
            display: "flex",
            flexDirection: "column",
            gap: "18px",
            paddingTop: "16px",
            position: "sticky",
            top: "140px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              style={{
                width: "6px",
                height: "6px",
                backgroundColor: "var(--color-mint-subtle)",
                borderRadius: "var(--radius-none)",
                display: "inline-block",
              }}
            />
            <span style={{ fontWeight: 600, color: "var(--color-primary-900)" }}>
              SYSTEM STATUS /<br />ONLINE
            </span>
          </div>
          <div style={{ opacity: 0.6 }}>PAIMANA / MoSPI</div>
          <div style={{ opacity: 0.6 }}>INFRASTRUCTURE INTELLIGENCE</div>
          <div style={{ opacity: 0.6 }}>PREDICTIVE MONITORING</div>
          <div style={{ opacity: 0.6 }}>DECISION SUPPORT</div>
        </div>

        {/* Main Headline & Narrative (10 Columns) */}
        <div style={{ gridColumn: "span 10 / span 10" }}>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(3.5rem, 8vw, 7.5rem)",
              fontWeight: 700,
              lineHeight: 0.88,
              letterSpacing: "-0.04em",
              marginBottom: "56px",
              textTransform: "uppercase",
              color: "var(--color-primary-900)",
              maxWidth: "1150px",
            }}
          >
            FROM
            <br />
            INFRASTRUCTURE
            <br />
            MONITORING
            <br />
            TO INTELLIGENCE.
          </h1>

          <div style={{ marginTop: "48px" }}>
            <p
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "clamp(1.125rem, 1.4vw, 1.4rem)",
                maxWidth: "620px",
                marginBottom: "48px",
                opacity: 0.85,
                lineHeight: 1.6,
                color: "var(--color-text-main)",
              }}
            >
              IRIS turns longitudinal infrastructure project data into predictive intelligence — helping
              decision-makers identify cost escalation, schedule delays, and emerging implementation risks before
              they become critical.
            </p>

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "16px",
                fontFamily: "var(--font-mono)",
                fontSize: "var(--font-size-xs)",
              }}
            >
              <Link
                to="/projects"
                style={{
                  backgroundColor: "var(--color-primary-900)",
                  color: "#ffffff",
                  padding: "16px 32px",
                  textTransform: "uppercase",
                  letterSpacing: "0.15em",
                  textDecoration: "none",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  borderRadius: "var(--radius-none)",
                  fontWeight: 600,
                  transition: "background-color 150ms ease",
                }}
              >
                <span>EXPLORE PROJECTS</span>
                <span>→</span>
              </Link>

              <a
                href="#capabilities"
                style={{
                  border: "1px solid var(--color-primary-900)",
                  color: "var(--color-primary-900)",
                  backgroundColor: "transparent",
                  padding: "16px 32px",
                  textTransform: "uppercase",
                  letterSpacing: "0.15em",
                  textDecoration: "none",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  borderRadius: "var(--radius-none)",
                  fontWeight: 600,
                  transition: "background-color 150ms ease",
                }}
              >
                ABOUT IRIS
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
