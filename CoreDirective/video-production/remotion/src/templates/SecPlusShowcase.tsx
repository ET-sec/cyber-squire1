/**
 * SecPlusShowcase.tsx - Security+ SY0-701 Study System product showcase (50s, 1920x1080)
 *
 * NOTION DARK MODE UI — authentic look with real sidebar, database chrome, breadcrumbs.
 * RED theme (#EB5757 Notion red accent). NO price displayed. NO audio.
 *
 * Scene timeline:
 *   0-4.5s   (0-135f):      Title reveal — "SEC+" slam + "SY0-701" + typed "STUDY SYSTEM"
 *   4.5-8.5s (135-255f):    Workspace Overview — sidebar + main page
 *   8.5-16s  (255-480f):    Exam Readiness Tracker (table)
 *   16-22s   (480-660f):    Knowledge Base (kanban)
 *   22-28s   (660-840f):    Acronym Database (table)
 *   28-34s   (840-1020f):   Port Numbers & Protocols (card rows)
 *   34-40s   (1020-1200f):  Study Analytics (dashboard)
 *   40-45s   (1200-1350f):  DoK Framework (4 levels)
 *   45-50s   (1350-1500f):  CTA — NO PRICE
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
import { FONTS } from "../data/brand";

// ============================================================
// NOTION DARK MODE THEME
// ============================================================

const N = {
  bg: "#191919",
  sidebar: "#202020",
  sidebarText: "rgba(255,255,255,0.73)",
  sidebarTextDim: "rgba(255,255,255,0.443)",
  sidebarActive: "rgba(255,255,255,0.094)",
  text: "rgba(255,255,255,0.81)",
  textDim: "rgba(255,255,255,0.443)",
  border: "rgba(255,255,255,0.094)",
  tableHeaderBg: "rgba(255,255,255,0.024)",
  red: "#EB5757",
  white: "#FFFFFF",
} as const;

const TAG = {
  blue:   { bg: "rgba(45,105,176,0.4)",  text: "#6DA8E8" },
  green:  { bg: "rgba(43,106,78,0.4)",   text: "#61AA85" },
  red:    { bg: "rgba(176,56,56,0.4)",    text: "#DF7070" },
  purple: { bg: "rgba(123,72,165,0.4)",   text: "#A980CB" },
  orange: { bg: "rgba(176,110,46,0.4)",   text: "#D69E60" },
  yellow: { bg: "rgba(169,142,45,0.4)",   text: "#D3BD63" },
  pink:   { bg: "rgba(161,60,101,0.4)",   text: "#CF759B" },
  gray:   { bg: "rgba(255,255,255,0.094)", text: "rgba(255,255,255,0.6)" },
} as const;

type TagColor = keyof typeof TAG;

// ============================================================
// SCENE DATA — Security+ SY0-701
// ============================================================

const SIDEBAR_SECTIONS = [
  {
    label: "Core Study System",
    items: [
      { icon: "\uD83C\uDFAF", name: "Exam Readiness Tracker" },
      { icon: "\uD83D\uDCD8", name: "Knowledge Base" },
      { icon: "\u274C", name: "Practice Exam Mistakes" },
    ],
  },
  {
    label: "Technical Reference",
    items: [
      { icon: "\uD83D\uDD0C", name: "Port Numbers" },
      { icon: "\uD83D\uDCDC", name: "Command Grimoire" },
      { icon: "\uD83D\uDD24", name: "Acronyms (325+)" },
    ],
  },
  {
    label: "Portfolio & Career",
    items: [
      { icon: "\uD83E\uDDEA", name: "Lab Environment Log" },
      { icon: "\uD83D\uDCBC", name: "Career Pipeline" },
    ],
  },
  {
    label: "Progress Tracking",
    items: [
      { icon: "\uD83D\uDCCA", name: "Study Analytics" },
    ],
  },
];

const EXAM_ROWS = [
  { obj: "1.4 \u2014 Compare authentication methods", domain: "General Security", domainColor: "blue" as TagColor, conf: 3, level: "Concept", lvlColor: "yellow" as TagColor, priority: 78 },
  { obj: "2.3 \u2014 Explain cryptographic solutions", domain: "Threats & Vulns", domainColor: "red" as TagColor, conf: 2, level: "Analysis", lvlColor: "orange" as TagColor, priority: 92 },
  { obj: "3.2 \u2014 Apply security to infrastructure", domain: "Architecture", domainColor: "purple" as TagColor, conf: 1, level: "Application", lvlColor: "red" as TagColor, priority: 95 },
  { obj: "4.1 \u2014 Apply common security techniques", domain: "Operations", domainColor: "green" as TagColor, conf: 4, level: "Recall", lvlColor: "green" as TagColor, priority: 45 },
  { obj: "5.3 \u2014 Explain compliance concepts", domain: "Governance", domainColor: "gray" as TagColor, conf: 2, level: "Concept", lvlColor: "yellow" as TagColor, priority: 88 },
];

const KB_COLS = [
  { name: "Threats & Attacks", color: "red" as TagColor, cards: ["Phishing & Social Eng.", "Ransomware", "SQL Injection", "On-Path Attacks"] },
  { name: "Cryptography", color: "purple" as TagColor, cards: ["AES Encryption", "PKI & Certificates", "Hashing Algorithms"] },
  { name: "Identity & Access", color: "blue" as TagColor, cards: ["MFA", "RBAC", "SSO & SAML", "Zero Trust"] },
];

const ACRONYMS = [
  { abbr: "SIEM", full: "Security Information and Event Management", cat: "Operations", catColor: "green" as TagColor, drill: "High", drillColor: "red" as TagColor, mastery: "Concept" },
  { abbr: "SOAR", full: "Security Orchestration, Automation & Response", cat: "Operations", catColor: "green" as TagColor, drill: "High", drillColor: "red" as TagColor, mastery: "New" },
  { abbr: "XDR", full: "Extended Detection and Response", cat: "Operations", catColor: "green" as TagColor, drill: "Medium", drillColor: "orange" as TagColor, mastery: "Recall" },
  { abbr: "CASB", full: "Cloud Access Security Broker", cat: "Architecture", catColor: "purple" as TagColor, drill: "High", drillColor: "red" as TagColor, mastery: "New" },
  { abbr: "ZTNA", full: "Zero Trust Network Access", cat: "Architecture", catColor: "purple" as TagColor, drill: "Medium", drillColor: "orange" as TagColor, mastery: "Concept" },
  { abbr: "AES", full: "Advanced Encryption Standard", cat: "Implementation", catColor: "blue" as TagColor, drill: "Low", drillColor: "green" as TagColor, mastery: "Mastered" },
];

const PORTS = [
  { port: 22, proto: "SSH", use: "Secure remote access", mastery: "Mastered", mColor: "green" as TagColor },
  { port: 80, proto: "HTTP", use: "Unencrypted web traffic", mastery: "Mastered", mColor: "green" as TagColor },
  { port: 443, proto: "HTTPS", use: "Encrypted web traffic", mastery: "Mastered", mColor: "green" as TagColor },
  { port: 3389, proto: "RDP", use: "Remote Desktop Protocol", mastery: "Review", mColor: "yellow" as TagColor },
  { port: 161, proto: "SNMP", use: "Network monitoring", mastery: "New", mColor: "red" as TagColor },
  { port: 514, proto: "Syslog", use: "Log collection", mastery: "Review", mColor: "yellow" as TagColor },
];

const METRICS = [
  { label: "Study Hours", cur: 32, max: 50, color: "blue" as TagColor },
  { label: "Concepts Mastered", cur: 22, max: 40, color: "green" as TagColor },
  { label: "Acronyms Drilled", cur: 180, max: 325, color: "purple" as TagColor },
  { label: "Ports Memorized", cur: 28, max: 42, color: "orange" as TagColor },
];

const DOK = [
  { n: 1, name: "Recall", desc: "Remember facts & definitions", color: "green" as TagColor },
  { n: 2, name: "Concept", desc: "Explain & apply concepts", color: "yellow" as TagColor },
  { n: 3, name: "Analysis", desc: "Analyze & troubleshoot", color: "orange" as TagColor },
  { n: 4, name: "Application", desc: "Design & architect solutions", color: "red" as TagColor },
];

// ============================================================
// HELPERS
// ============================================================

const CountUp: React.FC<{ target: number; suffix?: string; startFrame: number; dur?: number }> = ({
  target, suffix = "", startFrame, dur = 30,
}) => {
  const frame = useCurrentFrame();
  const p = Math.min(Math.max(0, frame - startFrame) / dur, 1);
  return <>{Math.round(target * (1 - Math.pow(1 - p, 3)))}{suffix}</>;
};

/** Notion-style tag pill */
const Pill: React.FC<{ text: string; color: TagColor; small?: boolean }> = ({ text, color, small }) => (
  <div style={{
    display: "inline-flex",
    padding: small ? "2px 7px" : "3px 8px",
    borderRadius: 3,
    backgroundColor: TAG[color].bg,
    color: TAG[color].text,
    fontFamily: FONTS.body,
    fontSize: small ? 12 : 13,
    fontWeight: 500,
    whiteSpace: "nowrap",
    lineHeight: 1.4,
  }}>
    {text}
  </div>
);

