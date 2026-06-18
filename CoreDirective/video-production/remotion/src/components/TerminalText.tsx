/**
 * TerminalText.tsx
 * Types text character by character with a blinking cursor.
 * Uses Remotion's interpolate() for smooth frame-based animation.
 *
 * Props:
 *   text        - The string to type out
 *   startFrame  - Frame to begin typing (default 0)
 *   speed       - Characters per frame (default 1.5)
 *   fontSize    - Font size in px (default 48)
 *   color       - Text color (default white)
 *   cursorColor - Cursor color (default accent green)
 *   showCursor  - Whether to show the blinking cursor (default true)
 *   style       - Additional CSS styles for the container
 */

import React from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { COLORS, FONTS } from "../data/brand";

interface TerminalTextProps {
  text: string;
  startFrame?: number;
  speed?: number;
  fontSize?: number;
  color?: string;
  cursorColor?: string;
  showCursor?: boolean;
  style?: React.CSSProperties;
}

export const TerminalText: React.FC<TerminalTextProps> = ({
  text,
  startFrame = 0,
  speed = 1.5,
  fontSize = 48,
  color = COLORS.text,
  cursorColor = COLORS.accent,
  showCursor = true,
  style = {},
}) => {
  const frame = useCurrentFrame();

  // Calculate how many characters should be visible at the current frame
  const elapsed = Math.max(0, frame - startFrame);
  const charsToShow = Math.min(Math.floor(elapsed * speed), text.length);

  // The visible portion of the text
  const visibleText = text.slice(0, charsToShow);

  // Cursor blinks every 15 frames (0.5s at 30fps)
  const cursorVisible = Math.floor(frame / 15) % 2 === 0;

  // Cursor opacity: fully visible while typing, blinks after done
  const isTyping = charsToShow < text.length;
  const cursorOpacity = isTyping ? 1 : cursorVisible ? 1 : 0;

  return (
    <div
      style={{
        fontFamily: FONTS.mono,
        fontSize,
        color,
        whiteSpace: "pre-wrap",
        lineHeight: 1.4,
        ...style,
      }}
    >
      {visibleText}
      {showCursor && (
        <span
          style={{
            color: cursorColor,
            opacity: cursorOpacity,
            fontWeight: "bold",
            marginLeft: 2,
          }}
        >
          _
        </span>
      )}
    </div>
  );
};
