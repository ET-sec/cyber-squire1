/**
 * Root.tsx - Registers all Remotion compositions.
 *
 * Compositions:
 *   7  CertCard variants   (5s each, 1080x1920, 30fps)
 *   10 DidYouKnow variants (4s each, 1080x1920, 30fps)
 *   1  DebtTracker default  (6s, 1080x1920, 30fps)
 *   1  YouTubeIntro default (5s, 1920x1080, 30fps)
 *   = 19 total compositions
 */

import React from "react";
import { Composition } from "remotion";
import "./styles/fonts.css";

// Templates
import { CertCard } from "./templates/CertCard";
import { CCNAShowcase } from "./templates/CCNAShowcase";
import { CCNAShowcaseV2 } from "./templates/CCNAShowcaseV2";
import { SecPlusShowcase } from "./templates/SecPlusShowcase";
import { CertDebate } from "./templates/CertDebate";
import { DebtTracker } from "./templates/DebtTracker";
import { DidYouKnow } from "./templates/DidYouKnow";
import { YouTubeIntro } from "./templates/YouTubeIntro";

// Data & Schemas
import { CERTS } from "./data/certs";
import { FACTS } from "./data/facts";
import { VERTICAL, HORIZONTAL, FPS } from "./data/brand";
import {
  certCardSchema,
  ccnaShowcaseSchema,
  ccnaShowcaseV2Schema,
  secPlusShowcaseSchema,
  certDebateSchema,
  didYouKnowSchema,
  debtTrackerSchema,
  youtubeIntroSchema,
} from "./data/schemas";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* ===== CERT CARDS (7 compositions, 5 seconds each, vertical) ===== */}
      {CERTS.map((cert) => (
        <Composition
          key={cert.id}
          id={cert.id}
          schema={certCardSchema}
          component={CertCard}
          durationInFrames={FPS * 5}
          fps={FPS}
          width={VERTICAL.width}
          height={VERTICAL.height}
          defaultProps={{
            certName: cert.certName,
            certFullName: cert.certFullName,
            issuer: cert.issuer,
            passDate: cert.passDate,
            difficulty: cert.difficulty,
            factoids: cert.factoids,
            salaryImpact: cert.salaryImpact,
          }}
        />
      ))}

      {/* ===== DID YOU KNOW FACTS (10 compositions, 4 seconds each, vertical) ===== */}
      {FACTS.map((fact) => (
        <Composition
          key={fact.id}
          id={fact.id}
          schema={didYouKnowSchema}
          component={DidYouKnow}
          durationInFrames={FPS * 4}
          fps={FPS}
          width={VERTICAL.width}
          height={VERTICAL.height}
          defaultProps={{
            category: fact.category,
            fact: fact.fact,
            source: fact.source,
            callToAction: fact.callToAction,
          }}
        />
      ))}

      {/* ===== DEBT TRACKER (1 default composition, 6 seconds, vertical) ===== */}
      <Composition
        id="DebtTracker-Default"
        schema={debtTrackerSchema}
        component={DebtTracker}
        durationInFrames={FPS * 6}
        fps={FPS}
        width={VERTICAL.width}
        height={VERTICAL.height}
        defaultProps={{
          weekNumber: 1,
          startingDebt: 45000,
          currentDebt: 43750,
          weeklyIncome: 1250,
          incomeSource: "Cybersecurity Consulting",
          milestone: "Journey begins.",
        }}
      />

      {/* ===== CCNA SHOWCASE (1 composition, 35 seconds, landscape for Gumroad) ===== */}
      <Composition
        id="CCNAShowcase"
        schema={ccnaShowcaseSchema}
        component={CCNAShowcase}
        durationInFrames={FPS * 35}
        fps={FPS}
        width={HORIZONTAL.width}
        height={HORIZONTAL.height}
        defaultProps={{}}
      />

      {/* ===== CCNA SHOWCASE V2 (1 composition, 50 seconds, landscape for Gumroad) ===== */}
      <Composition
        id="CCNAShowcaseV2"
        schema={ccnaShowcaseV2Schema}
        component={CCNAShowcaseV2}
        durationInFrames={FPS * 50}
        fps={FPS}
        width={HORIZONTAL.width}
        height={HORIZONTAL.height}
        defaultProps={{}}
      />

      {/* ===== SEC+ SHOWCASE (1 composition, 50 seconds, landscape for Gumroad) ===== */}
      <Composition
        id="SecPlusShowcase"
        schema={secPlusShowcaseSchema}
        component={SecPlusShowcase}
        durationInFrames={FPS * 50}
        fps={FPS}
        width={HORIZONTAL.width}
        height={HORIZONTAL.height}
        defaultProps={{}}
      />

      {/* ===== CERT DEBATE (1 composition, 15 seconds, vertical for LinkedIn) ===== */}
      <Composition
        id="CertDebate"
        schema={certDebateSchema}
        component={CertDebate}
        durationInFrames={FPS * 4}
        fps={FPS}
        width={VERTICAL.width}
        height={VERTICAL.height}
        defaultProps={{}}
      />

      {/* ===== YOUTUBE INTRO (1 default composition, 5 seconds, landscape) ===== */}
      <Composition
        id="YouTubeIntro-Default"
        schema={youtubeIntroSchema}
        component={YouTubeIntro}
        durationInFrames={FPS * 5}
        fps={FPS}
        width={HORIZONTAL.width}
        height={HORIZONTAL.height}
        defaultProps={{
          channelName: "COREDIRECTIVE_",
          tagline: "Cybersecurity. Career Intel. No Fluff.",
          episodeTitle: "Episode 01: Breaking Into Cyber",
        }}
      />
    </>
  );
};
