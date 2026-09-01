import React from "react";
import { Link } from "react-router-dom";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

export const CtaSection: React.FC = () => {
  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 40,
  });

  return (
    <section
      ref={sectionRef}
      className="landing-section landing-section-dark"
      style={{
        paddingTop: "clamp(6rem, 9vw, 10rem)",
        paddingBottom: "clamp(6rem, 9vw, 10rem)",
        textAlign: "center",
        zIndex: 10,
        position: "relative",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
      }}
    >
      <div
        className="container-main"
        style={{
          maxWidth: "1050px",
          margin: "0 auto",
          position: "relative",
          zIndex: 10,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <div className="landing-reveal-item" style={{ marginBottom: "20px" }}>
          <div
            className="landing-section-badge"
            style={{
              justifyContent: "center",
              color: "rgba(255, 255, 255, 0.7)",
            }}
          >
            <span
              className="landing-section-badge-dot"
              style={{ backgroundColor: "#10b981" }}
            />
            <span>[ SYSTEM READY / FULL PORTFOLIO ]</span>
          </div>
        </div>

        <h2
          className="landing-section-heading landing-section-heading-dark landing-reveal-item"
          style={{
            fontSize: "clamp(2.75rem, 6vw, 5.5rem)",
            lineHeight: 0.9,
            marginBottom: "40px",
          }}
        >
          EXPLORE THE
          <br />
          INFRASTRUCTURE PORTFOLIO.
        </h2>

        <p
          className="landing-reveal-item"
          style={{
            fontFamily: "var(--font-sans)",
            fontSize: "clamp(1.05rem, 1.3vw, 1.35rem)",
            lineHeight: 1.6,
            color: "rgba(255, 255, 255, 0.85)",
            maxWidth: "640px",
            margin: "0 auto 48px",
          }}
        >
          Access verified longitudinal project histories, multi-factor risk assessments, and
          actionable portfolio intelligence.
        </p>

        <div
          className="landing-reveal-item"
          style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: "20px",
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
          }}
        >
          <Link
            to="/dashboard"
            style={{
              backgroundColor: "#ffffff",
              color: "var(--color-primary-900)",
              padding: "18px 44px",
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              fontWeight: 700,
              textDecoration: "none",
              borderRadius: "var(--radius-none)",
              transition: "transform 160ms ease, background-color 160ms ease, box-shadow 160ms ease",
              display: "inline-block",
              border: "1px solid #ffffff",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.boxShadow = "0 6px 20px rgba(0, 0, 0, 0.25)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            ENTER IRIS
          </Link>

          <Link
            to="/projects"
            style={{
              border: "1px solid rgba(255, 255, 255, 0.5)",
              color: "#ffffff",
              backgroundColor: "transparent",
              padding: "18px 44px",
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              textDecoration: "none",
              borderRadius: "var(--radius-none)",
              fontWeight: 600,
              transition: "transform 160ms ease, background-color 160ms ease, border-color 160ms ease",
              display: "inline-block",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-2px)";
              e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
              e.currentTarget.style.borderColor = "#ffffff";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.backgroundColor = "transparent";
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.5)";
            }}
          >
            EXPLORE PROJECTS
          </Link>
        </div>
      </div>
    </section>
  );
};
