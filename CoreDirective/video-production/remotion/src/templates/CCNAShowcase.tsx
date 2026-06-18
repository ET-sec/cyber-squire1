/**
 * CCNAShowcase.tsx - CCNA 200-301 Study System product showcase (35s, 1920x1080)
 *
 * Gold theme product video for Gumroad listing.
 *
 * Animation timeline:
 *   0-4s     (0-120f):    Title reveal: "CCNA" slam, "200-301", "STUDY SYSTEM", "// NOTION TEMPLATE"
 *   4-14s    (120-420f):  Feature counter grid - 9 features count up with staggered entrance
 *   14-22s   (420-660f):  3 key benefit cards slide in sequentially
 *   22-28s   (660-840f):  DoK Framework differentiator reveal
 *   28-35s   (840-1050f): CTA + branding
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from "remotion";
import { MatrixRain } from "../components/MatrixRain";
import { TerminalText } from "../components/TerminalText";
import { FONTS } from "../data/brand";

// Gold theme colors
const GOLD = {
  bg: "#0D1117",
  accent: "#D4A843",
  accentBright: "#F0C94D",
  border: "#1C2333",
  cardBg: "rgba(13, 17, 23, 0.95)",
  text: "#FFFFFF",
  textDim: "rgba(255, 255, 255, 0.55)",
  darkGray: "#484F58",
} as const;

/** Animated number counter */
const CountUp: React.FC<{
  target: number;
  suffix?: string;
  startFrame: number;
  durationFrames?: number;
}> = ({ target, suffix = "", startFrame, durationFrames = 30 }) => {
  const frame = useCurrentFrame();
  const elapsed = Math.max(0, frame - startFrame);
  const progress = Math.min(elapsed / durationFrames, 1);
  // Ease out cubic
  const eased = 1 - Math.pow(1 - progress, 3);
  const current = Math.round(target * eased);
  return <>{current}{suffix}</>;
};

