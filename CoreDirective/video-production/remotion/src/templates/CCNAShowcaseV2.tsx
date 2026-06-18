/**
 * CCNAShowcaseV2.tsx - CCNA 200-301 Study System product showcase (50s, 1920x1080)
 *
 * v2: Recreates actual Notion template UI with real data from the CCNA study system.
 * Dark/cinematic tech audio + gold theme.
 *
 * Scene timeline:
 *   0-5s     (0-150f):      Title reveal
 *   5-9s     (130-280f):    Stats counter (10 DBs, 30+ Views, 68 Days)
 *   9-17s    (260-520f):    Exam Readiness Tracker (Notion table)
 *   17-23s   (500-690f):    Knowledge Base (Kanban board)
 *   23-29s   (670-870f):    Command Line Grimoire (terminal)
 *   29-35s   (850-1060f):   Accountability Matrix (timeline)
 *   35-41s   (1040-1240f):  Study Analytics (dashboard)
 *   41-46s   (1220-1370f):  DoK Framework (4 levels)
 *   46-50s   (1350-1500f):  CTA + pricing
 */

import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  Audio,
  staticFile,
} from "remotion";
import { MatrixRain } from "../components/MatrixRain";
import { TerminalText } from "../components/TerminalText";
import { FONTS } from "../data/brand";

// ============================================================
// THEME
// ============================================================

const G = {
  bg: "#0D1117",
  accent: "#D4A843",
  accentBright: "#F0C94D",
  border: "#1C2333",
  cardBg: "rgba(13, 17, 23, 0.95)",
  headerBg: "#161B22",
  rowBorder: "#21262D",
  text: "#FFFFFF",
  textDim: "rgba(255, 255, 255, 0.55)",
  textMuted: "rgba(255, 255, 255, 0.3)",
} as const;

const TAG = {
  blue:   { bg: "#1E3A5F", text: "#6CB6FF" },
  green:  { bg: "#1E3F2E", text: "#56D364" },
  yellow: { bg: "#3F3A1E", text: "#D9B44A" },
  orange: { bg: "#3F2E1E", text: "#D98B4A" },
  red:    { bg: "#3F1E1E", text: "#F85149" },
  purple: { bg: "#2E1E4A", text: "#BC8CFF" },
  pink:   { bg: "#3F1E33", text: "#F778BA" },
} as const;

type TagColor = keyof typeof TAG;

// ============================================================
// SCENE DATA
// ============================================================

const EXAM_ROWS = [
  { obj: "1.6 - Configure IPv4 addressing & subnetting", domain: "Network Fundamentals", domainColor: "blue" as TagColor, conf: 4, level: "Application", lvlColor: "red" as TagColor, priority: 85 },
  { obj: "2.1 - Configure VLANs spanning switches", domain: "Network Access", domainColor: "purple" as TagColor, conf: 3, level: "Analysis", lvlColor: "orange" as TagColor, priority: 72 },
  { obj: "4.4 - Explain SNMP in network ops", domain: "IP Services", domainColor: "green" as TagColor, conf: 2, level: "Concept", lvlColor: "yellow" as TagColor, priority: 90 },
  { obj: "6.2 - Controller-based networking", domain: "Automation", domainColor: "orange" as TagColor, conf: 1, level: "Recall", lvlColor: "green" as TagColor, priority: 95 },
  { obj: "4.8 - Configure SSH remote access", domain: "IP Services", domainColor: "green" as TagColor, conf: 3, level: "Analysis", lvlColor: "orange" as TagColor, priority: 68 },
];

const KB_COLS = [
  { name: "Networking", color: "blue" as TagColor, cards: ["VLANs & Trunking", "IPv4 Subnetting", "OSPF Routing", "STP & EtherChannel"] },
  { name: "Security", color: "red" as TagColor, cards: ["ACLs", "Port Security", "DHCP Snooping"] },
  { name: "Automation", color: "orange" as TagColor, cards: ["Ansible", "Terraform", "REST APIs"] },
];

const CMDS = [
  { cmd: "# show ip route", topic: "OSPF", color: "pink" as TagColor },
  { cmd: "(config)# interface VLAN 23", topic: "VLANs", color: "blue" as TagColor },
  { cmd: "# show ip ospf neighbor", topic: "OSPF", color: "pink" as TagColor },
  { cmd: "(config-if)# switchport trunk allowed vlan 10,20,30", topic: "VLANs", color: "blue" as TagColor },
  { cmd: "# show ip access-lists", topic: "ACLs", color: "orange" as TagColor },
];

