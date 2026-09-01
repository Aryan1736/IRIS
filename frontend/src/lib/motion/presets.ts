import { safeAnimate, stagger, MOTION_TIMINGS, MOTION_EASINGS, prefersReducedMotion } from "./anime.ts";

/**
 * Animates a page shell and its direct header/intro children on initial mount.
 */
export const animatePageEnter = (
  container: HTMLElement | null,
  childSelector = ".projects-intro-section, .dashboard-intro-section, .analytics-intro-header, .intelligence-intro-header, .dashboard-metrics-grid, .projects-metric-panel, .portfolio-snapshot-section, .search-section, .filters-bar"
) => {
  if (!container || prefersReducedMotion()) return;

  const children = container.querySelectorAll(childSelector);
  if (children.length > 0) {
    safeAnimate(children, {
      opacity: [0, 1],
      translateY: [8, 0],
      delay: stagger(MOTION_TIMINGS.staggerStep * 1.5, { start: 30 }),
      duration: MOTION_TIMINGS.base,
      ease: MOTION_EASINGS.outCubic,
    });
  } else {
    safeAnimate(container, {
      opacity: [0, 1],
      translateY: [6, 0],
      duration: MOTION_TIMINGS.base,
      ease: MOTION_EASINGS.outCubic,
    });
  }
};

/**
 * Section entrance reveal when triggered by IntersectionObserver.
 */
export const animateSectionReveal = (element: HTMLElement | null, onComplete?: () => void) => {
  if (!element) return;
  safeAnimate(element, {
    opacity: [0, 1],
    translateY: [10, 0],
    duration: MOTION_TIMINGS.section,
    ease: MOTION_EASINGS.outQuad,
    onComplete,
  });
};

/**
 * Scroll reveal for landing page sections with distinct scroll up vs scroll down animations.
 */
export const animateDirectionalScrollReveal = (
  element: HTMLElement | null,
  direction: "down" | "up" = "down",
  childSelector = ".landing-reveal-item",
  staggerTime = 40
) => {
  if (!element || prefersReducedMotion()) {
    if (element) {
      element.style.opacity = "1";
      element.style.transform = "none";
    }
    return;
  }

  const isDown = direction === "down";
  const parentY = isDown ? [24, 0] : [-24, 0];
  const childY = isDown ? [16, 0] : [-16, 0];

  // Animate main container with directional translation
  safeAnimate(element, {
    opacity: [0, 1],
    translateY: parentY,
    duration: 420,
    ease: MOTION_EASINGS.outCubic,
  });

  // Stagger child elements if present with matching directional flow
  const children = Array.from(element.querySelectorAll(childSelector));
  if (children.length > 0) {
    safeAnimate(children, {
      opacity: [0, 1],
      translateY: childY,
      delay: stagger(staggerTime, { start: 40 }),
      duration: 360,
      ease: MOTION_EASINGS.outQuad,
    });
  }
};

/**
 * Backward compatible scroll reveal alias defaulting to downward entry.
 */
export const animateScrollReveal = (
  element: HTMLElement | null,
  childSelector = ".landing-reveal-item",
  staggerTime = 40
) => {
  animateDirectionalScrollReveal(element, "down", childSelector, staggerTime);
};

/**
 * Staggered entrance for lists, cards, or metric tiles.
 */
export const animateStaggerChildren = (
  parent: HTMLElement | null,
  selector?: string,
  staggerTime = MOTION_TIMINGS.staggerStep
) => {
  if (!parent || prefersReducedMotion()) return;
  let items: Element[] = [];
  try {
    if (!selector || selector === "> *" || selector === ":scope > *") {
      items = Array.from(parent.children);
    } else {
      items = Array.from(parent.querySelectorAll(selector));
    }
  } catch {
    items = Array.from(parent.children);
  }
  if (items.length === 0) return;

  safeAnimate(items, {
    opacity: [0, 1],
    translateY: [6, 0],
    delay: stagger(staggerTime),
    duration: MOTION_TIMINGS.fast,
    ease: MOTION_EASINGS.outQuad,
  });
};

/**
 * Project and Risk Inspection Drawer entrance motion.
 */
export const animateDrawerEnter = (
  overlay: HTMLElement | null,
  drawer: HTMLElement | null,
  onComplete?: () => void
) => {
  if (prefersReducedMotion()) {
    if (overlay) overlay.style.opacity = "1";
    if (drawer) drawer.style.transform = "translateX(0)";
    if (onComplete) onComplete();
    return;
  }

  if (overlay) {
    safeAnimate(overlay, {
      opacity: [0, 1],
      duration: MOTION_TIMINGS.drawer * 0.85,
      ease: MOTION_EASINGS.outQuad,
    });
  }

  if (drawer) {
    safeAnimate(drawer, {
      translateX: ["100%", "0%"],
      duration: MOTION_TIMINGS.drawer,
      ease: MOTION_EASINGS.outCubic,
      onComplete,
    });
  }
};

/**
 * Project and Risk Inspection Drawer exit motion.
 */
export const animateDrawerExit = (
  overlay: HTMLElement | null,
  drawer: HTMLElement | null,
  onComplete?: () => void
) => {
  if (prefersReducedMotion()) {
    if (onComplete) onComplete();
    return;
  }

  let completedCount = 0;
  const checkComplete = () => {
    completedCount++;
    if (completedCount >= 2 && onComplete) {
      onComplete();
    }
  };

  if (drawer) {
    safeAnimate(drawer, {
      translateX: ["0%", "100%"],
      duration: 260,
      ease: MOTION_EASINGS.inQuad,
      onComplete: checkComplete,
    });
  } else {
    completedCount++;
  }

  if (overlay) {
    safeAnimate(overlay, {
      opacity: [1, 0],
      duration: 220,
      ease: MOTION_EASINGS.inQuad,
      onComplete: checkComplete,
    });
  } else {
    completedCount++;
  }
};

/**
 * Presentation-only numeric count interpolation for hero KPIs.
 * Interpolates directly to the target backend number without altering application state.
 */
export const animateNumericCount = (
  target: HTMLElement | null,
  endValue: number,
  formatter?: (val: number) => string
) => {
  if (!target || prefersReducedMotion()) {
    if (target) {
      target.textContent = formatter ? formatter(endValue) : endValue.toLocaleString();
    }
    return;
  }

  const obj = { val: 0 };
  safeAnimate(obj, {
    val: endValue,
    duration: 650,
    ease: MOTION_EASINGS.outCubic,
    onUpdate: () => {
      if (target) {
        const current = Math.round(obj.val);
        target.textContent = formatter ? formatter(current) : current.toLocaleString();
      }
    },
    onComplete: () => {
      if (target) {
        target.textContent = formatter ? formatter(endValue) : endValue.toLocaleString();
      }
    },
  });
};
