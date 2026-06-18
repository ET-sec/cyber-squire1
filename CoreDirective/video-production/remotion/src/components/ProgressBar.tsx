/**
 * ProgressBar.tsx
 * Animated horizontal bar that fills to a target percentage.
 * Uses spring() for smooth, natural fill animation.
 *
 * Props:
 *   progress    - Target fill percentage (0-100)
 *   startFrame  - Frame to begin the fill animation
 *   label       - Optional label text shown above the bar
 *   height      - Bar height in px (default 32)
 *   color       - Fill color (default accent green)
 *   bgColor     - Background bar color (default dark)
 *   showPercent - Whether to show percentage label (default true)
 *   style       - Additional container styles
 */

import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { COLORS, FONTS } from "../data/brand";

interface ProgressBarProps {
  progress: number;
  startFrame?: number;
  label?: string;
  height?: number;
  color?: string;
  bgColor?: string;
  showPercent?: boolean;
  style?: React.CSSProperties;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  startFrame = 0,
  label,
  height = 32,
  color = COLORS.accent,
  bgColor = "rgba(255, 255, 255, 0.1)",
  showPercent = true,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring animation for smooth fill
  const fillProgress = spring({
    frame: frame - startFrame,
    fps,
    config: {
      damping: 20,
      stiffness: 80,
      mass: 1,
    },
    from: 0,
    to: progress,
  });

  // Clamp to valid range
  const clampedProgress = Math.max(0, Math.min(100, fillProgress));

  // Glow intensity based on progress
  const glowIntensity = interpolate(clampedProgress, [0, 100], [0, 0.8]);

  return (
    <div style={{ width: "100%", ...style }}>
      {/* Optional label */}
      {label && (
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 20,
            color: COLORS.textDim,
            marginBottom: 8,
          }}
        >
          {label}
        </div>
      )}

      {/* Bar container */}
      <div
        style={{
          width: "100%",
          height,
          borderRadius: height / 2,
          backgroundColor: bgColor,
          overflow: "hidden",
          position: "relative",
          border: `1px solid rgba(0, 255, 65, 0.2)`,
        }}
      >
        {/* Fill bar */}
        <div
          style={{
            width: `${clampedProgress}%`,
            height: "100%",
            borderRadius: height / 2,
            background: `linear-gradient(90deg, ${color}, ${color}88)`,
            boxShadow: `0 0 ${20 * glowIntensity}px ${color}66, inset 0 0 10px rgba(255,255,255,0.1)`,
            transition: "none",
            position: "relative",
          }}
        >
          {/* Shimmer effect on the fill */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "50%",
              borderRadius: `${height / 2}px ${height / 2}px 0 0`,
              background:
                "linear-gradient(180deg, rgba(255,255,255,0.2), transparent)",
            }}
          />
        </div>
      </div>

      {/* Percentage label */}
      {showPercent && (
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 24,
            color: COLORS.text,
            marginTop: 8,
            textAlign: "right",
          }}
        >
          {Math.round(clampedProgress)}%
        </div>
      )}
    </div>
  );
};
