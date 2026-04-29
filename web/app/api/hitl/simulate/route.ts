export const runtime = "edge";

import {
  computeExpectedRewards,
} from "@/config/underwriting-features";
import {
  getHitlSession,
  resolveReview,
  simulatedHumanDecision,
} from "@/lib/hitl-store";
import { computePsiForFeature } from "@/lib/psi";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { sessionId }: { sessionId: string } = body;

    if (!sessionId) {
      return new Response(
        JSON.stringify({ error: "Missing sessionId" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const session = getHitlSession(sessionId);
    if (!session) {
      return new Response(JSON.stringify({ error: "Session not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!session.simulatedUnderwriter?.enabled) {
      return new Response(
        JSON.stringify({ error: "Simulated underwriter not enabled" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const conservatism = session.simulatedUnderwriter.conservatism ?? 0.5;
    const resolved: string[] = [];

    // Resolve all pending reviews with simulated human decisions
    // We copy the array because resolveReview mutates the original
    const pending = [...session.pendingReviews];
    for (const review of pending) {
      const decision = simulatedHumanDecision(review.riskScore, conservatism);
      const monthlyIncome = Number(review.applicantFeatures.monthly_income_usd ?? 165);
      const expectedRewards = computeExpectedRewards(review.riskScore, monthlyIncome);
      const optimalReward = Math.max(...expectedRewards);
      const reward = expectedRewards[decision.action];
      const regret = optimalReward - reward;

      resolveReview(
        sessionId,
        review.id,
        decision.action,
        reward,
        regret,
        "simulated"
      );
      resolved.push(review.id);
    }

    // Compute PSI
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
        resolvedCount: resolved.length,
        resolvedIds: resolved,
        cumulativeReward: session.cumulativeReward,
        cumulativeRegret: session.cumulativeRegret,
        cumulativeHumanCost: session.cumulativeHumanCost,
        pendingQueueLength: session.pendingReviews.length,
        overrideCount: session.overrideHistory.length,
        alignmentScore: session.alignmentScore,
        psi: psiResults,
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