/** Notion-style breadcrumb bar */
const Breadcrumb: React.FC<{ parts: string[]; opacity: number }> = ({ parts, opacity }) => (
  <div style={{
    opacity,
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "12px 0 8px 0",
    marginBottom: 4,
  }}>
    <div style={{
      fontFamily: FONTS.body,
      fontSize: 13,
      color: N.textDim,
      display: "flex",
      alignItems: "center",
      gap: 6,
    }}>
      <span style={{ cursor: "pointer" }}>\u2190</span>
      {parts.map((part, i) => (
        <React.Fragment key={i}>
          {i > 0 && <span style={{ color: N.textDim, opacity: 0.5 }}>/</span>}
          <span style={{ color: i === parts.length - 1 ? N.text : N.textDim }}>
            {part}
          </span>
        </React.Fragment>
      ))}
    </div>
  </div>
);

/** Notion-style page title with icon */
const PageTitle: React.FC<{
  icon: string; title: string; opacity: number; slideY?: number;
}> = ({ icon, title, opacity, slideY = 0 }) => (
  <div style={{
    opacity,
    transform: `translateY(${slideY}px)`,
    display: "flex",
    alignItems: "center",
    gap: 12,
    marginBottom: 16,
    padding: "4px 0",
  }}>
    <span style={{ fontSize: 32 }}>{icon}</span>
    <div style={{
      fontFamily: FONTS.body,
      fontSize: 28,
      fontWeight: 700,
      color: N.text,
      letterSpacing: -0.5,
    }}>
      {title}
    </div>
  </div>
);

