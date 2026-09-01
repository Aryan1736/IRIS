import { useEffect, useRef } from "react";
import {
  animatePageEnter,
  animateSectionReveal,
  animateScrollReveal,
  animateDirectionalScrollReveal,
  animateStaggerChildren,
  animateDrawerEnter,
  animateDrawerExit,
  animateNumericCount,
} from "./presets.ts";
import { prefersReducedMotion } from "./anime.ts";

/**
 * Hook to trigger a subtle page entrance animation on initial mount.
 */
export function usePageEnter<T extends HTMLElement = HTMLDivElement>() {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (ref.current) {
      animatePageEnter(ref.current);
    }
  }, []);

  return ref;
}

/**
 * Hook to reveal an analytical section once as it scrolls into the viewport.
 */
export function useSectionReveal<T extends HTMLElement = HTMLElement>(threshold = 0.1) {
  const ref = useRef<T>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || prefersReducedMotion()) return;

    if (typeof IntersectionObserver === "undefined") {
      el.style.opacity = "1";
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated.current) {
            hasAnimated.current = true;
            animateSectionReveal(el);
            observer.unobserve(el);
          }
        });
      },
      { threshold }
    );

    observer.observe(el);

    return () => {
      observer.disconnect();
    };
  }, [threshold]);

  return ref;
}

interface ScrollRevealOptions {
  threshold?: number;
  rootMargin?: string;
  childSelector?: string;
  staggerTime?: number;
  allowReentry?: boolean;
}

/**
 * Hook to reveal a landing page section with distinct animations when scrolling DOWN vs UP.
 */
export function useScrollReveal<T extends HTMLElement = HTMLElement>({
  threshold = 0.08,
  rootMargin = "0px 0px -40px 0px",
  childSelector = ".landing-reveal-item",
  staggerTime = 40,
  allowReentry = true,
}: ScrollRevealOptions = {}) {
  const ref = useRef<T>(null);
  const lastScrollY = useRef<number>(typeof window !== "undefined" ? window.scrollY : 0);

  useEffect(() => {
    const el = ref.current;
    if (!el || prefersReducedMotion()) return;

    if (typeof IntersectionObserver === "undefined") {
      el.style.opacity = "1";
      return;
    }

    const onScroll = () => {
      lastScrollY.current = window.scrollY;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    let previousY = typeof window !== "undefined" ? window.scrollY : 0;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const currentY = typeof window !== "undefined" ? window.scrollY : 0;
            // Direction: down if user moved forward/down or initial load; up if user scrolled upward
            const direction: "down" | "up" = currentY >= previousY ? "down" : "up";
            previousY = currentY;

            animateDirectionalScrollReveal(el, direction, childSelector, staggerTime);

            if (!allowReentry) {
              observer.unobserve(el);
            }
          } else {
            previousY = typeof window !== "undefined" ? window.scrollY : 0;
          }
        });
      },
      { threshold, rootMargin }
    );

    observer.observe(el);

    return () => {
      window.removeEventListener("scroll", onScroll);
      observer.disconnect();
    };
  }, [threshold, rootMargin, childSelector, staggerTime, allowReentry]);

  return ref;
}

/**
 * Hook to animate children items when a list or table finishes loading.
 */
export function useStaggerList<T extends HTMLElement = HTMLDivElement>(
  dependency: unknown,
  selector = "> *"
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (ref.current && dependency) {
      animateStaggerChildren(ref.current, selector);
    }
  }, [dependency, selector]);

  return ref;
}

export {
  animatePageEnter,
  animateSectionReveal,
  animateScrollReveal,
  animateDirectionalScrollReveal,
  animateStaggerChildren,
  animateDrawerEnter,
  animateDrawerExit,
  animateNumericCount,
  prefersReducedMotion,
};
