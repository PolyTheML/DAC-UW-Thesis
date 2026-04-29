export const runtime = "edge";

import { getSession } from "@/lib/session-store";
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

  const session = getSession(sessionId);
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
      decisions: session.decisions.map((d) => ({
        round: d.round,
        action: d.action,
        actionLabel: d.actionLabel,
        reward: d.reward,
        regret: d.regret,
        riskScore: d.riskScore,
        premiumLoading: d.premiumLoading,
      })),
      psi: psiResults,
    }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