/** Notion-style view tabs */
const ViewTabs: React.FC<{ tabs: string[]; active: number; opacity: number }> = ({ tabs, active, opacity }) => (
  <div style={{
    opacity,
    display: "flex",
    gap: 0,
    marginBottom: 12,
    borderBottom: `1px solid ${N.border}`,
  }}>
    {tabs.map((tab, i) => (
      <div key={i} style={{
        padding: "7px 14px",
        fontFamily: FONTS.body,
        fontSize: 13,
        color: i === active ? N.text : N.textDim,
        borderBottom: i === active ? `2px solid ${N.red}` : "2px solid transparent",
        fontWeight: i === active ? 600 : 400,
        cursor: "default",
      }}>
        {tab}
      </div>
    ))}
  </div>
);

/** Notion-style filter pill */
const FilterBadge: React.FC<{ text: string }> = ({ text }) => (
  <div style={{
    padding: "3px 10px",
    borderRadius: 3,
    backgroundColor: N.border,
    fontFamily: FONTS.body,
    fontSize: 12,
    color: N.textDim,
  }}>
    {text}
  </div>
);

/** Notion-style bottom badge bar */
const BottomBadge: React.FC<{ text: string; opacity: number }> = ({ text, opacity }) => (
  <div style={{
    opacity,
    marginTop: 14,
    padding: "8px 14px",
    borderRadius: 4,
    backgroundColor: N.tableHeaderBg,
    border: `1px solid ${N.border}`,
    fontFamily: FONTS.body,
    fontSize: 12,
    color: N.textDim,
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
  }}>
    {text}
  </div>
);

// ============================================================
// MAIN COMPONENT
// ============================================================

