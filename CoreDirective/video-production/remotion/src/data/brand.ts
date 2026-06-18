/**
 * CoreDirective Brand Constants
 * All colors, fonts, and shared design tokens used across templates.
 */

export const COLORS = {
  /** Near-black background */
  primary: "#0A0A0A",
  /** Matrix green accent */
  accent: "#00FF41",
  /** Alert red secondary */
  secondary: "#FF3366",
  /** White text */
  text: "#FFFFFF",
  /** Dimmed text for sources / secondary info */
  textDim: "rgba(255, 255, 255, 0.5)",
  /** Gold for salary category */
  gold: "#FFD700",
  /** Purple for hack category */
  purple: "#9B59B6",
  /** Card background */
  cardBg: "rgba(10, 10, 10, 0.92)",
  /** Card border */
  cardBorder: "rgba(0, 255, 65, 0.4)",
} as const;

export const FONTS = {
  /** Monospace font for code/tech elements */
  mono: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
  /** Body font for readable text */
  body: "'Inter', 'Helvetica Neue', Arial, sans-serif",
} as const;

/** Vertical (TikTok / Shorts) dimensions */
export const VERTICAL = {
  width: 1080,
  height: 1920,
} as const;

/** Horizontal (YouTube) dimensions */
export const HORIZONTAL = {
  width: 1920,
  height: 1080,
} as const;

/** Frames per second for all compositions */
export const FPS = 30;

/**
 * Map DidYouKnow categories to their accent colors.
 */
export const CATEGORY_COLORS: Record<string, string> = {
  "THREAT INTEL": COLORS.secondary,
  CAREER: COLORS.accent,
  SALARY: COLORS.gold,
  HACK: COLORS.purple,
};
