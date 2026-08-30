import React from "react";
import { Link } from "react-router-dom";

export const ProjectDetailNav: React.FC = () => {
  return (
    <nav className="project-detail-bottom-nav">
      <Link to="/projects" style={{ fontWeight: 600 }}>
        ← BACK TO PROJECTS
      </Link>
      <div style={{ display: "flex", gap: "24px" }}>
        <Link to="/dashboard">
          DASHBOARD OVERVIEW
        </Link>
        <Link to="/projects">
          SEARCH ALL PROJECTS →
        </Link>
      </div>
    </nav>
  );
};
