import React from "react";
import { Link } from "react-router-dom";

export const Footer: React.FC = () => {
  return (
    <footer
      className="hairline-t"
      aria-label="Institutional Footer"
      style={{
        backgroundColor: "var(--color-surface)",
        paddingTop: "24px",
        paddingBottom: "24px",
        position: "relative",
        zIndex: 10,
        width: "100%",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "24px",
          paddingLeft: "clamp(20px, 3.5vw, 64px)",
          paddingRight: "clamp(20px, 3.5vw, 64px)",
          width: "100%",
          boxSizing: "border-box",
        }}
      >
        {/* Left: Brand Lockup */}
        <Link
          to="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            textDecoration: "none",
            color: "inherit",
          }}
          aria-label="IRIS Home"
        >
          <span
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "14px",
              fontWeight: 700,
              letterSpacing: "-0.01em",
              textTransform: "uppercase",
              color: "var(--color-primary-900)",
            }}
          >
            IRIS
          </span>
          <span
            style={{
              width: "1px",
              height: "12px",
              backgroundColor: "var(--color-border-hairline)",
              display: "inline-block",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--color-text-dim)",
            }}
          >
            PAIMANA / MoSPI
          </span>
        </Link>

        {/* Center: Institutional Links */}
        <nav
          style={{
            display: "flex",
            alignItems: "center",
            gap: "32px",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            flexWrap: "wrap",
          }}
          aria-label="Footer Navigation"
        >
          <Link
            to="/dashboard"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            OVERVIEW
          </Link>
          <Link
            to="/projects"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            PROJECTS
          </Link>
          <Link
            to="/analytics"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            ANALYTICS
          </Link>
          <Link
            to="/intelligence"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            INTELLIGENCE
          </Link>
          <Link
            to="/#data"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            DOCUMENTATION
          </Link>
        </nav>

        {/* Right: Operational Status & Legal */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "28px",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--color-text-dim)",
          }}
        >
          <span>SYSTEM STATUS</span>
          <span>TERMS</span>
        </div>
      </div>
    </footer>
  );
};
