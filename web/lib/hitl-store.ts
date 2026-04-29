/**
 * Human-in-the-Loop (HITL) store extensions.
 *
 * When the bandit selects REFER, the decision enters a human-review queue.
 * A human (or simulated) underwriter can override to any action.
 * The bandit learns from the override action and reward.
 */

import type { BanditState, AlgoName } from "./bandits";
import type { DecisionRecord } from "./session-store";
import { banditUpdate } from "./bandits";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface PendingReview {
  id: string;
  round: number;
  applicantFeatures: Record<string, number | string | string[]>;
  context: number[];
  banditRecommendedAction: number; // usually REFER (3)
  qValues: number[];
  riskScore: number;
  submittedAt: number;
}

export interface OverrideRecord {
  reviewId: string;
  round: number;
  originalAction: number;
  overrideAction: number;
  overrideLabel: string;
  riskScore: number;
  reward: number;
  regret: number;
  humanName: string; // "user" | "simulated"
  timestamp: number;
}

export interface HitlSessionState {
  sessionId: string;
  algo: AlgoName;
  bandit: BanditState;

  // Original bandit decisions (including REFER)
  decisions: DecisionRecord[];

  // Human review queue
  pendingReviews: PendingReview[];
  overrideHistory: OverrideRecord[];

  // Metrics
  cumulativeReward: number;
  cumulativeRegret: number;
  cumulativeHumanCost: number; // $35 per review

  // Policy alignment tracking
  alignmentWindow: number[]; // last N agreement booleans (1 = agree)
  alignmentScore: number; // rolling average agreement rate

  // Approved portfolio for PSI
  approvedFeatures: {
    region: string[];
    occupation: string[];
    age: number[];
    bmi: number[];
    monthly_income_usd: number[];
  };

  // Simulated underwriter config
  simulatedUnderwriter: SimulatedUnderwriterConfig | null;
}

export interface SimulatedUnderwriterConfig {
  enabled: boolean;
  conservatism: number; // 0 = aggressive, 1 = conservative
  autoResolveDelayMs: number; // 0 = manual only
}

// ─────────────────────────────────────────────────────────────────────────────
// Simulated Underwriter Logic
// ─────────────────────────────────────────────────────────────────────────────

/**
 * A simulated human underwriter that makes decisions based on risk score.
 * More conservative than the optimal oracle — mimics real human caution.
 */
export function simulatedHumanDecision(
  riskScore: number,
  conservatism: number
): { action: number; label: string } {
  // Conservative thresholds shift with conservatism parameter
  // conservatism = 0.0 → close to optimal
  // conservatism = 1.0 → very conservative (declines more, refers more)
  const declineThreshold = 1.8 + conservatism * 0.8; // 1.8 .. 2.6
  const referThreshold = 1.3 + conservatism * 0.5;   // 1.3 .. 1.8

  if (riskScore >= declineThreshold) {
    return { action: 2, label: "DECLINE" };
  }
  if (riskScore >= referThreshold) {
    return { action: 1, label: "RATED" };
  }
  return { action: 0, label: "STANDARD" };
}

// ─────────────────────────────────────────────────────────────────────────────
// In-memory HITL Store
// ─────────────────────────────────────────────────────────────────────────────

const hitlStore = new Map<string, HitlSessionState>();

export function getHitlSession(sessionId: string): HitlSessionState | undefined {
  return hitlStore.get(sessionId);
}

export function createHitlSession(
  sessionId: string,
  algo: AlgoName,
  bandit: BanditState,
  simulatedUnderwriter: SimulatedUnderwriterConfig | null = null
): HitlSessionState {
  const state: HitlSessionState = {
    sessionId,
    algo,
    bandit,
    decisions: [],
    pendingReviews: [],
    overrideHistory: [],
    cumulativeReward: 0,
    cumulativeRegret: 0,
    cumulativeHumanCost: 0,
    alignmentWindow: [],
    alignmentScore: 0,
    approvedFeatures: {
      region: [],
      occupation: [],
      age: [],
      bmi: [],
      monthly_income_usd: [],
    },
    simulatedUnderwriter,
  };
  hitlStore.set(sessionId, state);
  return state;
}

export function addPendingReview(
  sessionId: string,
  review: PendingReview
): HitlSessionState {
  const session = hitlStore.get(sessionId);
  if (!session) throw new Error(`HITL session not found: ${sessionId}`);
  session.pendingReviews.push(review);
  return session;
}

/**
 * Resolve a pending review with a human override.
 * The bandit learns from the override action, not the original REFER.
 */
export function resolveReview(
  sessionId: string,
  reviewId: string,
  overrideAction: number,
  reward: number,
  regret: number,
  humanName: string
): HitlSessionState {
  const session = hitlStore.get(sessionId);
  if (!session) throw new Error(`HITL session not found: ${sessionId}`);

  const idx = session.pendingReviews.findIndex((r) => r.id === reviewId);
  if (idx === -1) throw new Error(`Review not found: ${reviewId}`);

  const review = session.pendingReviews[idx];
  session.pendingReviews.splice(idx, 1);

  // Bandit learns from the human's chosen action (override)
  banditUpdate(session.bandit, session.algo, overrideAction, review.context, reward);
  // Also update REFER so it doesn't stay artificially unexplored
  const referReward = 0.7 * (reward + regret) - 35;
  banditUpdate(session.bandit, session.algo, 3, review.context, referReward);

  // Record override
  const override: OverrideRecord = {
    reviewId,
    round: review.round,
    originalAction: review.banditRecommendedAction,
    overrideAction,
    overrideLabel: ["STANDARD", "RATED", "DECLINE", "REFER"][overrideAction] ?? "UNKNOWN",
    riskScore: review.riskScore,
    reward,
    regret,
    humanName,
    timestamp: Date.now(),
  };
  session.overrideHistory.push(override);

  // Update cumulative metrics
  session.cumulativeReward += reward;
  session.cumulativeRegret += regret;
  session.cumulativeHumanCost += 35; // $35 review cost

  // Alignment: compare bandit's best non-REFER choice against human's decision.
  // banditRecommendedAction is always REFER (3) here, so we use qValues instead.
  const nonReferQValues = review.qValues.slice(0, 3);
  const banditBestNonRefer = nonReferQValues.indexOf(Math.max(...nonReferQValues));
  const agreed = banditBestNonRefer === overrideAction ? 1 : 0;
  session.alignmentWindow.push(agreed);
  if (session.alignmentWindow.length > 50) {
    session.alignmentWindow.shift();
  }
  session.alignmentScore =
    session.alignmentWindow.reduce((a, b) => a + b, 0) /
    session.alignmentWindow.length;

  // Update approved portfolio PSI distributions (from override action)
  if (overrideAction === 0 || overrideAction === 1) {
    const inputs = review.applicantFeatures;
    if (inputs.region) session.approvedFeatures.region.push(String(inputs.region));
    if (inputs.occupation)
      session.approvedFeatures.occupation.push(String(inputs.occupation));
    if (inputs.age) session.approvedFeatures.age.push(Number(inputs.age));
    if (inputs.bmi) session.approvedFeatures.bmi.push(Number(inputs.bmi));
    if (inputs.monthly_income_usd)
      session.approvedFeatures.monthly_income_usd.push(
        Number(inputs.monthly_income_usd)
      );
  }

  return session;
}

export function deleteHitlSession(sessionId: string): boolean {
  return hitlStore.delete(sessionId);
}

export function listHitlSessions(): string[] {
  return Array.from(hitlStore.keys());
}
