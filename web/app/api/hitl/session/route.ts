export const runtime = "nodejs";

import { getHitlSession } from "@/lib/hitl-store";
import { computePsiForFeature } from "@/lib/psi";
import { PSI_REFERENCE } from "@/config/underwriting-features";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const sessionId = url.searchParams.get("sessionId");

  if (!sessionId) {
    return new Response(JSON.stringify({ error: "Missing sessionId" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const session = getHitlSession(sessionId);
  if (!session) {
    return new Response(JSON.stringify({ error: "Session not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Compute PSI for approved portfolio dynamically from config keys
  const psiResults: Record<string, { value: number; status: string }> = {};
  for (const key of Object.keys(PSI_REFERENCE)) {
    const approved = session.approvedFeatures[key as keyof typeof session.approvedFeatures];
    if (approved && approved.length > 0) {
      const result = computePsiForFeature(key, approved as string[] | number[]);
      psiResults[key] = result;
    }
  }

  return new Response(
    JSON.stringify({
      sessionId: session.sessionId,
      algo: session.algo,
      cumulativeReward: session.cumulativeReward,
      cumulativeRegret: session.cumulativeRegret,
      cumulativeHumanCost: session.cumulativeHumanCost,
      alignmentScore: session.alignmentScore,
      pendingQueueLength: session.pendingReviews.length,
      overrideCount: session.overrideHistory.length,
      pendingReviews: session.pendingReviews.map((r) => ({
        id: r.id,
        round: r.round,
        riskScore: r.riskScore,
        banditRecommendedAction: r.banditRecommendedAction,
        applicantFeatures: r.applicantFeatures,
        submittedAt: r.submittedAt,
      })),
      overrideHistory: session.overrideHistory.map((o) => ({
        reviewId: o.reviewId,
        round: o.round,
        originalAction: o.originalAction,
        overrideAction: o.overrideAction,
        overrideLabel: o.overrideLabel,
        riskScore: o.riskScore,
        reward: o.reward,
        regret: o.regret,
        humanName: o.humanName,
        timestamp: o.timestamp,
      })),
      psi: psiResults,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
