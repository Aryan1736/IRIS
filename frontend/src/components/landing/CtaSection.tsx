import React from "react";
import { Link } from "react-router-dom";

export const CtaSection: React.FC = () => {
  return (
    <section
      style={{
        paddingTop: "9rem",
        paddingBottom: "9rem",
        backgroundColor: "var(--color-primary-900)",
        color: "#ffffff",
        textAlign: "center",
        position: "relative",
        zIndex: 10,
      }}
    >
      <div
        className="container-main"
        style={{
          maxWidth: "1050px",
          position: "relative",
          zIndex: 10,
        }}
      >
        <h2
          style={{
            fontFamily: "var(--font-heading)",
            fontSize: "clamp(2.75rem, 6vw, 5.5rem)",
            fontWeight: 700,
            letterSpacing: "-0.03em",
            lineHeight: 0.9,
            textTransform: "uppercase",
            marginBottom: "56px",
          }}
        >
          EXPLORE THE
          <br />
          INFRASTRUCTURE PORTFOLIO.
        </h2>

        <div
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
            to="/projects"
            style={{
              backgroundColor: "#ffffff",
              color: "var(--color-primary-900)",
              padding: "18px 44px",
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              fontWeight: 700,
              textDecoration: "none",
              borderRadius: "var(--radius-none)",
              transition: "background-color 150ms ease",
              display: "inline-block",
            }}
          >
            ENTER IRIS
          </Link>

          <Link
            to="/projects"
            style={{
              border: "1px solid rgba(255, 255, 255, 0.4)",
              color: "#ffffff",
              backgroundColor: "transparent",
              padding: "18px 44px",
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              textDecoration: "none",
              borderRadius: "var(--radius-none)",
              fontWeight: 500,
              transition: "background-color 150ms ease",
              display: "inline-block",
            }}
          >
            EXPLORE PROJECTS
          </Link>
        </div>
      </div>
    </section>
  );
};
