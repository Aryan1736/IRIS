import React from "react";
import { useLocation } from "react-router-dom";
import { Header } from "./Header.tsx";
import { Footer } from "./Footer.tsx";

export interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const location = useLocation();
  const isLanding = location.pathname === "/";

  return (
    <div
      style={{
        position: "relative",
        minHeight: "100vh",
        backgroundColor: "var(--color-surface)",
        width: "100%",
        overflowX: "hidden",
      }}
    >
      {/* Full-Page Seamless Architectural Mosaic Background */}
      <div
        className="global-mosaic-bg"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          zIndex: 0,
          backgroundImage: "url('/mosaic-grid.svg')",
          backgroundSize: "1200px 800px",
          backgroundRepeat: "repeat",
          backgroundColor: "var(--color-surface)",
        }}
        aria-hidden="true"
      />

      {/* App Shell Content (Interactive Layer) */}
      <div
        className="app-shell"
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
          width: "100%",
        }}
      >
        <Header />
        <main
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            paddingTop: "64px",
            width: "100%",
          }}
        >
          {children}
        </main>
        {isLanding && <Footer />}
      </div>
    </div>
  );
};
