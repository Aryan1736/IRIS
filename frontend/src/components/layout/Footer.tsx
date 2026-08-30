import React from "react";
import { Link } from "react-router-dom";

export const Footer: React.FC = () => {
  return (
    <footer
      className="hairline-t"
      style={{
        backgroundColor: "var(--color-surface)",
        paddingTop: "24px",
        paddingBottom: "24px",
        position: "relative",
        zIndex: 10,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "24px",
          paddingLeft: "var(--space-6)",
          paddingRight: "var(--space-6)",
          width: "100%",
          maxWidth: "var(--max-width-content)",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        {/* Left: Brand Lockup */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
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
        </div>

        {/* Center: Institutional Links */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "36px",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
          }}
        >
          <a
            href="#data"
            style={{
              color: "var(--color-text-dim)",
              textDecoration: "none",
              transition: "color 150ms ease",
            }}
          >
            DOCUMENTATION
          </a>
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
        </div>

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
