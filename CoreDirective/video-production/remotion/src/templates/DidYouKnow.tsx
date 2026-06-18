/**
 * DidYouKnow.tsx - Fact/stat card template (4 seconds, 1080x1920 vertical)
 *
 * Animation timeline:
 *   0-0.3s   (0-9f):    Glitch -> category pill appears
 *   0.3-0.8s (9-24f):   "DID YOU KNOW?" types large with cursor blink
 *   0.8-2.8s (24-84f):  Fact text word-by-word fade in, max 3 lines
 *   2.8-3.5s (84-105f): Source fades in smaller, dimmer
 *   3.5-4s   (105-120f): CTA slides up from bottom
 *
 * Category colors: THREAT INTEL=red, CAREER=green, SALARY=gold, HACK=purple
 * Subtle scanline CRT effect, dark bg with animated mesh gradient.
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { GlitchEffect } from "../components/GlitchEffect";
import { Scanlines } from "../components/Scanlines";
import { TerminalText } from "../components/TerminalText";
import { COLORS, FONTS, CATEGORY_COLORS } from "../data/brand";
import { DidYouKnowProps } from "../data/schemas";

export const DidYouKnow: React.FC<DidYouKnowProps> = ({
  category,
  fact,
  source,
  callToAction,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Get category color (fallback to accent green)
  const categoryColor = CATEGORY_COLORS[category] || COLORS.accent;

  // ---- Phase 1: Category pill with glitch (frames 0-9) ----
  const pillScale = spring({
    frame,
    fps,
    config: { damping: 10, stiffness: 200, mass: 0.4 },
    from: 0,
    to: 1,
  });

  const pillOpacity = interpolate(frame, [0, 4], [0, 1], {
    extrapolateRight: "clamp",
  });

  // ---- Phase 2: "DID YOU KNOW?" heading (frames 9-24) ----
  // (TerminalText handles its own character-by-character animation)

  const headingOpacity = interpolate(frame, [9, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 3: Fact text word-by-word (frames 24-84) ----
  const words = fact.split(" ");
  const wordDuration = Math.min(2.5, 60 / words.length); // frames per word, fit in 60 frames

  const wordAnimations = words.map((_, i) => {
    const wordStart = 24 + i * wordDuration;
    const opacity = interpolate(
      frame,
      [wordStart, wordStart + wordDuration * 0.8],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    return { opacity };
  });

  // ---- Phase 4: Source (frames 84-105) ----
  const sourceOpacity = interpolate(frame, [84, 94], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 5: CTA slides up (frames 105-120) ----
  const ctaSlideY = spring({
    frame: frame - 105,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.6 },
    from: 60,
    to: 0,
  });

  const ctaOpacity = interpolate(frame, [105, 115], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Background animated mesh gradient (slow hue rotation)
  const gradientAngle = interpolate(frame, [0, 120], [0, 30], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary }}>
      {/* Animated mesh gradient background */}
      <AbsoluteFill
        style={{
          background: `
            radial-gradient(ellipse at 20% 20%, ${categoryColor}08 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, ${categoryColor}06 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(10,10,10,0.95) 0%, ${COLORS.primary} 100%)
          `,
          transform: `rotate(${gradientAngle}deg) scale(1.2)`,
        }}
      />

      {/* Glitch wrapper for the initial entrance */}
      <GlitchEffect startFrame={0} duration={8} intensity={12}>
        <AbsoluteFill
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            padding: 60,
            gap: 48,
          }}
        >
          {/* Phase 1: Category pill */}
          <div
            style={{
              opacity: pillOpacity,
              transform: `scale(${pillScale})`,
            }}
          >
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 26,
                fontWeight: 700,
                color: category === "CAREER" ? COLORS.primary : COLORS.text,
                backgroundColor: categoryColor,
                padding: "12px 32px",
                borderRadius: 8,
                letterSpacing: 4,
                textTransform: "uppercase",
                boxShadow: `0 0 20px ${categoryColor}44`,
              }}
            >
              {category}
            </div>
          </div>

          {/* Phase 2: "DID YOU KNOW?" heading */}
          <div style={{ opacity: headingOpacity }}>
            <TerminalText
              text="DID YOU KNOW?"
              startFrame={9}
              speed={2}
              fontSize={64}
              color={COLORS.text}
              cursorColor={categoryColor}
              style={{
                textAlign: "center",
                fontWeight: 700,
              }}
            />
          </div>

          {/* Phase 3: Fact text (word-by-word) */}
          <div
            style={{
              textAlign: "center",
              maxWidth: 900,
              lineHeight: 1.5,
            }}
          >
            {words.map((word, i) => (
              <span
                key={i}
                style={{
                  fontFamily: FONTS.body,
                  fontSize: 48,
                  color: COLORS.text,
                  opacity: wordAnimations[i].opacity,
                  display: "inline",
                }}
              >
                {word}{" "}
              </span>
            ))}
          </div>

          {/* Phase 4: Source */}
          {source && (
            <div
              style={{
                opacity: sourceOpacity,
                fontFamily: FONTS.mono,
                fontSize: 24,
                color: COLORS.textDim,
                textAlign: "center",
              }}
            >
              -- {source}
            </div>
          )}

          {/* Phase 5: CTA */}
          <div
            style={{
              opacity: ctaOpacity,
              transform: `translateY(${ctaSlideY}px)`,
              fontFamily: FONTS.body,
              fontSize: 32,
              color: categoryColor,
              textAlign: "center",
              fontWeight: 600,
              letterSpacing: 2,
              textShadow: `0 0 10px ${categoryColor}44`,
            }}
          >
            {callToAction}
          </div>
        </AbsoluteFill>
      </GlitchEffect>

      {/* CRT scanlines overlay */}
      <Scanlines opacity={0.06} />
    </AbsoluteFill>
  );
};
