/**
 * In-memory session store for the demo.
 *
 * ⚠️  This uses a global Map. In production (especially on Vercel Edge
 *    Runtime) you should replace this with Redis or a database, because
 *    global mutable state is NOT guaranteed to persist across requests.
 *    For a thesis demo it is sufficient.
 */

import type { BanditState, AlgoName } from "./bandits";

export interface DecisionRecord {
  round: number;
  action: number;
  actionLabel: string;
  reward: number;
  regret: number;
  riskScore: number;
  premiumLoading: number;
  qValues: number[];
  featureContributions: number[];
  inputs: Record<string, number | string | string[]>;
  context: number[];
  timestamp: number;
}

export interface SessionState {
  sessionId: string;
  algo: AlgoName;
  bandit: BanditState;
  decisions: DecisionRecord[];
  cumulativeReward: number;
  cumulativeRegret: number;
  // PSI tracking: only for approved portfolio (STANDARD or RATED)
  approvedFeatures: {
    region: string[];
    occupation: string[];
    age: number[];
    bmi: number[];
    monthly_income_usd: number[];
  };
}

const store = new Map<string, SessionState>();

export function getSession(sessionId: string): SessionState | undefined {
  return store.get(sessionId);
}

export function createSession(
  sessionId: string,
  algo: AlgoName,
  bandit: BanditState
): SessionState {
  const state: SessionState = {
    sessionId,
    algo,
    bandit,
    decisions: [],
    cumulativeReward: 0,
    cumulativeRegret: 0,
    approvedFeatures: {
      region: [],
      occupation: [],
      age: [],
      bmi: [],
      monthly_income_usd: [],
    },
  };
  store.set(sessionId, state);
  return state;
}

export function addDecision(
  sessionId: string,
  record: DecisionRecord
): SessionState {
  const session = store.get(sessionId);
  if (!session) throw new Error(`Session not found: ${sessionId}`);

  session.decisions.push(record);
  session.cumulativeReward += record.reward;
  session.cumulativeRegret += record.regret;

  // Update approved-portfolio PSI distributions
  if (record.action === 0 || record.action === 1) {
    // STANDARD or RATED
    const inputs = record.inputs;
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

export function deleteSession(sessionId: string): boolean {
  return store.delete(sessionId);
}

export function listSessions(): string[] {
  return Array.from(store.keys());
}
