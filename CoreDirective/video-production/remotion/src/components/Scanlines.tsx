/**
 * Scanlines.tsx
 * CRT monitor scanline overlay effect.
 * Renders semi-transparent horizontal lines across the viewport
 * to simulate an old CRT display.
 *
 * Props:
 *   opacity   - Overall opacity of the scanlines (default 0.08)
 *   lineGap   - Pixels between each scanline (default 4)
 *   lineWidth - Height of each scanline in px (default 2)
 *   animate   - Whether scanlines scroll slowly (default true)
 */

import React from "react";
import { useCurrentFrame, AbsoluteFill } from "remotion";

interface ScanlinesProps {
  opacity?: number;
  lineGap?: number;
  lineWidth?: number;
  animate?: boolean;
}

export const Scanlines: React.FC<ScanlinesProps> = ({
  opacity = 0.08,
  lineGap = 4,
  lineWidth = 2,
  animate = true,
}) => {
  const frame = useCurrentFrame();

  // Slow vertical scroll for subtle CRT movement
  const offset = animate ? (frame * 0.5) % (lineGap + lineWidth) : 0;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        zIndex: 999,
        opacity,
        backgroundImage: `repeating-linear-gradient(
          0deg,
          transparent,
          transparent ${lineGap}px,
          rgba(0, 0, 0, 0.8) ${lineGap}px,
          rgba(0, 0, 0, 0.8) ${lineGap + lineWidth}px
        )`,
        backgroundPosition: `0px ${offset}px`,
        // Subtle vignette at edges for CRT curvature feel
        maskImage:
          "radial-gradient(ellipse 85% 85% at 50% 50%, black 60%, transparent 100%)",
        WebkitMaskImage:
          "radial-gradient(ellipse 85% 85% at 50% 50%, black 60%, transparent 100%)",
      }}
    />
  );
};