const DAYS = [
  { day: "Day 01", topic: "Network Devices", status: "Mastered", sColor: "green" as TagColor, progress: 100 },
  { day: "Day 13", topic: "Subnetting", status: "Applied", sColor: "blue" as TagColor, progress: 75 },
  { day: "Day 16", topic: "VLANs", status: "Immersion", sColor: "yellow" as TagColor, progress: 50 },
  { day: "Day 26", topic: "OSPF", status: "Not Started", sColor: "red" as TagColor, progress: 0 },
  { day: "Day 48", topic: "Security", status: "Not Started", sColor: "red" as TagColor, progress: 0 },
  { day: "Day 63", topic: "Terraform", status: "Not Started", sColor: "red" as TagColor, progress: 0 },
];

const METRICS = [
  { label: "Study Hours", cur: 24, max: 40, color: "blue" as TagColor },
  { label: "Concepts Mastered", cur: 15, max: 30, color: "green" as TagColor },
  { label: "Labs Completed", cur: 8, max: 20, color: "purple" as TagColor },
  { label: "Commands Learned", cur: 45, max: 50, color: "orange" as TagColor },
];

const DOK = [
  { n: 1, name: "Recall", desc: "Remember facts & definitions", bg: "#1A2E22", tc: "#56D364" },
  { n: 2, name: "Concept", desc: "Explain & apply concepts", bg: "#2E2E1A", tc: "#D9D34A" },
  { n: 3, name: "Analysis", desc: "Analyze & troubleshoot", bg: "#2E221A", tc: "#D98B4A" },
  { n: 4, name: "Application", desc: "Design & architect solutions", bg: "#2E1A1A", tc: "#F85149" },
];

// ============================================================
// HELPERS
// ============================================================

/** Animated number counter with eased counting */
const CountUp: React.FC<{ target: number; suffix?: string; startFrame: number; dur?: number }> = ({
  target, suffix = "", startFrame, dur = 30,
}) => {
  const frame = useCurrentFrame();
  const p = Math.min(Math.max(0, frame - startFrame) / dur, 1);
  return <>{Math.round(target * (1 - Math.pow(1 - p, 3)))}{suffix}</>;
};

/** Notion-style colored tag pill */
const Pill: React.FC<{ text: string; color: TagColor; small?: boolean }> = ({ text, color, small }) => (
  <div style={{
    display: "inline-flex",
    padding: small ? "2px 8px" : "3px 10px",
    borderRadius: 4,
    backgroundColor: TAG[color].bg,
    color: TAG[color].text,
    fontFamily: FONTS.mono,
    fontSize: small ? 11 : 13,
    fontWeight: 500,
    whiteSpace: "nowrap",
  }}>
    {text}
  </div>
);

/** Scene section title with icon */
const SectionTitle: React.FC<{
  icon: string; title: string; subtitle?: string; opacity: number; slideY?: number;
}> = ({ icon, title, subtitle, opacity, slideY = 0 }) => (
  <div style={{
    opacity,
    transform: `translateY(${slideY}px)`,
    display: "flex",
    alignItems: "center",
    gap: 14,
    marginBottom: 20,
  }}>
    <span style={{ fontSize: 28 }}>{icon}</span>
    <div>
      <div style={{ fontFamily: FONTS.mono, fontSize: 24, fontWeight: 700, color: G.text, letterSpacing: 1 }}>
        {title}
      </div>
      {subtitle && (
        <div style={{ fontFamily: FONTS.mono, fontSize: 13, color: G.textDim, letterSpacing: 2, marginTop: 2 }}>
          {subtitle}
        </div>
      )}
    </div>
  </div>
);

/** Notion-style view tabs */
const ViewTabs: React.FC<{ tabs: string[]; active: number; opacity: number }> = ({ tabs, active, opacity }) => (
  <div style={{ opacity, display: "flex", gap: 0, marginBottom: 16, borderBottom: `1px solid ${G.rowBorder}` }}>
    {tabs.map((tab, i) => (
      <div key={i} style={{
        padding: "8px 16px",
        fontFamily: FONTS.body,
        fontSize: 13,
        color: i === active ? G.accent : G.textMuted,
        borderBottom: i === active ? `2px solid ${G.accent}` : "2px solid transparent",
        cursor: "default",
      }}>
        {tab}
      </div>
    ))}
  </div>
);

// ============================================================
// MAIN COMPONENT
// ============================================================

