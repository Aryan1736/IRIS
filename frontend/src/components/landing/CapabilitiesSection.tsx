import React from "react";
import { Link } from "react-router-dom";
import { useScrollReveal } from "@/lib/motion/useMotion.ts";

interface Capability {
  index: string;
  title: string;
  description: string;
  linkTo: string;
  tag: string;
}

const CAPABILITIES: Capability[] = [
  {
    index: "01",
    title: "PROJECT DISCOVERY",
    description: "Search and filter 1,800+ infrastructure projects across ministries, agencies, states, and sectors.",
    linkTo: "/projects",
    tag: "CATALOG",
  },
  {
    index: "02",
    title: "PROJECT HISTORY",
    description: "Trace how each project evolves month-by-month across historical reporting periods with zero invented data.",
    linkTo: "/projects",
    tag: "TRAJECTORY",
  },
  {
    index: "03",
    title: "COST INTELLIGENCE",
    description: "Track original vs revised cost variance and quantify cumulative expenditure trends across the entire portfolio.",
    linkTo: "/analytics",
    tag: "EXPENDITURE",
  },
  {
    index: "04",
    title: "SCHEDULE INTELLIGENCE",
    description: "Analyse completion timelines, original vs anticipated milestones, and emerging implementation delays.",
    linkTo: "/analytics",
    tag: "SCHEDULE",
  },
  {
    index: "05",
    title: "RISK & EARLY WARNING",
    description: "Surface critical projects requiring immediate attention before budget escalations and schedule slips compound.",
    linkTo: "/intelligence",
    tag: "PREDICTIVE",
  },
  {
    index: "06",
    title: "PORTFOLIO INTELLIGENCE",
    description: "Compare sector allocations, implementing agencies, and state-level infrastructure development metrics.",
    linkTo: "/dashboard",
    tag: "MACRO",
  },
];

export const CapabilitiesSection: React.FC = () => {
  const sectionRef = useScrollReveal<HTMLElement>({
    childSelector: ".landing-reveal-item",
    staggerTime: 45,
  });

  return (
    <section
      id="capabilities"
      ref={sectionRef}
      className="landing-section landing-section-light hairline-b"
    >
      <div className="container-main">
        {/* Section Heading */}
        <div style={{ marginBottom: "48px" }} className="landing-reveal-item">
          <div className="landing-section-badge">
            <span className="landing-section-badge-dot" />
            <span>[ 02 / CAPABILITIES ]</span>
          </div>

          <h2 className="landing-section-heading">
            MONITOR WHAT CHANGES
          </h2>

          <p className="landing-section-desc">
            Six foundational intelligence capabilities built directly on source-faithful monthly
            flash report data to empower policy and decision makers with institutional clarity.
          </p>
        </div>

        {/* 6-Grid Capabilities with Hairline Grid Borders */}
        <div
          className="landing-grid-container"
          style={{
            gridTemplateColumns: "repeat(3, 1fr)",
          }}
        >
          {CAPABILITIES.map((cap) => (
            <Link
              key={cap.index}
              to={cap.linkTo}
              className="landing-card landing-reveal-item"
              style={{
                textDecoration: "none",
                color: "inherit",
                minHeight: "240px",
              }}
            >
              {/* Card Header */}
              <div className="landing-card-header">
                <span>[ {cap.index} ]</span>
                <span
                  style={{
                    fontSize: "9px",
                    fontWeight: 700,
                    letterSpacing: "0.12em",
                    color: "var(--color-primary-800)",
                    backgroundColor: "var(--color-primary-50)",
                    padding: "3px 8px",
                  }}
                >
                  {cap.tag}
                </span>
              </div>

              {/* Card Title & Description */}
              <h3 className="landing-card-title">
                {cap.title}
              </h3>

              <p className="landing-card-body">
                {cap.description}
              </p>

              {/* Action Arrow */}
              <div className="landing-card-arrow">
                <span>EXPLORE</span>
                <span>→</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};
