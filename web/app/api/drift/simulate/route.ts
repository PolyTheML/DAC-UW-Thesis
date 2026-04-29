export const runtime = "edge";

import {
  buildContextVector,
  computeExpectedRewards,
  computeMortalityMultiplier,
} from "@/config/underwriting-features";
import {
  createBanditState,
  banditDecide,
  banditUpdate,
} from "@/lib/bandits";

// ── Applicant generator (simplified, seedable) ───────────────────────────────

interface Applicant {
  features: Record<string, number | string | string[]>;
  context: number[];
  riskScore: number;
  expectedRewards: number[];
}

function makeLCG(seed: number) {
  let s = seed;
  return () => {
    s = (1103515245 * s + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

function sampleNormal(rng: () => number, mean: number, std: number) {
  // Box-Muller
  const u1 = rng();
  const u2 = rng();
  const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return mean + z * std;
}

function generateApplicant(
  rng: () => number,
  driftFactor: number
): Applicant {
  // Base distributions from cambodia_dataset.csv
  // Drift factor: 0 = baseline, 1 = full drift
  const age = Math.round(
    Math.max(18, Math.min(85, sampleNormal(rng, 42.6 + driftFactor * 12, 11.2)))
  );
  const bmi = Math.max(
    16,
    Math.min(40, sampleNormal(rng, 23.0 + driftFactor * 2, 2.3))
  );
  const isSmoking = rng() < 0.245 + driftFactor * 0.25 ? 1 : 0;
  const isExercise = rng() < 0.403 - driftFactor * 0.15 ? 1 : 0;
  const hasFamilyHistory = rng() < 0.166 + driftFactor * 0.1 ? 1 : 0;
  const monthlyIncome = Math.max(
    60,
    Math.min(600, sampleNormal(rng, 165.7 - driftFactor * 40, 73.1))
  );

  const regions = [
    "Phnom Penh",
    "Siem Reap",
    "Battambang",
    "Preah Sihanouk",
    "Kampong Cham",
    "Other Rural",
  ];
  const region = regions[Math.floor(rng() * regions.length)];

  const occupations = [
    "Rice Farmer",
    "Garment Factory Worker",
    "Moto/Tuk-tuk Driver",
    "Market Vendor",
    "Construction Worker",
    "Civil Servant",
    "Monk/Retired",
  ];
  const occupation = occupations[Math.floor(rng() * occupations.length)];

  // Conditions: drift increases condition probability
  const conditionProb = 0.185 + driftFactor * 0.3;
  const conditions: string[] = [];
  const allConditions = [
    "Hypertension",
    "Diabetes",
    "Heart Disease",
    "COPD/Asthma",
    "Arthritis",
    "TB",
    "Hepatitis B",
  ];
  for (const c of allConditions) {
    if (rng() < conditionProb) conditions.push(c);
  }

  const features: Record<string, number | string | string[]> = {
    age,
    bmi,
    is_smoking: isSmoking,
    is_exercise: isExercise,
    has_family_history: hasFamilyHistory,
    monthly_income_usd: monthlyIncome,
    region,
    occupation,
    pre_existing_conditions: conditions,
  };

  const context = buildContextVector(features);
  const riskScore = computeMortalityMultiplier(features);
  const expectedRewards = computeExpectedRewards(riskScore, monthlyIncome);

  return { features, context, riskScore, expectedRewards };
}

// ── Simulation ───────────────────────────────────────────────────────────────

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const {
      nRounds = 2000,
      driftRound = 1000,
      driftMagnitude = 1.0,
      alpha = 1.0,
      lambda = 0.995,
      seed = 42,
    }: {
      nRounds?: number;
      driftRound?: number;
      driftMagnitude?: number;
      alpha?: number;
      lambda?: number;
      seed?: number;
    } = body;

    const rng = makeLCG(seed);

    // Two bandits: static vs adaptive
    const staticBandit = createBanditState("linucb", 27, { alpha });
    const adaptiveBandit = createBanditState("discountedLinUCB", 27, {
      alpha,
      lambda,
    });

    const staticSeries: {
      round: number;
      cumReward: number;
      cumRegret: number;
      action: number;
    }[] = [];
    const adaptiveSeries: {
      round: number;
      cumReward: number;
      cumRegret: number;
      action: number;
    }[] = [];

    let staticCumReward = 0;
    let staticCumRegret = 0;
    let adaptiveCumReward = 0;
    let adaptiveCumRegret = 0;

    // PSI tracking on approved portfolio
    const staticApproved: { riskScores: number[] } = { riskScores: [] };
    const adaptiveApproved: { riskScores: number[] } = { riskScores: [] };

    // (PSI time series could be added here for live monitoring)

    for (let t = 0; t < nRounds; t++) {
      const driftFactor = t >= driftRound ? driftMagnitude : 0;
      const applicant = generateApplicant(rng, driftFactor);
      const optimalReward = Math.max(...applicant.expectedRewards);

      // Static bandit
      const staticResult = banditDecide(staticBandit, "linucb", applicant.context);
      const staticReward = applicant.expectedRewards[staticResult.action];
      const staticRegret = optimalReward - staticReward;
      banditUpdate(staticBandit, "linucb", staticResult.action, applicant.context, staticReward);
      staticCumReward += staticReward;
      staticCumRegret += staticRegret;
      staticSeries.push({
        round: t + 1,
        cumReward: staticCumReward,
        cumRegret: staticCumRegret,
        action: staticResult.action,
      });
      if (staticResult.action === 0 || staticResult.action === 1) {
        staticApproved.riskScores.push(applicant.riskScore);
      }

      // Adaptive bandit
      const adaptiveResult = banditDecide(
        adaptiveBandit,
        "discountedLinUCB",
        applicant.context
      );
      const adaptiveReward = applicant.expectedRewards[adaptiveResult.action];
      const adaptiveRegret = optimalReward - adaptiveReward;
      banditUpdate(
        adaptiveBandit,
        "discountedLinUCB",
        adaptiveResult.action,
        applicant.context,
        adaptiveReward
      );
      adaptiveCumReward += adaptiveReward;
      adaptiveCumRegret += adaptiveRegret;
      adaptiveSeries.push({
        round: t + 1,
        cumReward: adaptiveCumReward,
        cumRegret: adaptiveCumRegret,
        action: adaptiveResult.action,
      });
      if (adaptiveResult.action === 0 || adaptiveResult.action === 1) {
        adaptiveApproved.riskScores.push(applicant.riskScore);
      }
    }

    return new Response(
      JSON.stringify({
        nRounds,
        driftRound,
        driftMagnitude,
        alpha,
        lambda,
        static: {
          finalReward: staticCumReward,
          finalRegret: staticCumRegret,
          series: staticSeries,
        },
        adaptive: {
          finalReward: adaptiveCumReward,
          finalRegret: adaptiveCumRegret,
          series: adaptiveSeries,
        },
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