export const CCNAShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ============================================================
  // SCENE 1: Title Reveal (0-120 frames / 0-4s)
  // ============================================================

  // "CCNA" slam in (frame 10-40)
  const ccnaScale = spring({
    frame: frame - 10,
    fps,
    config: { damping: 10, stiffness: 150, mass: 0.6 },
    from: 3,
    to: 1,
  });
  const ccnaOpacity = interpolate(frame, [10, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // "200-301" fade in (frame 35-55)
  const codeOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const codeSlideY = spring({
    frame: frame - 35,
    fps,
    config: { damping: 15, stiffness: 100, mass: 0.5 },
    from: 30,
    to: 0,
  });

  // "STUDY SYSTEM" (frame 55-85) - typed via TerminalText
  const studyOpacity = interpolate(frame, [55, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // "// NOTION TEMPLATE" (frame 85-105)
  const tagOpacity = interpolate(frame, [85, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out entire title scene (frame 110-125)
  const titleFadeOut = interpolate(frame, [110, 125], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ============================================================
  // SCENE 2: Feature Counter Grid (120-420 frames / 4-14s)
  // ============================================================

  const features = [
    { num: 10, label: "Databases", suffix: "" },
    { num: 30, label: "Custom Views", suffix: "+" },
    { num: 200, label: "Flashcards", suffix: "+" },
    { num: 80, label: "Acronyms", suffix: "+" },
    { num: 63, label: "Day Tracker", suffix: "" },
    { num: 4, label: "DoK Levels", suffix: "" },
    { num: 200, label: "Port Refs", suffix: "+" },
    { num: 100, label: "CLI Commands", suffix: "+" },
    { num: 4, label: "Study Levels", suffix: "" },
  ];

  // Grid container slides up
  const gridSlideY = spring({
    frame: frame - 120,
    fps,
    config: { damping: 14, stiffness: 80, mass: 0.8 },
    from: 400,
    to: 0,
  });
  const gridOpacity = interpolate(frame, [120, 140], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Grid header "SYSTEM COMPONENTS"
  const gridHeaderOpacity = interpolate(frame, [130, 145], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Stagger each cell: 25 frames apart starting at frame 150
  const cellAnimations = features.map((_, i) => {
    const cellStart = 150 + i * 25;
    const cellOpacity = interpolate(frame, [cellStart, cellStart + 15], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const cellScale = spring({
      frame: frame - cellStart,
      fps,
      config: { damping: 12, stiffness: 150, mass: 0.4 },
      from: 0.5,
      to: 1,
    });
    return { cellOpacity, cellScale, cellStart };
  });

  // Fade out grid (frame 400-420)
  const gridFadeOut = interpolate(frame, [400, 420], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ============================================================
  // SCENE 3: Key Benefits (420-660 frames / 14-22s)
  // ============================================================

  const benefits = [
    {
      title: "ADHD-Friendly Design",
      desc: "Clean layouts. Clear progress. No cognitive overload.",
    },
    {
      title: "Auto-Linked Mistakes",
      desc: "Every error links back to the concept. Learn from failure.",
    },
    {
      title: "Mobile Optimized",
      desc: "Study anywhere. Full functionality on any device.",
    },
  ];

  const benefitAnimations = benefits.map((_, i) => {
    const benefitStart = 430 + i * 70;
    const slideX = spring({
      frame: frame - benefitStart,
      fps,
      config: { damping: 14, stiffness: 100, mass: 0.6 },
      from: i % 2 === 0 ? -600 : 600,
      to: 0,
    });
    const opacity = interpolate(frame, [benefitStart, benefitStart + 20], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    return { slideX, opacity };
  });

  // Fade out benefits (frame 640-660)
  const benefitsFadeOut = interpolate(frame, [640, 660], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ============================================================
  // SCENE 4: DoK Framework (660-840 frames / 22-28s)
  // ============================================================

  // "Built with the" fade in
  const dokIntroOpacity = interpolate(frame, [665, 680], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // "Depths of Knowledge Framework" gold reveal
  const dokTitleOpacity = interpolate(frame, [690, 710], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const dokTitleSlideY = spring({
    frame: frame - 690,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.5 },
    from: 40,
    to: 0,
  });

  // 4 DoK levels animate in
  const dokLevels = [
    { level: "Level 1", name: "Recall", desc: "Remember facts & terms" },
    { level: "Level 2", name: "Skill", desc: "Apply concepts to scenarios" },
    { level: "Level 3", name: "Strategic", desc: "Analyze & troubleshoot" },
    { level: "Level 4", name: "Extended", desc: "Design & architect solutions" },
  ];

  const dokAnimations = dokLevels.map((_, i) => {
    const dokStart = 720 + i * 22;
    const opacity = interpolate(frame, [dokStart, dokStart + 15], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    const slideX = spring({
      frame: frame - dokStart,
      fps,
      config: { damping: 15, stiffness: 120, mass: 0.4 },
      from: 100,
      to: 0,
    });
    return { opacity, slideX };
  });

  // Fade out DoK (frame 820-840)
  const dokFadeOut = interpolate(frame, [820, 840], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ============================================================
  // SCENE 5: CTA (840-1050 frames / 28-35s)
  // ============================================================

  const ctaOpacity = interpolate(frame, [845, 865], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // "Get Your System" scale
  const ctaScale = spring({
    frame: frame - 860,
    fps,
    config: { damping: 10, stiffness: 120, mass: 0.5 },
    from: 0.7,
    to: 1,
  });

  // Gold badge pulse
  const badgePulse = interpolate(
    Math.sin((frame - 880) * 0.08),
    [-1, 1],
    [0.8, 1]
  );

  // URL fade in
  const urlOpacity = interpolate(frame, [920, 945], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Gold glow on badge
  const badgeGlow = frame > 880
    ? interpolate(Math.sin((frame - 880) * 0.1), [-1, 1], [10, 30])
    : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: GOLD.bg }}>
      {/* Background: Gold matrix rain */}
      <MatrixRain opacity={0.06} color={GOLD.accent} speed={0.5} />

      {/* Subtle scan line overlay */}
      <AbsoluteFill
        style={{
          background:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)",
          pointerEvents: "none",
        }}
      />

      {/* ===== SCENE 1: Title Reveal ===== */}
      {frame < 130 && (
        <AbsoluteFill
          style={{
            opacity: titleFadeOut,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {/* CCNA */}
          <div
            style={{
              opacity: ccnaOpacity,
              transform: `scale(${ccnaScale})`,
              fontFamily: FONTS.mono,
              fontSize: 180,
              fontWeight: 700,
              color: GOLD.text,
              textAlign: "center",
              letterSpacing: 20,
              textShadow: `0 0 60px ${GOLD.accent}44`,
            }}
          >
            CCNA
          </div>

          {/* 200-301 */}
          <div
            style={{
              opacity: codeOpacity,
              transform: `translateY(${codeSlideY}px)`,
              fontFamily: FONTS.mono,
              fontSize: 72,
              fontWeight: 700,
              color: GOLD.accent,
              textAlign: "center",
              letterSpacing: 8,
              marginTop: -10,
            }}
          >
            200-301
          </div>

          {/* STUDY SYSTEM */}
          <div style={{ opacity: studyOpacity, marginTop: 20 }}>
            <TerminalText
              text="STUDY SYSTEM"
              startFrame={55}
              speed={1.2}
              fontSize={44}
              color={GOLD.textDim}
              cursorColor={GOLD.accent}
              showCursor={frame < 100}
            />
          </div>

          {/* // NOTION TEMPLATE */}
          <div
            style={{
              opacity: tagOpacity,
              fontFamily: FONTS.mono,
              fontSize: 24,
              color: GOLD.accent,
              marginTop: 30,
              letterSpacing: 3,
            }}
          >
            {"// NOTION TEMPLATE"}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 2: Feature Counter Grid ===== */}
      {frame >= 115 && frame < 425 && (
        <AbsoluteFill
          style={{
            opacity: gridOpacity * gridFadeOut,
            transform: `translateY(${gridSlideY}px)`,
            justifyContent: "center",
            alignItems: "center",
            padding: 80,
          }}
        >
          {/* Header */}
          <div
            style={{
              opacity: gridHeaderOpacity,
              fontFamily: FONTS.mono,
              fontSize: 18,
              color: GOLD.textDim,
              letterSpacing: 6,
              marginBottom: 40,
              textTransform: "uppercase",
            }}
          >
            System Components
          </div>

          {/* Card container */}
          <div
            style={{
              width: 1200,
              borderRadius: 20,
              padding: 3,
              background: `linear-gradient(135deg, ${GOLD.accent}40, ${GOLD.border} 60%)`,
              boxShadow: `0 0 40px ${GOLD.accent}15, 0 20px 60px rgba(0,0,0,0.4)`,
            }}
          >
            <div
              style={{
                backgroundColor: GOLD.cardBg,
                borderRadius: 18,
                padding: 50,
              }}
            >
              {/* Top accent line */}
              <div
                style={{
                  height: 3,
                  background: `linear-gradient(90deg, ${GOLD.accent}, transparent)`,
                  borderRadius: 2,
                  marginBottom: 40,
                }}
              />

              {/* 3x3 grid */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr 1fr",
                  gap: 40,
                }}
              >
                {features.map((feat, i) => (
                  <div
                    key={i}
                    style={{
                      opacity: cellAnimations[i].cellOpacity,
                      transform: `scale(${cellAnimations[i].cellScale})`,
                      display: "flex",
                      flexDirection: "column",
                      gap: 6,
                    }}
                  >
                    {/* Number */}
                    <div
                      style={{
                        fontFamily: FONTS.mono,
                        fontSize: 56,
                        fontWeight: 700,
                        color: GOLD.accent,
                        lineHeight: 1,
                      }}
                    >
                      <CountUp
                        target={feat.num}
                        suffix={feat.suffix}
                        startFrame={cellAnimations[i].cellStart}
                        durationFrames={25}
                      />
                    </div>
                    {/* Label */}
                    <div
                      style={{
                        fontFamily: FONTS.body,
                        fontSize: 20,
                        color: GOLD.text,
                        letterSpacing: 1,
                      }}
                    >
                      {feat.label}
                    </div>
                    {/* Underline */}
                    <div
                      style={{
                        width: 60,
                        height: 1,
                        backgroundColor: GOLD.border,
                        marginTop: 4,
                      }}
                    />
                  </div>
                ))}
              </div>

              {/* Bottom tagline */}
              <div
                style={{
                  marginTop: 35,
                  paddingTop: 20,
                  borderTop: `1px solid ${GOLD.border}`,
                  fontFamily: FONTS.mono,
                  fontSize: 14,
                  color: GOLD.textDim,
                  textAlign: "center",
                  letterSpacing: 2,
                }}
              >
                Auto-Linked Mistakes {"  //  "} Study Analytics {"  //  "} Mobile
                Optimized
              </div>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 3: Key Benefits ===== */}
      {frame >= 415 && frame < 665 && (
        <AbsoluteFill
          style={{
            opacity: benefitsFadeOut,
            justifyContent: "center",
            alignItems: "center",
            padding: 100,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 35,
              width: "100%",
              maxWidth: 1100,
            }}
          >
            {benefits.map((benefit, i) => (
              <div
                key={i}
                style={{
                  opacity: benefitAnimations[i].opacity,
                  transform: `translateX(${benefitAnimations[i].slideX}px)`,
                  display: "flex",
                  alignItems: "center",
                  gap: 30,
                  padding: 35,
                  borderRadius: 16,
                  backgroundColor: GOLD.cardBg,
                  border: `1px solid ${GOLD.border}`,
                  boxShadow: `0 4px 20px rgba(0,0,0,0.3)`,
                }}
              >
                {/* Gold dot */}
                <div
                  style={{
                    width: 14,
                    height: 14,
                    borderRadius: 7,
                    backgroundColor: GOLD.accent,
                    flexShrink: 0,
                    boxShadow: `0 0 12px ${GOLD.accent}66`,
                  }}
                />
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <div
                    style={{
                      fontFamily: FONTS.mono,
                      fontSize: 30,
                      fontWeight: 700,
                      color: GOLD.text,
                    }}
                  >
                    {benefit.title}
                  </div>
                  <div
                    style={{
                      fontFamily: FONTS.body,
                      fontSize: 20,
                      color: GOLD.textDim,
                      lineHeight: 1.4,
                    }}
                  >
                    {benefit.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 4: DoK Framework ===== */}
      {frame >= 655 && frame < 845 && (
        <AbsoluteFill
          style={{
            opacity: dokFadeOut,
            justifyContent: "center",
            alignItems: "center",
            padding: 100,
          }}
        >
          {/* Intro text */}
          <div
            style={{
              opacity: dokIntroOpacity,
              fontFamily: FONTS.body,
              fontSize: 28,
              color: GOLD.textDim,
              textAlign: "center",
              marginBottom: 10,
              letterSpacing: 2,
            }}
          >
            Built with the
          </div>

          {/* Framework title */}
          <div
            style={{
              opacity: dokTitleOpacity,
              transform: `translateY(${dokTitleSlideY}px)`,
              fontFamily: FONTS.mono,
              fontSize: 52,
              fontWeight: 700,
              color: GOLD.accent,
              textAlign: "center",
              marginBottom: 50,
              textShadow: `0 0 30px ${GOLD.accent}33`,
            }}
          >
            Depths of Knowledge Framework
          </div>

          {/* 4 DoK levels */}
          <div
            style={{
              display: "flex",
              gap: 24,
              width: "100%",
              maxWidth: 1200,
            }}
          >
            {dokLevels.map((dok, i) => (
              <div
                key={i}
                style={{
                  opacity: dokAnimations[i].opacity,
                  transform: `translateX(${dokAnimations[i].slideX}px)`,
                  flex: 1,
                  padding: 28,
                  borderRadius: 14,
                  backgroundColor: GOLD.cardBg,
                  border: `1px solid ${GOLD.border}`,
                  display: "flex",
                  flexDirection: "column",
                  gap: 10,
                }}
              >
                {/* Level badge */}
                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 14,
                    color: GOLD.accent,
                    letterSpacing: 2,
                  }}
                >
                  {dok.level}
                </div>
                {/* Name */}
                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 26,
                    fontWeight: 700,
                    color: GOLD.text,
                  }}
                >
                  {dok.name}
                </div>
                {/* Description */}
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontSize: 16,
                    color: GOLD.textDim,
                    lineHeight: 1.4,
                  }}
                >
                  {dok.desc}
                </div>
                {/* Gold accent bar at bottom */}
                <div
                  style={{
                    height: 3,
                    borderRadius: 2,
                    background: `linear-gradient(90deg, ${GOLD.accent}, transparent)`,
                    marginTop: 8,
                    opacity: 0.6 + i * 0.1,
                  }}
                />
              </div>
            ))}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 5: CTA ===== */}
      {frame >= 835 && (
        <AbsoluteFill
          style={{
            opacity: ctaOpacity,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {/* "Get Your System" */}
          <div
            style={{
              transform: `scale(${ctaScale})`,
              fontFamily: FONTS.mono,
              fontSize: 64,
              fontWeight: 700,
              color: GOLD.text,
              textAlign: "center",
              marginBottom: 30,
              letterSpacing: 4,
            }}
          >
            Get Your System
          </div>

          {/* // NOTION TEMPLATE tag */}
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 22,
              color: GOLD.accent,
              letterSpacing: 4,
              marginBottom: 40,
            }}
          >
            {"// NOTION TEMPLATE"}
          </div>

          {/* Gold CTA badge */}
          <div
            style={{
              transform: `scale(${badgePulse})`,
              backgroundColor: GOLD.accent,
              borderRadius: 14,
              padding: "18px 50px",
              boxShadow: `0 0 ${badgeGlow}px ${GOLD.accent}88, 0 8px 30px rgba(0,0,0,0.4)`,
            }}
          >
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 28,
                fontWeight: 700,
                color: GOLD.bg,
                letterSpacing: 2,
              }}
            >
              CCNA 200-301 STUDY SYSTEM
            </div>
          </div>

          {/* URL */}
          <div
            style={{
              opacity: urlOpacity,
              fontFamily: FONTS.mono,
              fontSize: 18,
              color: GOLD.textDim,
              marginTop: 35,
              letterSpacing: 2,
            }}
          >
            coredirective1.gumroad.com
          </div>

          {/* Lifetime Updates + ADHD-Friendly + Money Back row */}
          <div
            style={{
              opacity: urlOpacity,
              display: "flex",
              gap: 40,
              marginTop: 25,
            }}
          >
            {["Lifetime Updates", "ADHD-Friendly", "7-Day Money Back"].map(
              (pt, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: GOLD.accent,
                    }}
                  />
                  <div
                    style={{
                      fontFamily: FONTS.body,
                      fontSize: 16,
                      color: GOLD.textDim,
                    }}
                  >
                    {pt}
                  </div>
                </div>
              )
            )}
          </div>
        </AbsoluteFill>
      )}

      {/* Corner brackets (persistent, subtle) */}
      {/* Top-left */}
      <div
        style={{
          position: "absolute",
          top: 30,
          left: 30,
          width: 60,
          height: 60,
          borderTop: `2px solid ${GOLD.accent}44`,
          borderLeft: `2px solid ${GOLD.accent}44`,
        }}
      />
      {/* Bottom-right */}
      <div
        style={{
          position: "absolute",
          bottom: 30,
          right: 30,
          width: 60,
          height: 60,
          borderBottom: `2px solid ${GOLD.accent}44`,
          borderRight: `2px solid ${GOLD.accent}44`,
        }}
      />
    </AbsoluteFill>
  );
};
