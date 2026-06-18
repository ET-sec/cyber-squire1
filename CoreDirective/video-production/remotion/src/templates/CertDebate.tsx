/**
 * CertDebate.tsx - Animated infographic reveal for LinkedIn Cert Thursday
 *
 * 4 seconds (120 frames), 1080x1920 vertical
 *
 * Takes the static Gemini infographic and adds motion:
 *   0-0.5s  (0-15f):   Title area fades in with scale
 *   0.5-1.2s(15-36f):  Left column (red/cert collector) wipes down to reveal
 *   1.2-1.9s(36-57f):  Middle column (orange/anti cert) wipes down to reveal
 *   1.9-2.6s(57-78f):  Right column (green/builder) wipes down to reveal
 *   2.6-3.2s(78-96f):  "HIRED" area pulses with green glow
 *   3.2-3.6s(96-108f): Diagonal shine sweep across whole image
 *   3.6-4s  (108-120f): Footer text pulses, hold for loop
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
  staticFile,
} from "remotion";

export const CertDebate: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Image dimensions: 572x1024, composition: 1080x1920
  // Scale to fill width, center vertically
  const imgScale = 1080 / 572; // ~1.89x
  const imgHeight = 1024 * imgScale; // ~1935px, close to 1920

  // ---- Overall fade in ----
  const fadeIn = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Title area: scale pop (0-15f) ----
  const titleScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.6 },
    from: 0.85,
    to: 1.0,
  });

  // ---- Column reveals using overlay masks ----
  // Three colored overlays that slide UP to reveal the infographic beneath
  // Each covers roughly 1/3 of the width

  // Left column (red) reveal: overlay slides up from 15-36f
  const leftReveal = interpolate(frame, [12, 34], [0, -100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Middle column (orange) reveal: overlay slides up from 36-57f
  const midReveal = interpolate(frame, [33, 55], [0, -100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Right column (green) reveal: overlay slides up from 57-78f
  const rightReveal = interpolate(frame, [54, 76], [0, -100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- "HIRED" glow pulse (78-96f) ----
  const glowOpacity = interpolate(
    frame,
    [78, 88, 96, 105],
    [0, 0.35, 0.2, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // ---- Diagonal shine sweep (96-108f) ----
  const shinePosition = interpolate(frame, [92, 112], [-50, 150], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ---- Subtle breathing/float on whole image ----
  const floatY = interpolate(
    Math.sin(frame * 0.06),
    [-1, 1],
    [-3, 3]
  );

  // ---- Footer pulse ----
  const footerGlow = interpolate(
    Math.sin(frame * 0.12),
    [-1, 1],
    [0.7, 1.0]
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#F5F0E8" }}>
      {/* Main infographic image with subtle float */}
      <AbsoluteFill
        style={{
          opacity: fadeIn,
          transform: `scale(${titleScale}) translateY(${floatY}px)`,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Img
          src={staticFile("cert-debate-infographic.png")}
          style={{
            width: 1080,
            height: imgHeight,
            objectFit: "cover",
          }}
        />
      </AbsoluteFill>

      {/* Column reveal overlays - these cover the content area below the title */}
      {/* The title bar is roughly the top 8% of the image */}
      {/* The columns run from roughly 8% to 88% of the image height */}
      {/* The footer is the bottom 12% */}

      {/* Left column overlay (matches red bg) */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: "8%",
          width: "34%",
          height: "80%",
          backgroundColor: "#EF9A9A",
          transform: `translateY(${leftReveal}%)`,
          zIndex: 10,
        }}
      />

      {/* Middle column overlay (matches orange bg) */}
      <div
        style={{
          position: "absolute",
          left: "34%",
          top: "8%",
          width: "33%",
          height: "80%",
          backgroundColor: "#FFB74D",
          transform: `translateY(${midReveal}%)`,
          zIndex: 10,
        }}
      />

      {/* Right column overlay (matches green bg) */}
      <div
        style={{
          position: "absolute",
          left: "67%",
          top: "8%",
          width: "33%",
          height: "80%",
          backgroundColor: "#A5D6A7",
          transform: `translateY(${rightReveal}%)`,
          zIndex: 10,
        }}
      />

      {/* Footer overlay - reveals after columns */}
      <div
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          width: "100%",
          height: "7%",
          backgroundColor: "#2C3E50",
          opacity: interpolate(frame, [70, 80], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          zIndex: 10,
        }}
      />

      {/* Green glow on "HIRED" area (bottom right) */}
      <div
        style={{
          position: "absolute",
          right: 0,
          bottom: "8%",
          width: "34%",
          height: "20%",
          background:
            "radial-gradient(ellipse at center, rgba(76, 175, 80, 0.5) 0%, transparent 70%)",
          opacity: glowOpacity,
          zIndex: 15,
          pointerEvents: "none",
        }}
      />

      {/* Diagonal shine sweep */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: `${shinePosition}%`,
          width: "15%",
          height: "100%",
          background:
            "linear-gradient(105deg, transparent 0%, rgba(255,255,255,0.25) 45%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0.25) 55%, transparent 100%)",
          transform: "skewX(-15deg)",
          zIndex: 20,
          pointerEvents: "none",
        }}
      />

      {/* Footer text glow overlay */}
      {frame > 80 && (
        <div
          style={{
            position: "absolute",
            left: 0,
            bottom: 0,
            width: "100%",
            height: "7%",
            boxShadow: `0 0 20px rgba(76, 175, 80, ${footerGlow * 0.3})`,
            zIndex: 15,
            pointerEvents: "none",
          }}
        />
      )}
    </AbsoluteFill>
  );
};
