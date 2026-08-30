import React from "react";
import { HeroSection } from "@/components/landing/HeroSection.tsx";
import { TimelineSection } from "@/components/landing/TimelineSection.tsx";
import { CapabilitiesSection } from "@/components/landing/CapabilitiesSection.tsx";
import { DataFoundationSection } from "@/components/landing/DataFoundationSection.tsx";
import { PredictiveSection } from "@/components/landing/PredictiveSection.tsx";
import { EvolutionSection } from "@/components/landing/EvolutionSection.tsx";
import { AuditabilitySection } from "@/components/landing/AuditabilitySection.tsx";
import { CtaSection } from "@/components/landing/CtaSection.tsx";

export const LandingPage: React.FC = () => {
  return (
    <div style={{ width: "100%", overflowX: "hidden" }}>
      <HeroSection />
      <TimelineSection />
      <CapabilitiesSection />
      <DataFoundationSection />
      <PredictiveSection />
      <EvolutionSection />
      <AuditabilitySection />
      <CtaSection />
    </div>
  );
};

export default LandingPage;
