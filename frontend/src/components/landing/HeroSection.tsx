import React from "react";
import { Link } from "react-router-dom";
import { TypingHeadline } from "./TypingHeadline.tsx";
import { usePageEnter } from "@/lib/motion/useMotion.ts";

const HERO_HEADLINE_LINES = [
  "FROM",
  "INFRASTRUCTURE",
  "MONITORING",
  "TO INTELLIGENCE.",
];

export const HeroSection: React.FC = () => {
  const heroRef = usePageEnter<HTMLElement>();

  return (
    <section
      ref={heroRef}
      className="landing-section hairline-b"
      style={{
        paddingTop: "clamp(6.5rem, 10vw, 11rem)",
        paddingBottom: "clamp(4.5rem, 7vw, 8rem)",
        width: "100%",
        position: "relative",
      }}
    >
      <div
        className="container-main"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(12, 1fr)",
          gap: "clamp(24px, 4vw, 56px)",
          alignItems: "start",
        }}
      >
        {/* Left Telemetry Sidebar (3 Columns on Desktop) */}
        <div
          style={{
            gridColumn: "span 3 / span 3",
            position: "sticky",
            top: "120px",
          }}
          className="landing-reveal-item"
        >
          <div className="hero-telemetry-panel">
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span className="hero-status-beacon" aria-hidden="true" />
              <span style={{ fontWeight: 700, color: "var(--color-primary-900)" }}>
                SYSTEM STATUS /<br />ONLINE
              </span>
            </div>

            <div
              style={{
                height: "1px",
                backgroundColor: "var(--color-border-hairline)",
                margin: "4px 0",
              }}
            />

            <div style={{ opacity: 0.65, fontSize: "10px" }}>PAIMANA / MoSPI</div>
            <div style={{ opacity: 0.65, fontSize: "10px" }}>INFRASTRUCTURE INTELLIGENCE</div>
            <div style={{ opacity: 0.65, fontSize: "10px" }}>PREDICTIVE MONITORING</div>
            <div style={{ opacity: 0.65, fontSize: "10px" }}>DECISION SUPPORT</div>

            <div
              style={{
                height: "1px",
                backgroundColor: "var(--color-border-hairline)",
                margin: "4px 0",
              }}
            />

            <div
              style={{
                fontSize: "9px",
                color: "var(--color-text-dim)",
                letterSpacing: "0.18em",
              }}
            >
              EST. 2026 / FLASH REPORTS
            </div>
          </div>
        </div>

        {/* Main Headline & Narrative (9 Columns) */}
        <div
          style={{ gridColumn: "span 9 / span 9" }}
          className="landing-reveal-item"
        >
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "clamp(3.25rem, 7.5vw, 7.25rem)",
              fontWeight: 700,
              lineHeight: 0.88,
              letterSpacing: "-0.04em",
              marginBottom: "40px",
              textTransform: "uppercase",
              color: "var(--color-primary-900)",
              maxWidth: "1150px",
            }}
          >
            <TypingHeadline lines={HERO_HEADLINE_LINES} speedMs={50} />
          </h1>

          <div style={{ marginTop: "36px" }}>
            <p className="landing-section-desc" style={{ marginBottom: "40px" }}>
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
              <Link to="/projects" className="hero-cta-button-primary">
                <span>EXPLORE PROJECTS</span>
                <span>→</span>
              </Link>

              <a href="#capabilities" className="hero-cta-button-secondary">
                ABOUT IRIS
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
