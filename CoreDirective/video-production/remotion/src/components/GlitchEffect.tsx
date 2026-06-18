/**
 * GlitchEffect.tsx
 * RGB channel shift (chromatic aberration) effect.
 * Wraps children and applies offset RGB layers during active frames.
 *
 * Props:
 *   intensity   - Maximum pixel offset for RGB shift (default 8)
 *   startFrame  - Frame to start the glitch (default 0)
 *   duration    - Duration in frames (default 6, ~0.2s at 30fps)
 *   children    - Content to apply the glitch to
 */

import React from "react";
import { useCurrentFrame, interpolate, AbsoluteFill } from "remotion";

interface GlitchEffectProps {
  intensity?: number;
  startFrame?: number;
  duration?: number;
  children: React.ReactNode;
}

export const GlitchEffect: React.FC<GlitchEffectProps> = ({
  intensity = 8,
  startFrame = 0,
  duration = 6,
  children,
}) => {
  const frame = useCurrentFrame();

  // Is the glitch currently active?
  const isActive = frame >= startFrame && frame < startFrame + duration;

  if (!isActive) {
    return <AbsoluteFill>{children}</AbsoluteFill>;
  }

  // Progress through the glitch (0 to 1)
  const progress = (frame - startFrame) / duration;

  // Intensity ramps up then down (peaks at middle of duration)
  const currentIntensity = interpolate(
    progress,
    [0, 0.3, 0.7, 1],
    [0, intensity, intensity, 0]
  );

  // Pseudo-random offsets per frame for jittery feel
  const seed = frame * 1337;
  const redX = Math.sin(seed) * currentIntensity;
  const redY = Math.cos(seed * 1.3) * currentIntensity * 0.5;
  const blueX = Math.sin(seed * 2.1) * currentIntensity * -1;
  const blueY = Math.cos(seed * 0.7) * currentIntensity * 0.3;

  // Horizontal slice displacement for scan-line glitch
  const sliceOffset = Math.sin(seed * 3.7) * currentIntensity * 2;
  const sliceTop = 30 + Math.sin(seed * 5.1) * 20; // % from top

  return (
    <AbsoluteFill>
      {/* Red channel layer */}
      <AbsoluteFill
        style={{
          transform: `translate(${redX}px, ${redY}px)`,
          mixBlendMode: "screen",
          opacity: 0.8,
          filter: "saturate(0) brightness(1.2)",
        }}
      >
        <AbsoluteFill
          style={{
            background: "rgba(255, 0, 0, 0.15)",
          }}
        />
        {children}
      </AbsoluteFill>

      {/* Blue channel layer */}
      <AbsoluteFill
        style={{
          transform: `translate(${blueX}px, ${blueY}px)`,
          mixBlendMode: "screen",
          opacity: 0.8,
          filter: "saturate(0) brightness(1.2)",
        }}
      >
        <AbsoluteFill
          style={{
            background: "rgba(0, 0, 255, 0.15)",
          }}
        />
        {children}
      </AbsoluteFill>

      {/* Main content layer */}
      <AbsoluteFill>{children}</AbsoluteFill>

      {/* Horizontal slice displacement overlay */}
      <AbsoluteFill
        style={{
          clipPath: `inset(${sliceTop}% 0 ${100 - sliceTop - 5}% 0)`,
          transform: `translateX(${sliceOffset}px)`,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