export const SecPlusShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sceneFade = (start: number, end: number, fadeIn = 20, fadeOut = 20) => {
    const fi = fadeIn > 0
      ? interpolate(frame, [start, start + fadeIn], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
      : frame >= start ? 1 : 0;
    const fo = fadeOut > 0
      ? interpolate(frame, [end - fadeOut, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
      : 1;
    return fi * fo;
  };

  const sp = (from: number, to: number, startFrame: number, config?: object) =>
    spring({ frame: frame - startFrame, fps, config: { damping: 14, stiffness: 100, mass: 0.6, ...config }, from, to });

  // ============================================================
  // SCENE 1: TITLE (0-135)
  // ============================================================
  const s1 = sceneFade(0, 135, 10, 20);

  const secScale = sp(3, 1, 10, { damping: 10, stiffness: 150, mass: 0.6 });
  const secOp = interpolate(frame, [10, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const codeOp = interpolate(frame, [35, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const codeY = sp(30, 0, 35, { damping: 15, stiffness: 100, mass: 0.5 });
  const studyOp = interpolate(frame, [55, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tagOp = interpolate(frame, [85, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // ============================================================
  // SCENE 2: WORKSPACE OVERVIEW (135-255)
  // ============================================================
  const s2 = sceneFade(135, 255);

  const sidebarOp = interpolate(frame, [140, 158], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const mainOp = interpolate(frame, [155, 173], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Scroll the main area down
  const scrollY = interpolate(frame, [180, 235], [0, -120], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const statsBadgeOp = interpolate(frame, [210, 228], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // ============================================================
  // SCENE 3: EXAM READINESS (255-480)
  // ============================================================
  const s3 = sceneFade(255, 480);

  const examRowAnims = EXAM_ROWS.map((_, i) => {
    const rs = 300 + i * 18;
    return {
      opacity: interpolate(frame, [rs, rs + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      slideX: sp(40, 0, rs, { damping: 16, stiffness: 120, mass: 0.4 }),
      startFrame: rs,
    };
  });

  const highlightRow = frame < 380 ? -1 : frame < 410 ? 1 : frame < 440 ? 2 : frame < 465 ? 4 : -1;

  // ============================================================
  // SCENE 4: KNOWLEDGE BASE (480-660)
  // ============================================================
  const s4 = sceneFade(480, 660);

  // ============================================================
  // SCENE 5: ACRONYM DATABASE (660-840)
  // ============================================================
  const s5 = sceneFade(660, 840);

  // ============================================================
  // SCENE 6: PORT NUMBERS (840-1020)
  // ============================================================
  const s6 = sceneFade(840, 1020);

  // ============================================================
  // SCENE 7: ANALYTICS (1020-1200)
  // ============================================================
  const s7 = sceneFade(1020, 1200);

  // ============================================================
  // SCENE 8: DOK (1200-1350)
  // ============================================================
  const s8 = sceneFade(1200, 1350);

  // ============================================================
  // SCENE 9: CTA (1350-1500)
  // ============================================================
  const s9 = sceneFade(1350, 1500, 20, 0);

  const ctaScale = sp(0.7, 1, 1370, { damping: 10, stiffness: 120 });
  const badgePulse = interpolate(Math.sin((frame - 1400) * 0.08), [-1, 1], [0.97, 1.03]);
  const badgeGlow = frame > 1400 ? interpolate(Math.sin((frame - 1400) * 0.1), [-1, 1], [6, 24]) : 0;

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <AbsoluteFill style={{ backgroundColor: N.bg, overflow: "hidden" }}>

      {/* ===== SCENE 1: TITLE ===== */}
      {frame < 140 && (
        <AbsoluteFill style={{ opacity: s1, justifyContent: "center", alignItems: "center" }}>
          {/* Very subtle MatrixRain for scene 1 only */}
          <MatrixRain opacity={0.025} color={N.red} speed={0.25} />

          <div style={{
            opacity: secOp,
            transform: `scale(${secScale})`,
            fontFamily: FONTS.body, fontSize: 160, fontWeight: 700,
            color: N.white, textAlign: "center", letterSpacing: -4,
          }}>
            SEC+
          </div>
          <div style={{
            opacity: codeOp,
            transform: `translateY(${codeY}px)`,
            fontFamily: FONTS.mono, fontSize: 64, fontWeight: 700,
            color: N.red, textAlign: "center", letterSpacing: 4, marginTop: -8,
          }}>
            SY0-701
          </div>
          <div style={{ opacity: studyOp, marginTop: 20 }}>
            <TerminalText
              text="STUDY SYSTEM"
              startFrame={55}
              speed={1.2}
              fontSize={40}
              color={N.textDim}
              cursorColor={N.red}
              showCursor={frame < 100}
            />
          </div>
          <div style={{
            opacity: tagOp,
            fontFamily: FONTS.body, fontSize: 20, color: N.textDim,
            marginTop: 28, letterSpacing: 2,
          }}>
            {"// NOTION TEMPLATE"}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 2: WORKSPACE OVERVIEW ===== */}
      {frame >= 130 && frame < 260 && (
        <AbsoluteFill style={{ opacity: s2, display: "flex", flexDirection: "row" }}>
          {/* Sidebar */}
          <div style={{
            opacity: sidebarOp,
            width: 260,
            backgroundColor: N.sidebar,
            borderRight: `1px solid ${N.border}`,
            padding: "20px 10px",
            display: "flex",
            flexDirection: "column",
            flexShrink: 0,
            overflow: "hidden",
          }}>
            {/* Workspace name */}
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "8px 10px",
              marginBottom: 14,
            }}>
              <div style={{
                width: 22, height: 22, borderRadius: 4,
                backgroundColor: N.red,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: FONTS.body, fontSize: 13, fontWeight: 700, color: N.white,
              }}>
                C
              </div>
              <div style={{
                fontFamily: FONTS.body, fontSize: 14, fontWeight: 600,
                color: N.sidebarText,
              }}>
                Cyber-Squire OS
              </div>
            </div>

            {/* Sidebar sections */}
            {SIDEBAR_SECTIONS.map((section, si) => {
              const secStart = 150 + si * 12;
              const secOp2 = interpolate(frame, [secStart, secStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={si} style={{ opacity: secOp2, marginBottom: 6 }}>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 11, fontWeight: 600,
                    color: N.sidebarTextDim,
                    padding: "6px 12px 3px 12px",
                    textTransform: "uppercase",
                    letterSpacing: 0.5,
                  }}>
                    {section.label}
                  </div>
                  {section.items.map((item, ii) => {
                    const itemStart = secStart + 5 + ii * 5;
                    const itemOp = interpolate(frame, [itemStart, itemStart + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                    return (
                      <div key={ii} style={{
                        opacity: itemOp,
                        display: "flex",
                        alignItems: "center",
                        gap: 7,
                        padding: "5px 12px",
                        borderRadius: 4,
                        fontFamily: FONTS.body,
                        fontSize: 13,
                        color: N.sidebarText,
                        cursor: "default",
                      }}>
                        <span style={{ fontSize: 15 }}>{item.icon}</span>
                        <span>{item.name}</span>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>

          {/* Main content area */}
          <div style={{
            opacity: mainOp,
            flex: 1,
            padding: "40px 60px",
            overflow: "hidden",
          }}>
            <div style={{ transform: `translateY(${scrollY}px)` }}>
              {/* Page icon and title */}
              <div style={{ fontSize: 52, marginBottom: 8 }}>{"\uD83D\uDEE1\uFE0F"}</div>
              <div style={{
                fontFamily: FONTS.body, fontSize: 38, fontWeight: 700,
                color: N.text, letterSpacing: -0.5, marginBottom: 10,
              }}>
                Cyber-Squire OS
              </div>
              <div style={{
                fontFamily: FONTS.body, fontSize: 15, color: N.textDim,
                marginBottom: 28, lineHeight: 1.6, maxWidth: 700,
              }}>
                Your complete Security+ SY0-701 study system. Every objective, every acronym, every port number — organized, tracked, and ready for exam day.
              </div>

              {/* Section callouts — Notion-style callout blocks */}
              {[
                { icon: "\uD83C\uDFAF", label: "Core Study System", desc: "Exam Readiness Tracker, Knowledge Base, Practice Mistakes" },
                { icon: "\uD83D\uDD0C", label: "Technical Reference", desc: "Port Numbers, Command Grimoire, 325+ Acronyms" },
                { icon: "\uD83D\uDCBC", label: "Portfolio & Career", desc: "Lab Environment Log, Career Pipeline" },
                { icon: "\uD83D\uDCCA", label: "Progress Tracking", desc: "Study Analytics, Weekly Efficiency" },
              ].map((block, i) => {
                const blockStart = 168 + i * 10;
                const blockOp = interpolate(frame, [blockStart, blockStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                const blockX = sp(30, 0, blockStart, { damping: 16, stiffness: 120, mass: 0.4 });
                return (
                  <div key={i} style={{
                    opacity: blockOp,
                    transform: `translateX(${blockX}px)`,
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    padding: "14px 18px",
                    marginBottom: 8,
                    backgroundColor: N.tableHeaderBg,
                    borderRadius: 4,
                    border: `1px solid ${N.border}`,
                  }}>
                    <span style={{ fontSize: 22 }}>{block.icon}</span>
                    <div>
                      <div style={{ fontFamily: FONTS.body, fontSize: 15, fontWeight: 600, color: N.text }}>
                        {block.label}
                      </div>
                      <div style={{ fontFamily: FONTS.body, fontSize: 13, color: N.textDim, marginTop: 2 }}>
                        {block.desc}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Stats badge */}
              <div style={{
                opacity: statsBadgeOp,
                marginTop: 16,
                display: "flex",
                gap: 10,
              }}>
                {["10 Databases", "35+ Views", "325+ Acronyms"].map((s, i) => (
                  <div key={i} style={{
                    padding: "4px 12px",
                    borderRadius: 3,
                    backgroundColor: TAG.red.bg,
                    fontFamily: FONTS.body,
                    fontSize: 12,
                    fontWeight: 500,
                    color: TAG.red.text,
                  }}>
                    {s}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 3: EXAM READINESS TRACKER ===== */}
      {frame >= 250 && frame < 485 && (
        <AbsoluteFill style={{ opacity: s3, padding: "36px 80px" }}>
          <Breadcrumb
            parts={["Cyber-Squire OS", "Core Study System", "Exam Readiness Tracker"]}
            opacity={interpolate(frame, [258, 273], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
          <PageTitle
            icon={"\uD83C\uDFAF"}
            title="Exam Readiness Tracker"
            opacity={interpolate(frame, [265, 280], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(15, 0, 265)}
          />
          <ViewTabs
            tabs={["All Objectives", "Today's Focus", "Weak Areas", "Exam Ready"]}
            active={1}
            opacity={interpolate(frame, [275, 290], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />

          {/* Table */}
          <div style={{
            borderRadius: 4,
            border: `1px solid ${N.border}`,
            overflow: "hidden",
            opacity: interpolate(frame, [285, 298], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {/* Header */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "2.6fr 1.2fr 0.5fr 1fr 0.6fr",
              backgroundColor: N.tableHeaderBg,
              padding: "9px 16px",
              borderBottom: `1px solid ${N.border}`,
            }}>
              {["Objective", "Domain", "Conf.", "Action Level", "Priority"].map((h) => (
                <div key={h} style={{
                  fontFamily: FONTS.body, fontSize: 12, fontWeight: 500,
                  color: N.textDim,
                }}>
                  {h}
                </div>
              ))}
            </div>

            {/* Rows */}
            {EXAM_ROWS.map((row, i) => (
              <div key={i} style={{
                display: "grid",
                gridTemplateColumns: "2.6fr 1.2fr 0.5fr 1fr 0.6fr",
                padding: "11px 16px",
                borderBottom: i < EXAM_ROWS.length - 1 ? `1px solid ${N.border}` : "none",
                backgroundColor: highlightRow === i ? "rgba(45,105,176,0.08)" : "transparent",
                borderLeft: highlightRow === i ? `3px solid ${TAG.blue.text}` : "3px solid transparent",
                opacity: examRowAnims[i].opacity,
                transform: `translateX(${examRowAnims[i].slideX}px)`,
                alignItems: "center",
                transition: "background-color 0.15s",
              }}>
                <div style={{
                  fontFamily: FONTS.body, fontSize: 14, color: N.text,
                  overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", paddingRight: 12,
                }}>
                  {row.obj}
                </div>
                <div><Pill text={row.domain} color={row.domainColor} small /></div>
                <div style={{
                  fontFamily: FONTS.body, fontSize: 14, fontWeight: 600,
                  color: row.conf >= 3 ? TAG.green.text : row.conf >= 2 ? TAG.yellow.text : TAG.red.text,
                }}>
                  {frame >= examRowAnims[i].startFrame ? <CountUp target={row.conf} startFrame={examRowAnims[i].startFrame} dur={15} /> : 0}
                </div>
                <div><Pill text={row.level} color={row.lvlColor} small /></div>
                <div style={{ fontFamily: FONTS.body, fontSize: 13, color: N.textDim }}>
                  {frame >= examRowAnims[i].startFrame ? <CountUp target={row.priority} startFrame={examRowAnims[i].startFrame} dur={20} /> : 0}
                </div>
              </div>
            ))}
          </div>

          {/* Filter pills */}
          <div style={{
            marginTop: 12,
            display: "flex", gap: 8, alignItems: "center",
            opacity: interpolate(frame, [400, 415], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            <FilterBadge text="Filter: Confidence < 3" />
            <FilterBadge text="Sort: Priority Score \u2193" />
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 4: KNOWLEDGE BASE (KANBAN) ===== */}
      {frame >= 475 && frame < 665 && (
        <AbsoluteFill style={{ opacity: s4, padding: "36px 80px" }}>
          <Breadcrumb
            parts={["Cyber-Squire OS", "Core Study System", "Knowledge Base"]}
            opacity={interpolate(frame, [483, 498], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
          <PageTitle
            icon={"\uD83D\uDCD8"}
            title="Knowledge Base (Concepts)"
            opacity={interpolate(frame, [490, 505], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(15, 0, 490)}
          />
          <ViewTabs
            tabs={["All Concepts", "By Category", "Study Next", "Mastered"]}
            active={1}
            opacity={interpolate(frame, [500, 515], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />

          {/* Kanban board */}
          <div style={{
            display: "flex", gap: 16, flex: 1,
            opacity: interpolate(frame, [510, 525], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {KB_COLS.map((col, ci) => {
              const colStart = 520 + ci * 18;
              const colOp = interpolate(frame, [colStart, colStart + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={ci} style={{
                  flex: 1, opacity: colOp,
                  display: "flex", flexDirection: "column", gap: 8,
                }}>
                  {/* Column header */}
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "6px 8px", marginBottom: 4,
                  }}>
                    <div style={{
                      width: 9, height: 9, borderRadius: "50%",
                      backgroundColor: TAG[col.color].text,
                    }} />
                    <div style={{
                      fontFamily: FONTS.body, fontSize: 14, fontWeight: 600, color: N.text,
                    }}>
                      {col.name}
                    </div>
                    <div style={{
                      fontFamily: FONTS.body, fontSize: 12, color: N.textDim,
                      backgroundColor: N.border, borderRadius: 3, padding: "1px 6px",
                    }}>
                      {col.cards.length}
                    </div>
                  </div>

                  {/* Cards */}
                  {col.cards.map((card, ki) => {
                    const cardStart = colStart + 12 + ki * 10;
                    const cardOp = interpolate(frame, [cardStart, cardStart + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                    const cardY = sp(25, 0, cardStart, { damping: 18, stiffness: 130, mass: 0.3 });
                    return (
                      <div key={ki} style={{
                        opacity: cardOp,
                        transform: `translateY(${cardY}px)`,
                        backgroundColor: N.sidebar,
                        border: `1px solid ${N.border}`,
                        borderRadius: 4,
                        padding: "12px 14px",
                        display: "flex", flexDirection: "column", gap: 8,
                      }}>
                        <div style={{
                          fontFamily: FONTS.body, fontSize: 14, color: N.text, fontWeight: 500,
                        }}>
                          {card}
                        </div>
                        <div style={{ display: "flex", gap: 6 }}>
                          <Pill text="SY0-701" color={col.color} small />
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 5: ACRONYM DATABASE ===== */}
      {frame >= 655 && frame < 845 && (
        <AbsoluteFill style={{ opacity: s5, padding: "36px 80px" }}>
          <Breadcrumb
            parts={["Cyber-Squire OS", "Technical Reference", "Acronyms"]}
            opacity={interpolate(frame, [663, 678], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
          <PageTitle
            icon={"\uD83D\uDD24"}
            title="325+ Security+ Acronyms"
            opacity={interpolate(frame, [670, 685], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(15, 0, 670)}
          />
          <ViewTabs
            tabs={["All Acronyms", "Drill Priority", "By Category", "Mastered"]}
            active={1}
            opacity={interpolate(frame, [680, 695], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />

          {/* Table */}
          <div style={{
            borderRadius: 4,
            border: `1px solid ${N.border}`,
            overflow: "hidden",
            opacity: interpolate(frame, [688, 703], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${sp(15, 0, 688)}px)`,
          }}>
            {/* Header */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "0.7fr 2.5fr 1fr 0.7fr 0.7fr",
              backgroundColor: N.tableHeaderBg,
              padding: "9px 16px",
              borderBottom: `1px solid ${N.border}`,
            }}>
              {["Acronym", "Full Name", "Category", "Drill", "Mastery"].map((h) => (
                <div key={h} style={{
                  fontFamily: FONTS.body, fontSize: 12, fontWeight: 500,
                  color: N.textDim,
                }}>
                  {h}
                </div>
              ))}
            </div>

            {/* Rows */}
            {ACRONYMS.map((a, i) => {
              const aStart = 705 + i * 16;
              const aOp = interpolate(frame, [aStart, aStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const aX = sp(40, 0, aStart, { damping: 16, stiffness: 120, mass: 0.4 });
              return (
                <div key={i} style={{
                  display: "grid",
                  gridTemplateColumns: "0.7fr 2.5fr 1fr 0.7fr 0.7fr",
                  padding: "10px 16px",
                  borderBottom: i < ACRONYMS.length - 1 ? `1px solid ${N.border}` : "none",
                  opacity: aOp,
                  transform: `translateX(${aX}px)`,
                  alignItems: "center",
                }}>
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 15, fontWeight: 700, color: N.red,
                  }}>
                    {a.abbr}
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 13, color: N.text,
                    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", paddingRight: 12,
                  }}>
                    {a.full}
                  </div>
                  <div><Pill text={a.cat} color={a.catColor} small /></div>
                  <div><Pill text={a.drill} color={a.drillColor} small /></div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 12,
                    color: a.mastery === "Mastered" ? TAG.green.text : a.mastery === "New" ? TAG.red.text : N.textDim,
                  }}>
                    {a.mastery}
                  </div>
                </div>
              );
            })}
          </div>

          <BottomBadge
            text="325+ acronyms loaded \u00B7 Spaced repetition built-in"
            opacity={interpolate(frame, [800, 815], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </AbsoluteFill>
      )}

      {/* ===== SCENE 6: PORT NUMBERS & PROTOCOLS ===== */}
      {frame >= 835 && frame < 1025 && (
        <AbsoluteFill style={{ opacity: s6, padding: "36px 80px" }}>
          <Breadcrumb
            parts={["Cyber-Squire OS", "Technical Reference", "Port Numbers"]}
            opacity={interpolate(frame, [843, 858], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
          <PageTitle
            icon={"\uD83D\uDD0C"}
            title="Port Numbers & Protocol Reference"
            opacity={interpolate(frame, [850, 865], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(15, 0, 850)}
          />

          <div style={{
            display: "flex", flexDirection: "column", gap: 10,
            opacity: interpolate(frame, [865, 878], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {PORTS.map((p, i) => {
              const pStart = 875 + i * 18;
              const pOp = interpolate(frame, [pStart, pStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const pX = sp(-50, 0, pStart, { damping: 16, stiffness: 120, mass: 0.4 });
              return (
                <div key={i} style={{
                  opacity: pOp,
                  transform: `translateX(${pX}px)`,
                  display: "flex", alignItems: "center", gap: 16,
                  padding: "13px 22px",
                  backgroundColor: N.sidebar,
                  borderRadius: 4,
                  border: `1px solid ${N.border}`,
                }}>
                  {/* Port number */}
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 26, fontWeight: 700, color: N.red,
                    width: 75, flexShrink: 0, textAlign: "right",
                  }}>
                    {frame >= pStart ? <CountUp target={p.port} startFrame={pStart} dur={15} /> : 0}
                  </div>
                  {/* Divider */}
                  <div style={{ width: 1, height: 32, backgroundColor: N.border, borderRadius: 1 }} />
                  {/* Protocol */}
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 17, fontWeight: 600, color: N.text,
                    width: 90, flexShrink: 0,
                  }}>
                    {p.proto}
                  </div>
                  {/* Use case */}
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 14, color: N.textDim,
                    flex: 1,
                  }}>
                    {p.use}
                  </div>
                  {/* Mastery status */}
                  <div style={{ width: 90, flexShrink: 0 }}>
                    <Pill text={p.mastery} color={p.mColor} />
                  </div>
                </div>
              );
            })}
          </div>

          <BottomBadge
            text="42 ports indexed \u00B7 SSH, HTTP, HTTPS, RDP, SNMP, Syslog, LDAP, DNS, and more"
            opacity={interpolate(frame, [985, 1000], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </AbsoluteFill>
      )}

      {/* ===== SCENE 7: STUDY ANALYTICS ===== */}
      {frame >= 1015 && frame < 1205 && (
        <AbsoluteFill style={{ opacity: s7, padding: "36px 80px" }}>
          <Breadcrumb
            parts={["Cyber-Squire OS", "Progress Tracking", "Study Analytics"]}
            opacity={interpolate(frame, [1023, 1038], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
          <PageTitle
            icon={"\uD83D\uDCCA"}
            title="Study Analytics"
            opacity={interpolate(frame, [1030, 1045], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(15, 0, 1030)}
          />

          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, marginTop: 8,
            opacity: interpolate(frame, [1040, 1055], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {METRICS.map((m, i) => {
              const mStart = 1050 + i * 18;
              const mOp = interpolate(frame, [mStart, mStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const barProg = interpolate(frame, [mStart + 6, mStart + 36], [0, (m.cur / m.max) * 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={i} style={{
                  opacity: mOp,
                  transform: `scale(${sp(0.95, 1, mStart, { damping: 14, stiffness: 120 })})`,
                  padding: "24px 28px",
                  backgroundColor: N.sidebar,
                  borderRadius: 6,
                  border: `1px solid ${N.border}`,
                  display: "flex", flexDirection: "column", gap: 14,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                    <div style={{ fontFamily: FONTS.body, fontSize: 15, color: N.textDim }}>
                      {m.label}
                    </div>
                    <div style={{ fontFamily: FONTS.body, fontSize: 26, fontWeight: 700, color: N.text }}>
                      <CountUp target={m.cur} startFrame={mStart} dur={25} />
                      <span style={{ fontSize: 15, color: N.textDim, fontWeight: 400 }}>/{m.max}</span>
                    </div>
                  </div>
                  <div style={{
                    height: 8, backgroundColor: N.border, borderRadius: 4, overflow: "hidden",
                  }}>
                    <div style={{
                      width: `${barProg}%`, height: "100%",
                      backgroundColor: TAG[m.color].text,
                      borderRadius: 4,
                    }} />
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 12, color: N.textDim, textAlign: "right",
                  }}>
                    {Math.round(barProg)}% complete
                  </div>
                </div>
              );
            })}
          </div>

          <BottomBadge
            text="Weekly Efficiency: 1.8 concepts/hour \u00B7 Auto-calculated"
            opacity={interpolate(frame, [1150, 1165], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </AbsoluteFill>
      )}

      {/* ===== SCENE 8: DOK FRAMEWORK ===== */}
      {frame >= 1195 && frame < 1355 && (
        <AbsoluteFill style={{ opacity: s8, justifyContent: "center", alignItems: "center", padding: "60px 100px" }}>
          <div style={{
            opacity: interpolate(frame, [1205, 1218], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: FONTS.body, fontSize: 20, color: N.textDim,
            textAlign: "center", marginBottom: 8, letterSpacing: 1,
          }}>
            Built on the
          </div>
          <div style={{
            opacity: interpolate(frame, [1212, 1228], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${sp(20, 0, 1212)}px)`,
            fontFamily: FONTS.body, fontSize: 44, fontWeight: 700, color: N.red,
            textAlign: "center", marginBottom: 40, letterSpacing: -0.5,
          }}>
            Depths of Knowledge Framework
          </div>

          <div style={{ display: "flex", gap: 18, width: "100%", maxWidth: 1200 }}>
            {DOK.map((d, i) => {
              const dStart = 1235 + i * 16;
              const dOp = interpolate(frame, [dStart, dStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const dX = sp(70, 0, dStart, { damping: 15, stiffness: 120, mass: 0.4 });
              return (
                <div key={i} style={{
                  flex: 1, opacity: dOp,
                  transform: `translateX(${dX}px)`,
                  padding: 22, borderRadius: 6,
                  backgroundColor: N.sidebar,
                  border: `1px solid ${N.border}`,
                  display: "flex", flexDirection: "column", gap: 10,
                }}>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 11, fontWeight: 600,
                    color: TAG[d.color].text, letterSpacing: 1.5, textTransform: "uppercase",
                  }}>
                    Level {d.n}
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 22, fontWeight: 700, color: TAG[d.color].text,
                  }}>
                    {d.name}
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 14, color: N.textDim, lineHeight: 1.5,
                  }}>
                    {d.desc}
                  </div>
                  <div style={{
                    height: 3, borderRadius: 2, marginTop: 6,
                    backgroundColor: TAG[d.color].bg,
                    overflow: "hidden",
                  }}>
                    <div style={{
                      width: "60%", height: "100%",
                      backgroundColor: TAG[d.color].text,
                      borderRadius: 2,
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 9: CTA — NO PRICE ===== */}
      {frame >= 1345 && (
        <AbsoluteFill style={{ opacity: s9, justifyContent: "center", alignItems: "center" }}>
          {/* Tagline */}
          <div style={{
            fontFamily: FONTS.body, fontSize: 20, color: N.textDim, letterSpacing: 3, marginBottom: 24,
            fontWeight: 500,
            opacity: interpolate(frame, [1358, 1373], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            STOP GUESSING. START STUDYING.
          </div>

          {/* CTA button */}
          <div style={{
            transform: `scale(${ctaScale * badgePulse})`,
            backgroundColor: N.red,
            borderRadius: 8, padding: "20px 56px",
            boxShadow: `0 0 ${badgeGlow}px ${N.red}66, 0 6px 24px rgba(0,0,0,0.4)`,
          }}>
            <div style={{
              fontFamily: FONTS.body, fontSize: 26, fontWeight: 700,
              color: N.white, letterSpacing: 1,
            }}>
              GET YOUR STUDY SYSTEM
            </div>
          </div>

          {/* URL */}
          <div style={{
            opacity: interpolate(frame, [1408, 1423], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: FONTS.body, fontSize: 15, color: N.textDim,
            marginTop: 28, letterSpacing: 1,
          }}>
            coredirective1.gumroad.com
          </div>

          {/* Benefits row */}
          <div style={{
            opacity: interpolate(frame, [1425, 1440], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            display: "flex", gap: 30, marginTop: 20, flexWrap: "wrap", justifyContent: "center",
          }}>
            {["10 Databases", "325+ Acronyms", "ADHD-Friendly", "Mobile Optimized", "7-Day Money Back"].map((pt, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <div style={{
                  width: 6, height: 6, borderRadius: 3,
                  backgroundColor: N.red,
                }} />
                <div style={{ fontFamily: FONTS.body, fontSize: 13, color: N.textDim }}>
                  {pt}
                </div>
              </div>
            ))}
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