export const CCNAShowcaseV2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene fade helper
  const sceneFade = (start: number, end: number, fadeIn = 20, fadeOut = 20) => {
    const fi = fadeIn > 0
      ? interpolate(frame, [start, start + fadeIn], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
      : frame >= start ? 1 : 0;
    const fo = fadeOut > 0
      ? interpolate(frame, [end - fadeOut, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
      : 1;
    return fi * fo;
  };

  // Spring shorthand
  const sp = (from: number, to: number, startFrame: number, config?: object) =>
    spring({ frame: frame - startFrame, fps, config: { damping: 14, stiffness: 100, mass: 0.6, ...config }, from, to });

  // ============================================================
  // SCENE 1: TITLE (0-150)
  // ============================================================
  const s1 = sceneFade(0, 150, 10, 20);

  const ccnaScale = sp(3, 1, 10, { damping: 10, stiffness: 150, mass: 0.6 });
  const ccnaOp = interpolate(frame, [10, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const codeOp = interpolate(frame, [35, 55], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const codeY = sp(30, 0, 35, { damping: 15, stiffness: 100, mass: 0.5 });
  const studyOp = interpolate(frame, [55, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const tagOp = interpolate(frame, [85, 100], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // ============================================================
  // SCENE 2: STATS (130-280)
  // ============================================================
  const s2 = sceneFade(130, 280);

  const stats = [
    { num: 10, label: "Databases", suffix: "" },
    { num: 30, label: "Custom Views", suffix: "+" },
    { num: 68, label: "Study Days", suffix: "" },
  ];

  // ============================================================
  // SCENE 3: EXAM READINESS (260-520)
  // ============================================================
  const s3 = sceneFade(260, 520);

  // Row stagger: each row appears 18 frames apart starting at frame 300
  const examRowAnims = EXAM_ROWS.map((_, i) => {
    const rs = 300 + i * 18;
    return {
      opacity: interpolate(frame, [rs, rs + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      slideX: sp(40, 0, rs, { damping: 16, stiffness: 120, mass: 0.4 }),
      startFrame: rs,
    };
  });

  // Cursor highlight: moves between rows
  const highlightRow = frame < 400 ? -1 : frame < 440 ? 2 : frame < 480 ? 0 : frame < 510 ? 3 : -1;

  // ============================================================
  // SCENE 4: KNOWLEDGE BASE (500-690)
  // ============================================================
  const s4 = sceneFade(500, 690);

  // ============================================================
  // SCENE 5: COMMAND GRIMOIRE (670-870)
  // ============================================================
  const s5 = sceneFade(670, 870);

  // ============================================================
  // SCENE 6: ACCOUNTABILITY (850-1060)
  // ============================================================
  const s6 = sceneFade(850, 1060);

  // ============================================================
  // SCENE 7: ANALYTICS (1040-1240)
  // ============================================================
  const s7 = sceneFade(1040, 1240);

  // ============================================================
  // SCENE 8: DOK (1220-1370)
  // ============================================================
  const s8 = sceneFade(1220, 1370);

  // ============================================================
  // SCENE 9: CTA (1350-1500)
  // ============================================================
  const s9 = sceneFade(1350, 1500, 20, 0); // no fade out at the very end

  const ctaScale = sp(0.7, 1, 1370, { damping: 10, stiffness: 120 });
  const badgePulse = interpolate(Math.sin((frame - 1400) * 0.08), [-1, 1], [0.95, 1.05]);
  const badgeGlow = frame > 1400 ? interpolate(Math.sin((frame - 1400) * 0.1), [-1, 1], [10, 35]) : 0;

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <AbsoluteFill style={{ backgroundColor: G.bg, overflow: "hidden" }}>
      {/* ===== BACKGROUND ===== */}
      <MatrixRain opacity={0.04} color={G.accent} speed={0.35} />
      <AbsoluteFill style={{
        background: "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.02) 3px, rgba(0,0,0,0.02) 4px)",
        pointerEvents: "none",
      }} />

      {/* ===== AUDIO ===== */}
      <Audio
        src={staticFile("audio/bg-dark-tech.mp3")}
        volume={(f) => interpolate(f, [0, 90, 1380, 1500], [0, 0.25, 0.25, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {/* Whoosh on scene transitions */}
      {[130, 260, 500, 670, 850, 1040, 1220, 1350].map((f, i) => (
        <Sequence key={`w${i}`} from={f} durationInFrames={18}>
          <Audio src={staticFile("audio/whoosh.mp3")} volume={0.45} />
        </Sequence>
      ))}
      {/* Typing sound during Command Grimoire */}
      <Sequence from={700} durationInFrames={150}>
        <Audio src={staticFile("audio/typing.mp3")} volume={0.3} loop />
      </Sequence>
      {/* Click sounds on row highlights */}
      {[400, 440, 480].map((f, i) => (
        <Sequence key={`c${i}`} from={f} durationInFrames={6}>
          <Audio src={staticFile("audio/click.mp3")} volume={0.4} />
        </Sequence>
      ))}
      {/* Reveal impact on CTA */}
      <Sequence from={1365} durationInFrames={36}>
        <Audio src={staticFile("audio/reveal.mp3")} volume={0.6} />
      </Sequence>

      {/* ===== SCENE 1: TITLE ===== */}
      {frame < 155 && (
        <AbsoluteFill style={{ opacity: s1, justifyContent: "center", alignItems: "center" }}>
          <div style={{
            opacity: ccnaOp,
            transform: `scale(${ccnaScale})`,
            fontFamily: FONTS.mono, fontSize: 180, fontWeight: 700,
            color: G.text, textAlign: "center", letterSpacing: 20,
            textShadow: `0 0 60px ${G.accent}44`,
          }}>
            CCNA
          </div>
          <div style={{
            opacity: codeOp,
            transform: `translateY(${codeY}px)`,
            fontFamily: FONTS.mono, fontSize: 72, fontWeight: 700,
            color: G.accent, textAlign: "center", letterSpacing: 8, marginTop: -10,
          }}>
            200-301
          </div>
          <div style={{ opacity: studyOp, marginTop: 20 }}>
            <TerminalText text="STUDY SYSTEM" startFrame={55} speed={1.2} fontSize={44} color={G.textDim} cursorColor={G.accent} showCursor={frame < 100} />
          </div>
          <div style={{
            opacity: tagOp,
            fontFamily: FONTS.mono, fontSize: 24, color: G.accent,
            marginTop: 30, letterSpacing: 3,
          }}>
            {"// NOTION TEMPLATE"}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 2: STATS ===== */}
      {frame >= 125 && frame < 285 && (
        <AbsoluteFill style={{ opacity: s2, justifyContent: "center", alignItems: "center" }}>
          <div style={{
            fontFamily: FONTS.mono, fontSize: 16, color: G.textDim,
            letterSpacing: 6, textTransform: "uppercase", marginBottom: 50,
            opacity: interpolate(frame, [140, 155], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            Your Complete Study System
          </div>
          <div style={{ display: "flex", gap: 80, alignItems: "center" }}>
            {stats.map((s, i) => {
              const start = 155 + i * 25;
              const op = interpolate(frame, [start, start + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const sc = sp(0.5, 1, start, { damping: 12, stiffness: 150, mass: 0.4 });
              return (
                <div key={i} style={{
                  opacity: op, transform: `scale(${sc})`,
                  display: "flex", flexDirection: "column", alignItems: "center", gap: 10,
                }}>
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 80, fontWeight: 700, color: G.accent, lineHeight: 1,
                  }}>
                    <CountUp target={s.num} suffix={s.suffix} startFrame={start} dur={30} />
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 22, color: G.text, letterSpacing: 1,
                  }}>
                    {s.label}
                  </div>
                  <div style={{ width: 60, height: 2, backgroundColor: G.accent, opacity: 0.4, borderRadius: 1 }} />
                </div>
              );
            })}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 3: EXAM READINESS TRACKER ===== */}
      {frame >= 255 && frame < 525 && (
        <AbsoluteFill style={{ opacity: s3, padding: "60px 100px" }}>
          <SectionTitle
            icon="🎯"
            title="Exam Readiness Tracker"
            subtitle="22 PROPERTIES  ·  5 VIEWS  ·  AUTO-CALCULATED PRIORITY"
            opacity={interpolate(frame, [265, 280], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(20, 0, 265)}
          />
          <ViewTabs
            tabs={["Full View", "Today's Focus", "Weak Areas", "Exam Ready"]}
            active={1}
            opacity={interpolate(frame, [275, 290], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />

          {/* Table */}
          <div style={{
            borderRadius: 8,
            border: `1px solid ${G.rowBorder}`,
            overflow: "hidden",
            opacity: interpolate(frame, [280, 295], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {/* Header */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "2.5fr 1.2fr 0.6fr 1fr 0.6fr",
              backgroundColor: G.headerBg,
              padding: "10px 16px",
              borderBottom: `1px solid ${G.rowBorder}`,
            }}>
              {["Objective", "Domain", "Conf.", "Action Level", "Priority"].map((h) => (
                <div key={h} style={{
                  fontFamily: FONTS.mono, fontSize: 12, fontWeight: 600,
                  color: G.textMuted, letterSpacing: 1, textTransform: "uppercase",
                }}>
                  {h}
                </div>
              ))}
            </div>

            {/* Rows */}
            {EXAM_ROWS.map((row, i) => (
              <div key={i} style={{
                display: "grid",
                gridTemplateColumns: "2.5fr 1.2fr 0.6fr 1fr 0.6fr",
                padding: "12px 16px",
                borderBottom: i < EXAM_ROWS.length - 1 ? `1px solid ${G.rowBorder}` : "none",
                backgroundColor: highlightRow === i ? `rgba(212, 168, 67, 0.08)` : "transparent",
                borderLeft: highlightRow === i ? `3px solid ${G.accent}` : "3px solid transparent",
                opacity: examRowAnims[i].opacity,
                transform: `translateX(${examRowAnims[i].slideX}px)`,
                alignItems: "center",
                transition: "background-color 0.1s",
              }}>
                <div style={{ fontFamily: FONTS.body, fontSize: 14, color: G.text, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", paddingRight: 12 }}>
                  {row.obj}
                </div>
                <div><Pill text={row.domain} color={row.domainColor} small /></div>
                <div style={{ fontFamily: FONTS.mono, fontSize: 16, fontWeight: 700, color: row.conf >= 3 ? TAG.green.text : row.conf >= 2 ? TAG.yellow.text : TAG.red.text }}>
                  {frame >= examRowAnims[i].startFrame ? <CountUp target={row.conf} startFrame={examRowAnims[i].startFrame} dur={15} /> : 0}
                </div>
                <div><Pill text={row.level} color={row.lvlColor} small /></div>
                <div style={{ fontFamily: FONTS.mono, fontSize: 14, color: G.textDim }}>
                  {frame >= examRowAnims[i].startFrame ? <CountUp target={row.priority} startFrame={examRowAnims[i].startFrame} dur={20} /> : 0}
                </div>
              </div>
            ))}
          </div>

          {/* Filter indicator */}
          <div style={{
            marginTop: 14,
            display: "flex", gap: 10, alignItems: "center",
            opacity: interpolate(frame, [380, 395], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            <div style={{
              padding: "4px 12px", borderRadius: 4,
              backgroundColor: `${G.accent}18`, border: `1px solid ${G.accent}33`,
              fontFamily: FONTS.mono, fontSize: 12, color: G.accent,
            }}>
              Filter: Confidence {"<"} 3
            </div>
            <div style={{
              padding: "4px 12px", borderRadius: 4,
              backgroundColor: `${G.accent}18`, border: `1px solid ${G.accent}33`,
              fontFamily: FONTS.mono, fontSize: 12, color: G.accent,
            }}>
              Sort: Priority Score ↓
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 4: KNOWLEDGE BASE (KANBAN) ===== */}
      {frame >= 495 && frame < 695 && (
        <AbsoluteFill style={{ opacity: s4, padding: "60px 100px" }}>
          <SectionTitle
            icon="📘"
            title="Knowledge Base"
            subtitle="17 PROPERTIES  ·  9 VIEWS  ·  AUTO-PRIORITIZED STUDY"
            opacity={interpolate(frame, [505, 520], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(20, 0, 505)}
          />
          <ViewTabs
            tabs={["All", "By Category", "Study Next", "Mastered"]}
            active={1}
            opacity={interpolate(frame, [515, 530], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />

          {/* Kanban Board */}
          <div style={{
            display: "flex", gap: 20, flex: 1,
            opacity: interpolate(frame, [520, 535], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {KB_COLS.map((col, ci) => {
              const colStart = 530 + ci * 20;
              const colOp = interpolate(frame, [colStart, colStart + 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={ci} style={{
                  flex: 1, opacity: colOp,
                  display: "flex", flexDirection: "column", gap: 10,
                }}>
                  {/* Column header */}
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "8px 12px", marginBottom: 4,
                  }}>
                    <div style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: TAG[col.color].text }} />
                    <div style={{ fontFamily: FONTS.mono, fontSize: 14, fontWeight: 600, color: G.text }}>
                      {col.name}
                    </div>
                    <div style={{
                      fontFamily: FONTS.mono, fontSize: 12, color: G.textMuted,
                      backgroundColor: G.headerBg, borderRadius: 4, padding: "2px 6px",
                    }}>
                      {col.cards.length}
                    </div>
                  </div>

                  {/* Cards */}
                  {col.cards.map((card, ki) => {
                    const cardStart = colStart + 15 + ki * 12;
                    const cardOp = interpolate(frame, [cardStart, cardStart + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                    const cardY = sp(30, 0, cardStart, { damping: 18, stiffness: 130, mass: 0.3 });
                    return (
                      <div key={ki} style={{
                        opacity: cardOp,
                        transform: `translateY(${cardY}px)`,
                        backgroundColor: G.headerBg,
                        border: `1px solid ${G.rowBorder}`,
                        borderRadius: 6,
                        padding: "14px 16px",
                        display: "flex", flexDirection: "column", gap: 8,
                      }}>
                        <div style={{ fontFamily: FONTS.body, fontSize: 14, color: G.text, fontWeight: 500 }}>
                          {card}
                        </div>
                        <div style={{ display: "flex", gap: 6 }}>
                          <Pill text="CCNA" color={col.color} small />
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

      {/* ===== SCENE 5: COMMAND LINE GRIMOIRE ===== */}
      {frame >= 665 && frame < 875 && (
        <AbsoluteFill style={{ opacity: s5, padding: "60px 100px" }}>
          <SectionTitle
            icon="📜"
            title="Command Line Grimoire"
            subtitle="50+ CISCO IOS COMMANDS  ·  21 TOPICS  ·  LAB-READY"
            opacity={interpolate(frame, [675, 690], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(20, 0, 675)}
          />

          {/* Terminal window */}
          <div style={{
            borderRadius: 10,
            border: `1px solid ${G.rowBorder}`,
            overflow: "hidden",
            opacity: interpolate(frame, [685, 700], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${sp(20, 0, 685)}px)`,
          }}>
            {/* Terminal title bar */}
            <div style={{
              backgroundColor: "#1A1E24",
              padding: "10px 16px",
              display: "flex", alignItems: "center", gap: 8,
              borderBottom: `1px solid ${G.rowBorder}`,
            }}>
              <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#FF5F57" }} />
              <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#FEBC2E" }} />
              <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#28C840" }} />
              <div style={{ fontFamily: FONTS.mono, fontSize: 12, color: G.textMuted, marginLeft: 12 }}>
                Cisco IOS — Command Reference
              </div>
            </div>

            {/* Command lines */}
            <div style={{ backgroundColor: "#0D1117", padding: "20px 24px" }}>
              {CMDS.map((c, i) => {
                const cmdStart = 705 + i * 28;
                const lineOp = interpolate(frame, [cmdStart, cmdStart + 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
                return (
                  <div key={i} style={{
                    opacity: lineOp,
                    display: "flex", alignItems: "center", gap: 16,
                    padding: "10px 0",
                    borderBottom: i < CMDS.length - 1 ? `1px solid ${G.rowBorder}` : "none",
                  }}>
                    <div style={{ fontFamily: FONTS.mono, fontSize: 13, color: G.textMuted, width: 30, textAlign: "right" }}>
                      {i + 1}
                    </div>
                    <div style={{ fontFamily: FONTS.mono, fontSize: 15, color: G.accent, flex: 1 }}>
                      {frame >= cmdStart ? (
                        <TerminalText
                          text={c.cmd}
                          startFrame={cmdStart}
                          speed={2}
                          fontSize={15}
                          color={G.accent}
                          cursorColor={G.accentBright}
                          showCursor={frame < cmdStart + Math.ceil(c.cmd.length / 2) + 10}
                        />
                      ) : null}
                    </div>
                    <div style={{ opacity: interpolate(frame, [cmdStart + 15, cmdStart + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
                      <Pill text={c.topic} color={c.color} small />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom status bar */}
            <div style={{
              backgroundColor: "#1A1E24",
              padding: "6px 16px",
              display: "flex", justifyContent: "space-between",
              borderTop: `1px solid ${G.rowBorder}`,
            }}>
              <div style={{ fontFamily: FONTS.mono, fontSize: 11, color: G.textMuted }}>
                Platform: Cisco IOS
              </div>
              <div style={{ fontFamily: FONTS.mono, fontSize: 11, color: G.textMuted }}>
                50+ commands indexed
              </div>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 6: ACCOUNTABILITY MATRIX ===== */}
      {frame >= 845 && frame < 1065 && (
        <AbsoluteFill style={{ opacity: s6, padding: "60px 100px" }}>
          <SectionTitle
            icon="⚔️"
            title="Accountability Matrix"
            subtitle="68 DAYS  ·  19 PROPERTIES  ·  4-CHECKPOINT MASTERY"
            opacity={interpolate(frame, [855, 870], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(20, 0, 855)}
          />

          {/* Timeline */}
          <div style={{
            display: "flex", flexDirection: "column", gap: 12,
            opacity: interpolate(frame, [870, 885], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {DAYS.map((d, i) => {
              const dayStart = 880 + i * 20;
              const dayOp = interpolate(frame, [dayStart, dayStart + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const dayX = sp(-60, 0, dayStart, { damping: 16, stiffness: 120, mass: 0.4 });
              const barWidth = interpolate(frame, [dayStart + 10, dayStart + 35], [0, d.progress], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={i} style={{
                  opacity: dayOp,
                  transform: `translateX(${dayX}px)`,
                  display: "flex", alignItems: "center", gap: 16,
                  padding: "12px 20px",
                  backgroundColor: G.headerBg,
                  borderRadius: 8,
                  border: `1px solid ${G.rowBorder}`,
                }}>
                  {/* Day badge */}
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 13, fontWeight: 700, color: G.accent,
                    width: 60, flexShrink: 0,
                  }}>
                    {d.day}
                  </div>
                  {/* Topic */}
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 15, color: G.text,
                    width: 180, flexShrink: 0,
                  }}>
                    {d.topic}
                  </div>
                  {/* Progress bar */}
                  <div style={{
                    flex: 1, height: 8, backgroundColor: G.rowBorder, borderRadius: 4, overflow: "hidden",
                  }}>
                    <div style={{
                      width: `${barWidth}%`, height: "100%",
                      backgroundColor: TAG[d.sColor].text,
                      borderRadius: 4,
                      boxShadow: d.progress > 0 ? `0 0 8px ${TAG[d.sColor].text}44` : "none",
                    }} />
                  </div>
                  {/* Status */}
                  <div style={{ width: 120, flexShrink: 0 }}>
                    <Pill text={d.status} color={d.sColor} small />
                  </div>
                  {/* Checkmarks */}
                  <div style={{ display: "flex", gap: 8 }}>
                    {d.progress === 100 ? (
                      <>
                        <span style={{ fontSize: 14, opacity: 0.8 }}>✅</span>
                        <span style={{ fontSize: 14, opacity: 0.8 }}>✅</span>
                      </>
                    ) : (
                      <>
                        <span style={{ fontSize: 14, opacity: 0.3 }}>☐</span>
                        <span style={{ fontSize: 14, opacity: 0.3 }}>☐</span>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Mastery standard callout */}
          <div style={{
            marginTop: 20,
            padding: "12px 20px",
            borderRadius: 8,
            backgroundColor: `${G.accent}0A`,
            border: `1px solid ${G.accent}22`,
            display: "flex", alignItems: "center", gap: 12,
            opacity: interpolate(frame, [1000, 1015], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            <span style={{ fontSize: 18 }}>🏆</span>
            <div style={{ fontFamily: FONTS.mono, fontSize: 13, color: G.accent }}>
              Mastery Standard: Anki Clear + Blank-Slate Lab + Logic Gap Documented + Status = Mastered
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 7: STUDY ANALYTICS ===== */}
      {frame >= 1035 && frame < 1245 && (
        <AbsoluteFill style={{ opacity: s7, padding: "60px 100px" }}>
          <SectionTitle
            icon="📊"
            title="Study Analytics"
            subtitle="WEEKLY ROLLUP  ·  AUTO-AGGREGATED FROM ALL DATABASES"
            opacity={interpolate(frame, [1045, 1060], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            slideY={sp(20, 0, 1045)}
          />

          {/* Dashboard cards */}
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 10,
            opacity: interpolate(frame, [1060, 1075], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            {METRICS.map((m, i) => {
              const mStart = 1070 + i * 20;
              const mOp = interpolate(frame, [mStart, mStart + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const barProg = interpolate(frame, [mStart + 8, mStart + 40], [0, (m.cur / m.max) * 100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return (
                <div key={i} style={{
                  opacity: mOp,
                  transform: `scale(${sp(0.9, 1, mStart, { damping: 14, stiffness: 120 })})`,
                  padding: "28px 30px",
                  backgroundColor: G.headerBg,
                  borderRadius: 12,
                  border: `1px solid ${G.rowBorder}`,
                  display: "flex", flexDirection: "column", gap: 16,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                    <div style={{ fontFamily: FONTS.body, fontSize: 16, color: G.textDim }}>
                      {m.label}
                    </div>
                    <div style={{ fontFamily: FONTS.mono, fontSize: 28, fontWeight: 700, color: G.text }}>
                      <CountUp target={m.cur} startFrame={mStart} dur={25} />
                      <span style={{ fontSize: 16, color: G.textMuted }}>/{m.max}</span>
                    </div>
                  </div>
                  {/* Bar */}
                  <div style={{
                    height: 10, backgroundColor: G.rowBorder, borderRadius: 5, overflow: "hidden",
                  }}>
                    <div style={{
                      width: `${barProg}%`, height: "100%",
                      backgroundColor: TAG[m.color].text,
                      borderRadius: 5,
                      boxShadow: `0 0 12px ${TAG[m.color].text}44`,
                    }} />
                  </div>
                  <div style={{ fontFamily: FONTS.mono, fontSize: 12, color: G.textMuted, textAlign: "right" }}>
                    {Math.round(barProg)}% complete
                  </div>
                </div>
              );
            })}
          </div>

          {/* Weekly efficiency badge */}
          <div style={{
            marginTop: 20, display: "flex", justifyContent: "center",
            opacity: interpolate(frame, [1160, 1175], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            <div style={{
              padding: "10px 24px", borderRadius: 8,
              backgroundColor: `${G.accent}12`, border: `1px solid ${G.accent}33`,
              fontFamily: FONTS.mono, fontSize: 14, color: G.accent,
            }}>
              Weekly Efficiency: 1.6 concepts/hour · Auto-calculated
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 8: DOK FRAMEWORK ===== */}
      {frame >= 1215 && frame < 1375 && (
        <AbsoluteFill style={{ opacity: s8, justifyContent: "center", alignItems: "center", padding: 100 }}>
          <div style={{
            opacity: interpolate(frame, [1225, 1240], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: FONTS.body, fontSize: 22, color: G.textDim,
            textAlign: "center", marginBottom: 8, letterSpacing: 2,
          }}>
            Built on the
          </div>
          <div style={{
            opacity: interpolate(frame, [1235, 1250], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            transform: `translateY(${sp(25, 0, 1235)}px)`,
            fontFamily: FONTS.mono, fontSize: 48, fontWeight: 700, color: G.accent,
            textAlign: "center", marginBottom: 45, textShadow: `0 0 30px ${G.accent}33`,
          }}>
            Depths of Knowledge Framework
          </div>

          <div style={{ display: "flex", gap: 20, width: "100%", maxWidth: 1200 }}>
            {DOK.map((d, i) => {
              const dStart = 1255 + i * 18;
              const dOp = interpolate(frame, [dStart, dStart + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              const dX = sp(80, 0, dStart, { damping: 15, stiffness: 120, mass: 0.4 });
              return (
                <div key={i} style={{
                  flex: 1, opacity: dOp,
                  transform: `translateX(${dX}px)`,
                  padding: 24, borderRadius: 12,
                  backgroundColor: d.bg,
                  border: `1px solid ${d.tc}33`,
                  display: "flex", flexDirection: "column", gap: 10,
                }}>
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 12, color: d.tc, letterSpacing: 2, opacity: 0.8,
                  }}>
                    LEVEL {d.n}
                  </div>
                  <div style={{
                    fontFamily: FONTS.mono, fontSize: 24, fontWeight: 700, color: d.tc,
                  }}>
                    {d.name}
                  </div>
                  <div style={{
                    fontFamily: FONTS.body, fontSize: 14, color: G.textDim, lineHeight: 1.5,
                  }}>
                    {d.desc}
                  </div>
                  <div style={{
                    height: 3, borderRadius: 2, marginTop: 6,
                    background: `linear-gradient(90deg, ${d.tc}, transparent)`,
                    opacity: 0.6,
                  }} />
                </div>
              );
            })}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== SCENE 9: CTA ===== */}
      {frame >= 1345 && (
        <AbsoluteFill style={{ opacity: s9, justifyContent: "center", alignItems: "center" }}>
          {/* Price */}
          <div style={{
            fontFamily: FONTS.mono, fontSize: 22, color: G.textDim, letterSpacing: 3, marginBottom: 12,
            opacity: interpolate(frame, [1360, 1375], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}>
            PAY WHAT YOU WANT · SUGGESTED
          </div>
          <div style={{
            fontFamily: FONTS.mono, fontSize: 72, fontWeight: 700, color: G.accent, marginBottom: 20,
            opacity: interpolate(frame, [1365, 1380], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            textShadow: `0 0 40px ${G.accent}44`,
          }}>
            $39.99
          </div>

          {/* CTA button */}
          <div style={{
            transform: `scale(${ctaScale * badgePulse})`,
            backgroundColor: G.accent,
            borderRadius: 14, padding: "20px 60px",
            boxShadow: `0 0 ${badgeGlow}px ${G.accent}88, 0 8px 30px rgba(0,0,0,0.5)`,
          }}>
            <div style={{
              fontFamily: FONTS.mono, fontSize: 26, fontWeight: 700,
              color: G.bg, letterSpacing: 2,
            }}>
              GET YOUR STUDY SYSTEM
            </div>
          </div>

          {/* URL */}
          <div style={{
            opacity: interpolate(frame, [1410, 1425], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            fontFamily: FONTS.mono, fontSize: 16, color: G.textDim,
            marginTop: 30, letterSpacing: 2,
          }}>
            coredirective1.gumroad.com
          </div>

          {/* Benefits row */}
          <div style={{
            opacity: interpolate(frame, [1430, 1445], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            display: "flex", gap: 35, marginTop: 20,
          }}>
            {["10 Databases", "ADHD-Friendly", "Mobile Optimized", "Lifetime Updates", "7-Day Money Back"].map((pt, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{
                  width: 7, height: 7, borderRadius: 4,
                  backgroundColor: G.accent,
                }} />
                <div style={{ fontFamily: FONTS.body, fontSize: 14, color: G.textDim }}>
                  {pt}
                </div>
              </div>
            ))}
          </div>
        </AbsoluteFill>
      )}

      {/* ===== CORNER BRACKETS ===== */}
      <div style={{
        position: "absolute", top: 30, left: 30,
        width: 50, height: 50,
        borderTop: `2px solid ${G.accent}33`,
        borderLeft: `2px solid ${G.accent}33`,
      }} />
      <div style={{
        position: "absolute", bottom: 30, right: 30,
        width: 50, height: 50,
        borderBottom: `2px solid ${G.accent}33`,
        borderRight: `2px solid ${G.accent}33`,
      }} />
    </AbsoluteFill>
  );
};
