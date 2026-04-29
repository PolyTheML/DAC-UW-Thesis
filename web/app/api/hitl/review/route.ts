export const runtime = "nodejs";

import {
  computeExpectedRewards,
  ACTIONS,
} from "@/config/underwriting-features";
import {
  getHitlSession,
  resolveReview,
} from "@/lib/hitl-store";
import { computePsiForFeature } from "@/lib/psi";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const {
      sessionId,
      reviewId,
      overrideAction,
      humanName = "user",
    }: {
      sessionId: string;
      reviewId: string;
      overrideAction: number;
      humanName?: string;
    } = body;

    if (!sessionId || !reviewId || overrideAction === undefined) {
      return new Response(
        JSON.stringify({ error: "Missing sessionId, reviewId, or overrideAction" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (![0, 1, 2].includes(overrideAction)) {
      return new Response(
        JSON.stringify({ error: "overrideAction must be 0 (STANDARD), 1 (RATED), or 2 (DECLINE)" }),
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

    // Find the pending review to compute reward/regret
    const review = session.pendingReviews.find((r) => r.id === reviewId);
    if (!review) {
      return new Response(JSON.stringify({ error: "Review not found or already resolved" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    const monthlyIncome = Number(review.applicantFeatures.monthly_income_usd ?? 165);
    const expectedRewards = computeExpectedRewards(review.riskScore, monthlyIncome);
    const optimalReward = Math.max(...expectedRewards);

    const reward = expectedRewards[overrideAction];
    const regret = optimalReward - reward;

    const updatedSession = resolveReview(
      sessionId,
      reviewId,
      overrideAction,
      reward,
      regret,
      humanName
    );

    // Compute PSI for approved portfolio
    const psiResults: Record<string, { value: number; status: string }> = {};
    for (const key of Object.keys(updatedSession.approvedFeatures)) {
      const approved = updatedSession.approvedFeatures[key as keyof typeof updatedSession.approvedFeatures];
      if (approved && approved.length > 0) {
        const result = computePsiForFeature(key, approved as string[] | number[]);
        psiResults[key] = result;
      }
    }

    return new Response(
      JSON.stringify({
        sessionId,
        reviewId,
        overrideAction,
        overrideLabel: ACTIONS[overrideAction]?.label ?? "UNKNOWN",
        reward,
        regret,
        cumulativeReward: updatedSession.cumulativeReward,
        cumulativeRegret: updatedSession.cumulativeRegret,
        cumulativeHumanCost: updatedSession.cumulativeHumanCost,
        pendingQueueLength: updatedSession.pendingReviews.length,
        overrideCount: updatedSession.overrideHistory.length,
        alignmentScore: updatedSession.alignmentScore,
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
