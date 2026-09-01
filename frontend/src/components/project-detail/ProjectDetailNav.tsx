import React from "react";
import { Link } from "react-router-dom";

export const ProjectDetailNav: React.FC = () => {
  return (
    <nav className="project-detail-bottom-nav" aria-label="Project Detail Navigation">
      <Link to="/projects" style={{ fontWeight: 600 }}>
        ← BACK TO PROJECTS
      </Link>
      <div style={{ display: "flex", alignItems: "center", gap: "24px", flexWrap: "wrap" }}>
        <Link to="/dashboard">
          DASHBOARD OVERVIEW
        </Link>
        <Link to="/analytics">
          PORTFOLIO ANALYTICS
        </Link>
        <Link to="/intelligence">
          RISK INTELLIGENCE
        </Link>
        <Link to="/projects">
          SEARCH ALL PROJECTS →
        </Link>
      </div>
    </nav>
  );
};
