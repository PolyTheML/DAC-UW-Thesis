export const runtime = "edge";

import {
  buildContextVector,
  computeExpectedRewards,
  computeMortalityMultiplier,
  ACTIONS,
  ALGO_PARAMS,
} from "@/config/underwriting-features";
import {
  createBanditState,
  banditDecide,
  banditUpdate,
  type AlgoName,
} from "@/lib/bandits";
import { getSession, createSession, addDecision } from "@/lib/session-store";
import { computePsiForFeature } from "@/lib/psi";

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const {
      features,
      algo,
      sessionId: existingSessionId,
      param,
    }: {
      features: Record<string, number | string | string[]>;
      algo: AlgoName;
      sessionId?: string;
      param?: number;
    } = body;

    if (!features || !algo) {
      return new Response(
        JSON.stringify({ error: "Missing features or algo" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const sessionId = existingSessionId || generateId();
    let session = getSession(sessionId);

    if (!session) {
      const bandit = createBanditState(algo, 27, {
        alpha: algo === "linucb" ? (param ?? ALGO_PARAMS.linucb.alpha) : undefined,
        v2: algo === "linTS" ? (param ?? ALGO_PARAMS.linTS.v2) : undefined,
        epsilon: algo === "epsilonGreedy" ? (param ?? ALGO_PARAMS.epsilonGreedy.epsilon) : undefined,
      });
      session = createSession(sessionId, algo, bandit);
    }

    // Build context vector (27-dim, normalised)
    const context = buildContextVector(features);

    // Compute risk score (mortality multiplier)
    const riskScore = computeMortalityMultiplier(features);
    const monthlyIncome = Number(features.monthly_income_usd ?? 165);

    // Oracle expected rewards for regret calculation
    const expectedRewards = computeExpectedRewards(riskScore, monthlyIncome);
    const optimalReward = Math.max(...expectedRewards);

    // Bandit decision
    const result = banditDecide(session.bandit, algo, context);
    const action = result.action;
    const actionLabel = ACTIONS[action].label;
    const premiumLoading = ACTIONS[action].loadingPercent;

    // Reward (deterministic expected value)
    const reward = expectedRewards[action];
    const regret = optimalReward - reward;

    // Update bandit
    banditUpdate(session.bandit, algo, action, context, reward);

    // Record decision
    const record = {
      round: session.decisions.length + 1,
      action,
      actionLabel,
      reward,
      regret,
      riskScore,
      premiumLoading,
      qValues: result.qValues,
      featureContributions: result.featureContributions,
      inputs: features,
      context,
      timestamp: Date.now(),
    };
    addDecision(sessionId, record);

    // Compute PSI for approved portfolio
    const psiResults: Record<string, { value: number; status: string }> = {};
    for (const key of Object.keys(session.approvedFeatures)) {
      const approved = session.approvedFeatures[key as keyof typeof session.approvedFeatures];
      if (approved && approved.length > 0) {
        const result = computePsiForFeature(key, approved as string[] | number[]);
        psiResults[key] = result;
      }
    }

    return new Response(
      JSON.stringify({
        sessionId,
        action,
        actionLabel,
        riskScore,
        premiumLoading,
        qValues: result.qValues,
        featureContributions: result.featureContributions,
        reward,
        regret,
        cumulativeReward: session.cumulativeReward,
        cumulativeRegret: session.cumulativeRegret,
        round: record.round,
        psi: psiResults,
        decisions: session.decisions.map((d) => ({
          round: d.round,
          action: d.action,
          actionLabel: d.actionLabel,
          reward: d.reward,
          regret: d.regret,
          riskScore: d.riskScore,
          premiumLoading: d.premiumLoading,
        })),
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
