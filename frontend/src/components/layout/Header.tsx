import React, { useEffect, useState, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { fetchHealth, fetchDatasetInfo } from "@/api/system.ts";
import { Settings, Bell } from "lucide-react";
import { safeAnimate, stagger, prefersReducedMotion } from "@/lib/motion/anime.ts";

export const Header: React.FC = () => {
  const location = useLocation();
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [dateRange, setDateRange] = useState<string>("2023-01 → 2026-07");
  const isLanding = location.pathname === "/";
  const headerInnerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (headerInnerRef.current && !prefersReducedMotion()) {
      safeAnimate(Array.from(headerInnerRef.current.children), {
        opacity: [0, 1],
        translateY: [4, 0],
        delay: stagger(40) as unknown as number,
        duration: 260,
        ease: "outQuad",
      });
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    fetchHealth()
      .then((res) => {
        if (isMounted) setIsBackendHealthy(res.status === "healthy");
      })
      .catch(() => {
        if (isMounted) setIsBackendHealthy(false);
      });

    fetchDatasetInfo()
      .then((info) => {
        if (isMounted && info.covered_months && info.covered_months.length > 0) {
          const sorted = [...info.covered_months].sort();
          setDateRange(`${sorted[0]} → ${sorted[sorted.length - 1]}`);
        }
      })
      .catch(() => {
        // Fallback default
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const navItems = [
    { label: "OVERVIEW", path: "/dashboard" },
    { label: "01. PROJECTS", path: "/projects" },
    { label: "02. ANALYTICS", path: "/analytics" },
    { label: "03. INTELLIGENCE", path: "/intelligence" },
  ];

  return (
    <header
      className="hairline-b"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        backgroundColor: "var(--color-surface)",
        height: "64px",
      }}
    >
      <div
        ref={headerInnerRef}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: "100%",
          paddingLeft: "clamp(20px, 3.5vw, 64px)",
          paddingRight: "clamp(20px, 3.5vw, 64px)",
          width: "100%",
          boxSizing: "border-box",
          gap: "16px",
        }}
      >
        {/* Brand Lockup */}
        <Link
          to="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "14px",
            textDecoration: "none",
            color: "inherit",
            flexShrink: 0,
          }}
          aria-label="IRIS Home"
        >
          <span
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "22px",
              fontWeight: 700,
              letterSpacing: "-0.02em",
              textTransform: "uppercase",
              color: "var(--color-primary-950)",
              lineHeight: 1,
            }}
          >
            IRIS
          </span>
          <span
            style={{
              width: "1px",
              height: "14px",
              backgroundColor: "var(--color-border-hairline)",
              display: "inline-block",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "var(--color-text-dim)",
              display: "inline-block",
            }}
          >
            {isLanding ? "PAIMANA / MoSPI" : "PAIMANA / INFRASTRUCTURE INTELLIGENCE"}
          </span>
        </Link>

        {/* Numbered Navigation */}
        <nav
          style={{
            display: "flex",
            alignItems: "center",
            gap: "28px",
            height: "100%",
            overflowX: "auto",
            whiteSpace: "nowrap",
            scrollbarWidth: "none",
          }}
          aria-label="Main Navigation"
        >
          {navItems.map((item) => {
            const isActive =
              item.path === "/projects"
                ? location.pathname.startsWith("/projects")
                : item.path === "/analytics"
                ? location.pathname.startsWith("/analytics")
                : item.path === "/intelligence"
                ? location.pathname.startsWith("/intelligence")
                : location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  letterSpacing: "0.14em",
                  textTransform: "uppercase",
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? "var(--color-primary-950)" : "var(--color-text-muted)",
                  textDecoration: "none",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  borderBottom: isActive ? "2px solid var(--color-primary-950)" : "2px solid transparent",
                  boxSizing: "border-box",
                  paddingTop: "2px",
                  flexShrink: 0,
                  transition: "color 150ms ease, border-color 150ms ease",
                }}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Right CTA Button or Operational Telemetry */}
        {isLanding ? (
          <div style={{ display: "flex", alignItems: "center", gap: "16px", flexShrink: 0 }}>
            {isBackendHealthy !== null && (
              <div
                style={{
                  alignItems: "center",
                  gap: "6px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--color-text-variant)",
                  display: "none",
                }}
              >
                <span
                  style={{
                    width: "6px",
                    height: "6px",
                    borderRadius: "var(--radius-sm)",
                    backgroundColor: isBackendHealthy
                      ? "var(--color-mint-subtle)"
                      : "var(--color-risk-high)",
                    display: "inline-block",
                  }}
                />
                <span>{isBackendHealthy ? "SYSTEM / ONLINE" : "SYSTEM / OFFLINE"}</span>
              </div>
            )}
            <Link
              to="/dashboard"
              style={{
                backgroundColor: "var(--color-primary-900)",
                color: "#ffffff",
                padding: "10px 24px",
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                textDecoration: "none",
                borderRadius: "var(--radius-none)",
                fontWeight: 600,
                transition: "background-color 150ms ease",
                display: "inline-block",
              }}
            >
              ENTER IRIS
            </Link>
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: "20px", flexShrink: 0 }}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-end",
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: "var(--color-text-dim)",
                lineHeight: 1.4,
              }}
            >
              <span>DATA: {dateRange}</span>
              <span style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <span
                  style={{
                    width: "6px",
                    height: "6px",
                    backgroundColor: isBackendHealthy === null ? "var(--color-text-dim)" : isBackendHealthy ? "var(--color-primary-950)" : "var(--color-risk-high)",
                    display: "inline-block",
                  }}
                />
                SYSTEM STATUS / {isBackendHealthy === null ? "CHECKING" : isBackendHealthy ? "ONLINE" : "OFFLINE"}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <button
                type="button"
                aria-label="Settings"
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--color-text-muted)",
                  padding: "6px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "color 150ms ease",
                }}
              >
                <Settings size={18} />
              </button>

              <button
                type="button"
                aria-label="Notifications"
                style={{
                  background: "transparent",
                  border: "none",
                  color: "var(--color-text-muted)",
                  padding: "6px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "color 150ms ease",
                }}
              >
                <Bell size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
