/**
 * DebtTracker.tsx - Debt payoff journey template (6 seconds, 1080x1920 vertical)
 *
 * Animation timeline:
 *   0-1s     (0-30f):   "WEEK {n}" types in terminal style, large, center
 *   1-2.5s   (30-75f):  Debt counter rolls down (odometer) from startingDebt to currentDebt in RED
 *   2.5-3.5s (75-105f): Green flash, "+${weeklyIncome}" animates up in green
 *   3.5-4.5s (105-135f): Progress bar fills (% of debt paid off)
 *   4.5-5.5s (135-165f): Milestone text or "The grind continues."
 *   5.5-6s   (165-180f): "Follow the journey" fade in
 *
 * Debt number is HUGE (40% screen width), red glow. Income has green glow.
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { MatrixRain } from "../components/MatrixRain";
import { TerminalText } from "../components/TerminalText";
import { ProgressBar } from "../components/ProgressBar";
import { COLORS, FONTS } from "../data/brand";
import { DebtTrackerProps } from "../data/schemas";

export const DebtTracker: React.FC<DebtTrackerProps> = ({
  weekNumber,
  startingDebt,
  currentDebt,
  weeklyIncome,
  incomeSource,
  milestone,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calculate debt progress percentage
  const debtPaid = startingDebt - currentDebt;
  const progressPercent = (debtPaid / startingDebt) * 100;

  // ---- Phase 1: "WEEK {n}" terminal text (frames 0-30) ----
  const weekOpacity = interpolate(frame, [0, 5, 25, 35], [0, 1, 1, 0.3], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // ---- Phase 2: Debt odometer roll (frames 30-75) ----
  // Animated debt value rolls from startingDebt down to currentDebt
  const debtRollProgress = interpolate(frame, [30, 75], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3), // ease-out cubic
  });

  const displayedDebt = Math.round(
    startingDebt - (startingDebt - currentDebt) * debtRollProgress
  );

  const debtOpacity = interpolate(frame, [28, 35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Debt glow pulses while rolling
  const debtGlow =
    frame >= 30 && frame <= 75
      ? interpolate(Math.sin(frame * 0.3), [-1, 1], [10, 25])
      : 8;

  // ---- Phase 3: Income flash (frames 75-105) ----
  // Green flash overlay
  const flashOpacity = interpolate(frame, [75, 78, 85], [0, 0.15, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const incomeSlideY = spring({
    frame: frame - 78,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.5 },
    from: 60,
    to: 0,
  });

  const incomeOpacity = interpolate(frame, [78, 88], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 4: Progress bar (frames 105-135) ----
  const barOpacity = interpolate(frame, [105, 112], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 5: Milestone (frames 135-165) ----
  const milestoneScale = spring({
    frame: frame - 135,
    fps,
    config: { damping: 10, stiffness: 120, mass: 0.6 },
    from: 0.5,
    to: 1,
  });

  const milestoneOpacity = interpolate(frame, [135, 142], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Phase 6: Follow CTA (frames 165-180) ----
  const ctaOpacity = interpolate(frame, [165, 175], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Format number as currency string
  const formatCurrency = (n: number): string => {
    return "$" + n.toLocaleString("en-US");
  };

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary }}>
      {/* Subtle matrix rain background */}
      <MatrixRain opacity={0.06} speed={0.5} />

      {/* Green flash overlay for income reveal */}
      <AbsoluteFill
        style={{
          backgroundColor: COLORS.accent,
          opacity: flashOpacity,
          pointerEvents: "none",
        }}
      />

      {/* Main content */}
      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 60,
          gap: 40,
        }}
      >
        {/* Phase 1: Week number */}
        <div style={{ opacity: weekOpacity, marginBottom: 20 }}>
          <TerminalText
            text={`WEEK ${weekNumber}`}
            startFrame={0}
            speed={2.5}
            fontSize={72}
            color={COLORS.accent}
            style={{ textAlign: "center" }}
          />
        </div>

        {/* Phase 2: Debt counter (HUGE, red glow) */}
        <div
          style={{
            opacity: debtOpacity,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 20,
              color: COLORS.textDim,
              letterSpacing: 6,
              textTransform: "uppercase",
              marginBottom: 12,
            }}
          >
            REMAINING DEBT
          </div>
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 108,
              fontWeight: 700,
              color: COLORS.secondary,
              textShadow: `0 0 ${debtGlow}px ${COLORS.secondary}, 0 0 ${debtGlow * 2}px ${COLORS.secondary}44`,
              lineHeight: 1,
              // Make the number take ~40% of screen width
              letterSpacing: -2,
            }}
          >
            {formatCurrency(displayedDebt)}
          </div>
        </div>

        {/* Phase 3: Weekly income */}
        <div
          style={{
            opacity: incomeOpacity,
            transform: `translateY(${incomeSlideY}px)`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 64,
              fontWeight: 700,
              color: COLORS.accent,
              textShadow: `0 0 15px ${COLORS.accent}88, 0 0 30px ${COLORS.accent}44`,
            }}
          >
            +{formatCurrency(weeklyIncome)}
          </div>
          <div
            style={{
              fontFamily: FONTS.body,
              fontSize: 28,
              color: COLORS.textDim,
              marginTop: 8,
            }}
          >
            {incomeSource}
          </div>
        </div>

        {/* Phase 4: Progress bar */}
        <div
          style={{
            opacity: barOpacity,
            width: "100%",
            maxWidth: 800,
          }}
        >
          <ProgressBar
            progress={progressPercent}
            startFrame={105}
            label="DEBT ELIMINATED"
            height={36}
          />
        </div>

        {/* Phase 5: Milestone or grind message */}
        <div
          style={{
            opacity: milestoneOpacity,
            transform: `scale(${milestoneScale})`,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 36,
              color: milestone ? COLORS.accent : COLORS.textDim,
              textShadow: milestone
                ? `0 0 10px ${COLORS.accent}44`
                : "none",
              fontStyle: milestone ? "normal" : "italic",
            }}
          >
            {milestone || "The grind continues."}
          </div>
        </div>

        {/* Phase 6: Follow CTA */}
        <div
          style={{
            opacity: ctaOpacity,
            fontFamily: FONTS.body,
            fontSize: 28,
            color: COLORS.textDim,
            textAlign: "center",
            letterSpacing: 4,
            textTransform: "uppercase",
            marginTop: 20,
          }}
        >
          Follow the journey
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
