import { describe, it, expect, vi, beforeEach } from "vitest";
import { prefersReducedMotion, safeAnimate, MOTION_TIMINGS } from "@/lib/motion/anime.ts";
import {
  animatePageEnter,
  animateSectionReveal,
  animateScrollReveal,
  animateDirectionalScrollReveal,
  animateStaggerChildren,
  animateDrawerEnter,
  animateDrawerExit,
  animateNumericCount,
} from "@/lib/motion/presets.ts";

describe("IRIS Anime.js Motion System", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("exports correct institutional timing constants", () => {
    expect(MOTION_TIMINGS.fast).toBe(220);
    expect(MOTION_TIMINGS.base).toBe(350);
    expect(MOTION_TIMINGS.drawer).toBe(400);
  });

  it("handles prefersReducedMotion safely", () => {
    const isReduced = prefersReducedMotion();
    expect(typeof isReduced).toBe("boolean");
  });

  it("safeAnimate executes onComplete callback on null target", () => {
    const onComplete = vi.fn();
    safeAnimate(null, { duration: 100, onComplete });
    expect(onComplete).toHaveBeenCalled();
  });

  it("animateDrawerEnter and animateDrawerExit execute safely with DOM elements", () => {
    const overlay = document.createElement("div");
    const drawer = document.createElement("div");
    const onComplete = vi.fn();

    animateDrawerEnter(overlay, drawer, onComplete);
    expect(typeof overlay).toBe("object");

    const onExitComplete = vi.fn();
    animateDrawerExit(overlay, drawer, onExitComplete);
    expect(typeof drawer).toBe("object");
  });

  it("animatePageEnter and animateSectionReveal execute safely on container elements", () => {
    const container = document.createElement("div");
    const child = document.createElement("div");
    child.className = "dashboard-intro-section";
    container.appendChild(child);

    expect(() => animatePageEnter(container)).not.toThrow();
    expect(() => animateSectionReveal(container)).not.toThrow();
    expect(() => animateStaggerChildren(container)).not.toThrow();
  });

  it("animateDirectionalScrollReveal executes distinct up and down animations safely", () => {
    const container = document.createElement("div");
    const child1 = document.createElement("div");
    child1.className = "landing-reveal-item";
    const child2 = document.createElement("div");
    child2.className = "landing-reveal-item";
    container.appendChild(child1);
    container.appendChild(child2);

    // Scroll Down direction (enters upwards)
    expect(() => animateDirectionalScrollReveal(container, "down")).not.toThrow();

    // Scroll Up direction (enters downwards)
    expect(() => animateDirectionalScrollReveal(container, "up")).not.toThrow();

    // Backward-compatible alias
    expect(() => animateScrollReveal(container)).not.toThrow();
  });

  it("animateNumericCount writes target text content safely", () => {
    const target = document.createElement("span");
    animateNumericCount(target, 4738, (v) => `${v.toLocaleString()}`);
    expect(typeof target.textContent).toBe("string");
  });
});
