/**
 * YouTubeIntro.tsx - YouTube intro template (5 seconds, 1920x1080 LANDSCAPE)
 *
 * Animation timeline:
 *   0-0.5s   (0-15f):   Black -> green cursor blinks twice
 *   0.5-1.5s (15-45f):  "COREDIRECTIVE_" types in terminal style, large, center
 *   1.5-2.5s (45-75f):  Tagline fades in below, wide letter-spacing
 *   2.5-3.5s (75-105f): Episode title slides in from bottom (if provided)
 *   3.5-4.5s (105-135f): Glitch/chromatic aberration effect (0.2s burst)
 *   4.5-5s   (135-150f): Settles, slight zoom in
 *
 * Background: very dark with subtle circuit board pattern (SVG)
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
import { COLORS, FONTS } from "../data/brand";
import { YouTubeIntroProps } from "../data/schemas";

export const YouTubeIntro: React.FC<YouTubeIntroProps> = ({
  channelName,
  tagline,
  episodeTitle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ---- Phase 1: Cursor blinks (frames 0-15) ----
  // Cursor blinks twice: on at 0, off at 4, on at 8, off at 12, then stays on
  const cursorPhase1Visible =
    frame < 15 && (frame < 4 || (frame >= 8 && frame < 12));

  // ---- Phase 2: Channel name types in (frames 15-45) ----
  const nameText = channelName;
  const charsPerFrame = 1.2;
  const nameElapsed = Math.max(0, frame - 15);
  const nameCharsVisible = Math.min(
    Math.floor(nameElapsed * charsPerFrame),
    nameText.length
  );
  const nameVisibleText = nameText.slice(0, nameCharsVisible);
  const nameIsTyping = nameCharsVisible < nameText.length;

  // Cursor during typing: always visible when typing, blinks when done
  const namePostTypingFrame = 15 + Math.ceil(nameText.length / charsPerFrame);
  const cursorPhase2Visible =
    frame >= 15 &&
    (nameIsTyping || Math.floor(frame / 15) % 2 === 0);

  const nameOpacity = interpolate(frame, [14, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 3: Tagline fade in (frames 45-75) ----
  const taglineOpacity = interpolate(frame, [45, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const taglineSpacing = interpolate(frame, [45, 65], [20, 12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 4: Episode title slides up (frames 75-105) ----
  const episodeSlideY = spring({
    frame: frame - 75,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.7 },
    from: 80,
    to: 0,
  });

  const episodeOpacity = interpolate(frame, [75, 88], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 5: Glitch burst (frames 105-111, ~0.2s) ----
  // Handled by GlitchEffect wrapper

  // ---- Phase 6: Settle + slight zoom (frames 135-150) ----
  const settleZoom = interpolate(frame, [135, 150], [1, 1.03], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Circuit board SVG pattern for background
  const circuitPattern = `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%2300FF41' stroke-width='0.5' opacity='0.06'%3E%3Cpath d='M30 0v15M30 45v15M0 30h15M45 30h60'/%3E%3Ccircle cx='30' cy='30' r='3'/%3E%3Ccircle cx='30' cy='15' r='1.5'/%3E%3Ccircle cx='30' cy='45' r='1.5'/%3E%3Ccircle cx='15' cy='30' r='1.5'/%3E%3Ccircle cx='45' cy='30' r='1.5'/%3E%3Cpath d='M15 15h30v30H15z'/%3E%3C/g%3E%3C/svg%3E")`;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary }}>
      {/* Circuit board pattern background */}
      <AbsoluteFill
        style={{
          backgroundImage: circuitPattern,
          backgroundRepeat: "repeat",
          opacity: 0.4,
        }}
      />

      {/* Very subtle radial gradient overlay */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, transparent 30%, ${COLORS.primary} 80%)`,
        }}
      />

      {/* Glitch effect wraps the main content for the burst at 105-111 */}
      <GlitchEffect startFrame={105} duration={6} intensity={15}>
        <AbsoluteFill
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            transform: `scale(${settleZoom})`,
          }}
        >
          {/* Phase 1: Standalone cursor before typing */}
          {frame < 15 && (
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 80,
                color: COLORS.accent,
                opacity: cursorPhase1Visible ? 1 : 0,
                fontWeight: 700,
              }}
            >
              _
            </div>
          )}

          {/* Phase 2: Channel name typing */}
          {frame >= 15 && (
            <div
              style={{
                opacity: nameOpacity,
                fontFamily: FONTS.mono,
                fontSize: 80,
                fontWeight: 700,
                color: COLORS.accent,
                textShadow: `0 0 20px ${COLORS.accent}66, 0 0 40px ${COLORS.accent}33`,
                textAlign: "center",
                lineHeight: 1.2,
              }}
            >
              {nameVisibleText}
              <span
                style={{
                  opacity: cursorPhase2Visible ? 1 : 0,
                  marginLeft: 2,
                }}
              >
                _
              </span>
            </div>
          )}

          {/* Phase 3: Tagline */}
          <div
            style={{
              opacity: taglineOpacity,
              fontFamily: FONTS.body,
              fontSize: 28,
              color: COLORS.textDim,
              letterSpacing: taglineSpacing,
              textTransform: "uppercase",
              marginTop: 24,
              textAlign: "center",
            }}
          >
            {tagline}
          </div>

          {/* Phase 4: Episode title (optional) */}
          {episodeTitle && (
            <div
              style={{
                opacity: episodeOpacity,
                transform: `translateY(${episodeSlideY}px)`,
                fontFamily: FONTS.body,
                fontSize: 36,
                color: COLORS.text,
                marginTop: 48,
                textAlign: "center",
                fontWeight: 600,
                padding: "16px 40px",
                border: `1px solid ${COLORS.accent}33`,
                borderRadius: 8,
                backgroundColor: "rgba(0, 255, 65, 0.05)",
              }}
            >
              {episodeTitle}
            </div>
          )}
        </AbsoluteFill>
      </GlitchEffect>
    </AbsoluteFill>
  );
};
