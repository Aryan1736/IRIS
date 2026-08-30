import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppLayout } from "@/components/layout/AppLayout.tsx";
import { ErrorBoundary } from "@/components/common/ErrorBoundary.tsx";
import { LandingPage } from "@/pages/LandingPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { ProjectsPage } from "@/pages/ProjectsPage";
import { ProjectDetailPage } from "@/pages/ProjectDetailPage";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { IntelligencePage } from "@/pages/IntelligencePage";
import { Card } from "@/components/ui/Card.tsx";
import { TechnicalLabel } from "@/components/ui/TechnicalLabel.tsx";
import { Button } from "@/components/ui/Button.tsx";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5,
    },
  },
});

const RoutePlaceholder: React.FC<{ title: string; screenRef: string; description: string }> = ({
  title,
  screenRef,
  description,
}) => {
  return (
    <div className="container-main" style={{ padding: "12rem 0 8rem 0" }}>
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        <TechnicalLabel label="ROUTING READY" sublabel={screenRef} />
        <Card
          style={{ marginTop: "16px" }}
          padding="lg"
          title={title}
          subtitle="SCREEN ISOLATION PASS PENDING"
        >
          <p
            style={{
              fontFamily: "var(--font-sans)",
              fontSize: "var(--font-size-base)",
              color: "var(--color-text-variant)",
              lineHeight: 1.6,
              marginBottom: "24px",
            }}
          >
            {description}
          </p>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <Link to="/" style={{ textDecoration: "none" }}>
              <Button variant="primary" size="sm">
                ← RETURN TO OVERVIEW
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <BrowserRouter>
          <AppLayout>
            <Routes>
              {/* 01: Landing Page */}
              <Route path="/" element={<LandingPage />} />

              {/* 02: Dashboard Overview */}
              <Route path="/dashboard" element={<DashboardPage />} />

              {/* 03: Projects / Discovery */}
              <Route path="/projects" element={<ProjectsPage />} />

              {/* 04: Project Detail */}
              <Route path="/projects/:projectCode" element={<ProjectDetailPage />} />

              {/* 05: Analytics / Portfolio Analysis */}
              <Route path="/analytics" element={<AnalyticsPage />} />

              {/* 06: Intelligence / Early Warning */}
              <Route path="/intelligence" element={<IntelligencePage />} />

              {/* Fallback 404 */}
              <Route
                path="*"
                element={
                  <RoutePlaceholder
                    title="404 — Page Unmapped"
                    screenRef="NOT FOUND"
                    description="The requested route is unmapped in the current IRIS system."
                  />
                }
              />
            </Routes>
          </AppLayout>
        </BrowserRouter>
      </ErrorBoundary>
    </QueryClientProvider>
  );
};

export default App;
