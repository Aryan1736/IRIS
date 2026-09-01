import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, act } from "@testing-library/react";
import { TypingHeadline } from "@/components/landing/TypingHeadline.tsx";

describe("TypingHeadline Component", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders with typing cursor attached", () => {
    const { container } = render(
      <TypingHeadline lines={["FROM", "INFRASTRUCTURE"]} speedMs={50} initialDelayMs={0} />
    );

    const cursor = container.querySelector(".iris-typing-cursor");
    expect(cursor).toBeInTheDocument();
    expect(cursor).toHaveAttribute("aria-hidden", "true");
  });

  it("progressively reveals characters every 50ms until complete", () => {
    const onComplete = vi.fn();
    const { container } = render(
      <TypingHeadline
        lines={["FROM", "INTELLIGENCE."]}
        speedMs={50}
        initialDelayMs={50}
        onComplete={onComplete}
      />
    );

    const textSpan = container.querySelector(".iris-typing-text");

    // After initial delay + 4 ticks (4 * 50ms = 200ms)
    act(() => {
      vi.advanceTimersByTime(250);
    });

    expect(textSpan?.textContent).toContain("FROM");
    expect(onComplete).not.toHaveBeenCalled();

    // Advance to full completion
    act(() => {
      vi.advanceTimersByTime(1500);
    });

    expect(textSpan?.textContent).toBe("FROMINTELLIGENCE.");
    expect(onComplete).toHaveBeenCalled();

    // Cursor remains after completion
    const cursor = container.querySelector(".iris-typing-cursor");
    expect(cursor).toBeInTheDocument();
  });

  it("immediately renders complete text when prefers-reduced-motion is true", () => {
    // Mock reduced motion
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === "(prefers-reduced-motion: reduce)",
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const onComplete = vi.fn();
    const { container } = render(
      <TypingHeadline
        lines={["FROM", "INFRASTRUCTURE", "MONITORING", "TO INTELLIGENCE."]}
        speedMs={50}
        onComplete={onComplete}
      />
    );

    const textSpan = container.querySelector(".iris-typing-text");
    expect(textSpan?.textContent).toBe("FROMINFRASTRUCTUREMONITORINGTO INTELLIGENCE.");
    expect(onComplete).toHaveBeenCalled();
  });

  it("cleans up timers on unmount without throwing errors", () => {
    const { unmount } = render(
      <TypingHeadline lines={["TEST", "TYPING"]} speedMs={50} />
    );

    expect(() => {
      unmount();
      act(() => {
        vi.advanceTimersByTime(500);
      });
    }).not.toThrow();
  });
});
