import React, { useEffect, useState, useMemo } from "react";
import { prefersReducedMotion } from "@/lib/motion/anime.ts";

interface TypingHeadlineProps {
  lines: string[];
  speedMs?: number;
  initialDelayMs?: number;
  onComplete?: () => void;
}

export const TypingHeadline: React.FC<TypingHeadlineProps> = ({
  lines,
  speedMs = 50,
  initialDelayMs = 80,
  onComplete,
}) => {
  const fullText = useMemo(() => lines.join("\n"), [lines]);
  const isReduced = prefersReducedMotion();

  const [visibleChars, setVisibleChars] = useState<number>(() =>
    isReduced ? fullText.length : 0
  );

  useEffect(() => {
    if (isReduced) {
      setVisibleChars(fullText.length);
      if (onComplete) onComplete();
      return;
    }

    let intervalId: NodeJS.Timeout | null = null;
    const delayTimeout = setTimeout(() => {
      let count = 0;
      intervalId = setInterval(() => {
        count += 1;
        setVisibleChars(count);
        if (count >= fullText.length) {
          if (intervalId) clearInterval(intervalId);
          if (onComplete) onComplete();
        }
      }, speedMs);
    }, initialDelayMs);

    return () => {
      clearTimeout(delayTimeout);
      if (intervalId) clearInterval(intervalId);
    };
  }, [fullText, speedMs, initialDelayMs, isReduced, onComplete]);

  // Current slice of full text
  const currentText = fullText.slice(0, visibleChars);
  const currentLines = currentText.split("\n");

  return (
    <span
      className="iris-typing-headline"
      aria-label={lines.join(" ")}
      role="text"
    >
      {/* Screen-reader accessible complete headline */}
      <span className="sr-only">{lines.join(" ")}</span>

      {/* Visual character-by-character typing representation */}
      <span className="iris-typing-text" aria-hidden="true">
        {currentLines.map((line, idx) => (
          <React.Fragment key={idx}>
            {idx > 0 && <br />}
            {line}
          </React.Fragment>
        ))}
      </span>
      <span className="iris-typing-cursor" aria-hidden="true" />
    </span>
  );
};
