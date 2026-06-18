/**
 * MatrixRain.tsx
 * Canvas-based falling green characters effect.
 * Renders columns of random characters that fall down the screen,
 * creating the iconic "Matrix" digital rain look.
 *
 * Props:
 *   opacity - overall opacity of the effect (0-1), default 0.15
 *   color   - character color, default "#00FF41"
 *   speed   - fall speed multiplier, default 1
 */

import React, { useEffect, useRef } from "react";
import { useCurrentFrame, useVideoConfig, AbsoluteFill } from "remotion";
import { COLORS } from "../data/brand";

interface MatrixRainProps {
  opacity?: number;
  color?: string;
  speed?: number;
}

export const MatrixRain: React.FC<MatrixRainProps> = ({
  opacity = 0.15,
  color = COLORS.accent,
  speed = 1,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Characters used in the rain
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:',.<>?/~`";

  // Seeded pseudo-random for deterministic rendering across frames
  const seededRandom = (seed: number): number => {
    const x = Math.sin(seed * 9301 + 49297) * 49297;
    return x - Math.floor(x);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = width;
    canvas.height = height;

    const fontSize = 14;
    const columns = Math.floor(width / fontSize);

    // Clear canvas
    ctx.fillStyle = "rgba(0, 0, 0, 0)";
    ctx.clearRect(0, 0, width, height);

    // Draw characters for each column
    for (let col = 0; col < columns; col++) {
      // Each column has its own speed offset so they don't all sync up
      const columnSpeed = 0.5 + seededRandom(col * 7) * 1.5;
      const columnOffset = seededRandom(col * 13) * height;

      // Number of characters in this column
      const numChars = Math.floor(height / fontSize) + 5;

      for (let row = 0; row < numChars; row++) {
        // Calculate y position: falls over time
        const baseY = row * fontSize + columnOffset;
        const y =
          (baseY + frame * speed * columnSpeed * 2) % (height + fontSize * 5);

        // Character selection changes over time for flicker effect
        const charIndex = Math.floor(
          seededRandom(col * 100 + row * 7 + Math.floor(frame / 3)) *
            chars.length
        );
        const char = chars[charIndex];

        // Fade: brighter at the bottom of each column's "trail"
        const trailLength = 15;
        const trailPos = row % trailLength;
        const trailOpacity = trailPos === 0 ? 1.0 : 0.1 + (trailPos / trailLength) * 0.4;

        ctx.fillStyle = color;
        ctx.globalAlpha = trailOpacity * opacity;
        ctx.font = `${fontSize}px "JetBrains Mono", "Courier New", monospace`;
        ctx.fillText(char, col * fontSize, y);
      }
    }

    ctx.globalAlpha = 1;
  }, [frame, width, height, color, opacity, speed, chars]);

  return (
    <AbsoluteFill>
      <canvas
        ref={canvasRef}
        style={{
          width: "100%",
          height: "100%",
          position: "absolute",
          top: 0,
          left: 0,
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
