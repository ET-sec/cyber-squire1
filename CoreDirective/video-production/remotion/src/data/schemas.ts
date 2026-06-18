/**
 * Zod schemas for all Remotion composition props.
 * Used by Root.tsx for Composition registration and by template components for type inference.
 * This ensures type safety between the schema definitions and the component props.
 */

import { z } from "zod";

export const certCardSchema = z.object({
  certName: z.string(),
  certFullName: z.string(),
  issuer: z.string(),
  passDate: z.string(),
  difficulty: z.string(),
  factoids: z.tuple([z.string(), z.string(), z.string()]),
  salaryImpact: z.string(),
});

export type CertCardProps = z.infer<typeof certCardSchema>;

export const didYouKnowSchema = z.object({
  category: z.string(),
  fact: z.string(),
  source: z.string().optional(),
  callToAction: z.string(),
});

export type DidYouKnowProps = z.infer<typeof didYouKnowSchema>;

export const debtTrackerSchema = z.object({
  weekNumber: z.number(),
  startingDebt: z.number(),
  currentDebt: z.number(),
  weeklyIncome: z.number(),
  incomeSource: z.string(),
  milestone: z.string().optional(),
});

export type DebtTrackerProps = z.infer<typeof debtTrackerSchema>;

export const youtubeIntroSchema = z.object({
  channelName: z.string(),
  tagline: z.string(),
  episodeTitle: z.string().optional(),
});

export type YouTubeIntroProps = z.infer<typeof youtubeIntroSchema>;

/** CCNA Showcase has no dynamic props - all data is baked in */
export const ccnaShowcaseSchema = z.object({});

/** CCNA Showcase V2 - same pattern, all data baked in */
export const ccnaShowcaseV2Schema = z.object({});

/** Sec+ Showcase - all data baked in */
export const secPlusShowcaseSchema = z.object({});

/** Cert Debate - all data baked in */
export const certDebateSchema = z.object({});
