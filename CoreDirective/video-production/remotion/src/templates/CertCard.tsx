/**
 * CertCard.tsx - Certification showcase template (5 seconds, 1080x1920 vertical)
 *
 * Animation timeline:
 *   0-0.5s   (0-15f):   Black -> terminal text types "> LOADING CERT: {certName}_"
 *   0.5-1.5s (15-45f):  Card slides up from bottom with green border glow
 *   1.5-3.5s (45-105f): Factoids animate in one by one (fade + slide right)
 *   3.5-4.5s (105-135f): Salary impact slams in with pulse, red accent
 *   4.5-5s   (135-150f): "Follow for more" fades in
 *   Background: subtle matrix rain (low opacity)
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import { MatrixRain } from "../components/MatrixRain";
import { TerminalText } from "../components/TerminalText";
import { COLORS, FONTS } from "../data/brand";
import { CertCardProps } from "../data/schemas";

export const CertCard: React.FC<CertCardProps> = ({
  certName,
  certFullName,
  issuer,
  passDate,
  difficulty,
  factoids,
  salaryImpact,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ---- Phase 1: Terminal loading text (frames 0-15) ----
  const loadingOpacity = interpolate(frame, [0, 5], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out the loading text as card appears
  const loadingFadeOut = interpolate(frame, [15, 30], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 2: Card slide up (frames 15-45) ----
  const cardSlide = spring({
    frame: frame - 15,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.8 },
    from: 600,
    to: 0,
  });

  const cardOpacity = interpolate(frame, [15, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Card border glow pulses
  const glowIntensity = interpolate(
    Math.sin(frame * 0.1),
    [-1, 1],
    [0.3, 0.7]
  );

  // ---- Phase 3: Factoids animate in (frames 45-105, 21 frames apart ~0.7s) ----
  const factoidAnimations = factoids.map((_, i) => {
    const factStartFrame = 45 + i * 21;

    const slideX = spring({
      frame: frame - factStartFrame,
      fps,
      config: { damping: 15, stiffness: 120, mass: 0.6 },
      from: 80,
      to: 0,
    });

    const opacity = interpolate(
      frame,
      [factStartFrame, factStartFrame + 10],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    return { slideX, opacity };
  });

  // ---- Phase 4: Salary impact slam (frames 105-135) ----
  const salaryScale = spring({
    frame: frame - 105,
    fps,
    config: { damping: 8, stiffness: 200, mass: 0.5 },
    from: 2.0,
    to: 1.0,
  });

  const salaryOpacity = interpolate(frame, [105, 112], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Salary pulse glow
  const salaryGlow = interpolate(
    frame,
    [105, 115, 125, 135],
    [0, 20, 10, 5],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ---- Phase 5: Follow CTA (frames 135-150) ----
  const ctaOpacity = interpolate(frame, [135, 145], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary }}>
      {/* Background: Matrix rain at low opacity */}
      <MatrixRain opacity={0.08} speed={0.7} />

      {/* Phase 1: Terminal loading text */}
      <AbsoluteFill
        style={{
          opacity: loadingOpacity * loadingFadeOut,
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
        }}
      >
        <TerminalText
          text={`> LOADING CERT: ${certName}`}
          startFrame={0}
          speed={2}
          fontSize={42}
          color={COLORS.accent}
        />
      </AbsoluteFill>

      {/* Phase 2-5: Main card */}
      <AbsoluteFill
        style={{
          opacity: cardOpacity,
          transform: `translateY(${cardSlide}px)`,
          justifyContent: "center",
          alignItems: "center",
          padding: 40,
        }}
      >
        {/* Card container */}
        <div
          style={{
            width: "100%",
            maxWidth: 960,
            borderRadius: 24,
            padding: 3,
            // Gradient border: green to transparent
            background: `linear-gradient(135deg, ${COLORS.accent}${Math.round(glowIntensity * 255).toString(16).padStart(2, "0")}, transparent 70%)`,
            boxShadow: `0 0 ${30 * glowIntensity}px ${COLORS.accent}33, 0 20px 60px rgba(0,0,0,0.5)`,
          }}
        >
          <div
            style={{
              backgroundColor: COLORS.cardBg,
              borderRadius: 22,
              padding: 56,
              display: "flex",
              flexDirection: "column",
              gap: 32,
            }}
          >
            {/* Cert name with glow */}
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 72,
                fontWeight: 700,
                color: COLORS.accent,
                textShadow: `0 0 20px ${COLORS.accent}88, 0 0 40px ${COLORS.accent}44`,
                lineHeight: 1.1,
              }}
            >
              {certName}
            </div>

            {/* Full name */}
            <div
              style={{
                fontFamily: FONTS.body,
                fontSize: 36,
                color: COLORS.text,
                opacity: 0.9,
                lineHeight: 1.3,
              }}
            >
              {certFullName}
            </div>

            {/* Issuer + Difficulty row */}
            <div
              style={{
                display: "flex",
                gap: 20,
                flexWrap: "wrap",
              }}
            >
              <div
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 22,
                  color: COLORS.textDim,
                  padding: "8px 16px",
                  border: `1px solid ${COLORS.cardBorder}`,
                  borderRadius: 8,
                }}
              >
                {issuer}
              </div>
              <div
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 22,
                  color: COLORS.accent,
                  padding: "8px 16px",
                  border: `1px solid ${COLORS.cardBorder}`,
                  borderRadius: 8,
                }}
              >
                {difficulty}
              </div>
            </div>

            {/* Divider */}
            <div
              style={{
                height: 1,
                background: `linear-gradient(90deg, ${COLORS.accent}44, transparent)`,
              }}
            />

            {/* Factoids */}
            <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
              {factoids.map((factoid, i) => (
                <div
                  key={i}
                  style={{
                    opacity: factoidAnimations[i].opacity,
                    transform: `translateX(${factoidAnimations[i].slideX}px)`,
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 16,
                  }}
                >
                  {/* Green prefix arrow */}
                  <span
                    style={{
                      fontFamily: FONTS.mono,
                      fontSize: 32,
                      color: COLORS.accent,
                      flexShrink: 0,
                      lineHeight: 1.3,
                    }}
                  >
                    {">"}
                  </span>
                  <span
                    style={{
                      fontFamily: FONTS.body,
                      fontSize: 32,
                      color: COLORS.text,
                      lineHeight: 1.3,
                    }}
                  >
                    {factoid}
                  </span>
                </div>
              ))}
            </div>

            {/* Divider */}
            <div
              style={{
                height: 1,
                background: `linear-gradient(90deg, ${COLORS.secondary}44, transparent)`,
              }}
            />

            {/* Salary impact - slams in */}
            <div
              style={{
                opacity: salaryOpacity,
                transform: `scale(${salaryScale})`,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 52,
                  fontWeight: 700,
                  color: COLORS.secondary,
                  textShadow: `0 0 ${salaryGlow}px ${COLORS.secondary}`,
                  lineHeight: 1.2,
                }}
              >
                {salaryImpact}
              </div>
            </div>
          </div>
        </div>

        {/* Follow CTA */}
        <div
          style={{
            opacity: ctaOpacity,
            marginTop: 40,
            fontFamily: FONTS.body,
            fontSize: 28,
            color: COLORS.textDim,
            textAlign: "center",
            letterSpacing: 4,
            textTransform: "uppercase",
          }}
        >
          Follow for more certs
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
