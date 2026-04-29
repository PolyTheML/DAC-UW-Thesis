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
import {
  getHitlSession,
  createHitlSession,
  addPendingReview,
  type SimulatedUnderwriterConfig,
} from "@/lib/hitl-store";
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
      simulatedUnderwriter,
    }: {
      features: Record<string, number | string | string[]>;
      algo: AlgoName;
      sessionId?: string;
      param?: number;
      simulatedUnderwriter?: SimulatedUnderwriterConfig;
    } = body;

    if (!features || !algo) {
      return new Response(
        JSON.stringify({ error: "Missing features or algo" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const sessionId = existingSessionId || generateId();
    let session = getHitlSession(sessionId);

    if (!session) {
      const bandit = createBanditState(algo, 27, {
        alpha: algo === "linucb" ? (param ?? ALGO_PARAMS.linucb.alpha) : undefined,
        v2: algo === "linTS" ? (param ?? ALGO_PARAMS.linTS.v2) : undefined,
        epsilon: algo === "epsilonGreedy" ? (param ?? ALGO_PARAMS.epsilonGreedy.epsilon) : undefined,
      });
      session = createHitlSession(
        sessionId,
        algo,
        bandit,
        simulatedUnderwriter ?? null
      );
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

    const round = session.decisions.length + session.overrideHistory.length + 1;

    // ── HITL Logic ───────────────────────────────────────────────────────────
    // If REFER → queue for human review, do NOT update bandit yet
    // Otherwise → normal bandit update
    let needsHumanReview = false;
    let reward = 0;
    let regret = 0;

    if (action === 3) {
      // REFER
      needsHumanReview = true;
      const review = {
        id: generateId(),
        round,
        applicantFeatures: features,
        context,
        banditRecommendedAction: action,
        qValues: result.qValues,
        riskScore,
        submittedAt: Date.now(),
      };
      addPendingReview(sessionId, review);

      // Reward/regret for REFER (used for display only)
      reward = expectedRewards[action];
      regret = optimalReward - reward;
    } else {
      // STANDARD, RATED, DECLINE → immediate finalize
      reward = expectedRewards[action];
      regret = optimalReward - reward;

      banditUpdate(session.bandit, algo, action, context, reward);
      session.cumulativeReward += reward;
      session.cumulativeRegret += regret;

      // Update approved portfolio PSI distributions
      if (action === 0 || action === 1) {
        if (features.region)
          session.approvedFeatures.region.push(String(features.region));
        if (features.occupation)
          session.approvedFeatures.occupation.push(String(features.occupation));
        if (features.age)
          session.approvedFeatures.age.push(Number(features.age));
        if (features.bmi)
          session.approvedFeatures.bmi.push(Number(features.bmi));
        if (features.monthly_income_usd)
          session.approvedFeatures.monthly_income_usd.push(
            Number(features.monthly_income_usd)
          );
      }
    }

    // Record decision (even if pending)
    session.decisions.push({
      round,
      action,
      actionLabel,
      reward,
      regret,
      riskScore,
      premiumLoading: ACTIONS[action].loadingPercent,
      qValues: result.qValues,
      featureContributions: result.featureContributions,
      inputs: features,
      context,
      timestamp: Date.now(),
    });

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
        premiumLoading: ACTIONS[action].loadingPercent,
        qValues: result.qValues,
        featureContributions: result.featureContributions,
        reward,
        regret,
        cumulativeReward: session.cumulativeReward,
        cumulativeRegret: session.cumulativeRegret,
        cumulativeHumanCost: session.cumulativeHumanCost,
        round,
        needsHumanReview,
        pendingQueueLength: session.pendingReviews.length,
        psi: psiResults,
        alignmentScore: session.alignmentScore,
        overrideCount: session.overrideHistory.length,
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
