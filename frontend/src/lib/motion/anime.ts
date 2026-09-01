import { animate, createTimeline, stagger } from "animejs";

/**
 * Checks if the client has requested reduced motion.
 */
export const prefersReducedMotion = (): boolean => {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
};

/**
 * Common Institutional Motion Constants
 * Precise, restrained, fast, industrial timing.
 */
export const MOTION_TIMINGS = {
  instant: 0,
  micro: 120,
  fast: 220,
  base: 350,
  drawer: 400,
  section: 420,
  staggerStep: 30,
} as const;

export const MOTION_EASINGS = {
  outQuad: "outQuad",
  outCubic: "outCubic",
  inQuad: "inQuad",
  inCubic: "inCubic",
  inOutQuad: "inOutQuad",
  inOutCubic: "inOutCubic",
} as const;

export type SafeAnimateTarget =
  | Element
  | Element[]
  | NodeListOf<Element>
  | HTMLCollection
  | string
  | object
  | null
  | undefined;

export interface SafeAnimateOptions {
  duration?: number;
  ease?: string;
  delay?: unknown;
  onComplete?: () => void;
  onUpdate?: () => void;
  [key: string]: unknown;
}

/**
 * Safe wrapper around Anime.js `animate` that respects `prefers-reduced-motion`
 * and handles React component lifecycle cleanup cleanly.
 */
export const safeAnimate = (
  targets: SafeAnimateTarget,
  params: SafeAnimateOptions
) => {
  if (!targets) {
    if (params.onComplete) params.onComplete();
    return { revert: () => {}, pause: () => {} };
  }

  // If reduced motion is requested, instantly apply final properties and trigger onComplete
  if (prefersReducedMotion()) {
    try {
      if (typeof targets === "object" && targets !== null && !("nodeType" in targets) && !Array.isArray(targets) && !(targets instanceof NodeList) && !(targets instanceof HTMLCollection)) {
        // Plain JS object
        const obj = targets as Record<string, unknown>;
        Object.keys(params).forEach((k) => {
          if (k in obj && typeof params[k] === "number") {
            obj[k] = params[k];
          }
        });
      } else {
        const elements: Element[] =
          typeof targets === "string"
            ? Array.from(document.querySelectorAll(targets))
            : Array.isArray(targets)
            ? (targets as Element[])
            : targets instanceof NodeList || targets instanceof HTMLCollection
            ? Array.from(targets as NodeListOf<Element>)
            : [targets as Element];

        elements.forEach((el) => {
          if (el instanceof HTMLElement) {
            if (params.opacity !== undefined) {
              const op = Array.isArray(params.opacity) ? params.opacity[params.opacity.length - 1] : params.opacity;
              el.style.opacity = String(op);
            }
            if (params.translateY !== undefined || params.translateX !== undefined) {
              el.style.transform = "none";
            }
          }
        });
      }
    } catch {
      // Ignore fallback styling errors
    }

    if (params.onComplete) params.onComplete();
    return { revert: () => {}, pause: () => {} };
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return animate(targets as any, {
      ...params,
      onComplete: () => {
        if (params.onComplete) params.onComplete();
      },
      onUpdate: () => {
        if (params.onUpdate) params.onUpdate();
      },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);
  } catch {
    if (params.onComplete) params.onComplete();
    return { revert: () => {}, pause: () => {} };
  }
};

export { animate, createTimeline, stagger };
