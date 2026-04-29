/**
 * Source-of-truth configuration for the Adaptive Health Insurance Underwriting demo.
 *
 * Extracted from the thesis Python codebase:
 *   - stress_testing/rl/underwriting_bandit.py
 *   - case-study/generate_cambodia_dataset.py
 *   - case-study/cambodia_dataset.csv (computed normalization stats & PSI refs)
 *   - stress_testing/rl/experiments/exp_006_fairness_audit.py
 *
 * All values are grounded in the actual codebase. Any TODO marks a value that
 * could not be inferred from the existing code.
 */

// ─────────────────────────────────────────────────────────────────────────────
// 1. INPUT FEATURES — what the user enters in the UI
// ─────────────────────────────────────────────────────────────────────────────

export type FeatureType = "continuous" | "binary" | "categorical" | "multi_select";

export interface InputFeature {
  name: string;
  label: string;
  type: FeatureType;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  weight?: string; // human-readable weight description from mortality formula
  unit?: string; // display unit suffix (e.g. "USD")
  description: string;
}

export const INPUT_FEATURES: InputFeature[] = [
  {
    name: "age",
    label: "Age",
    type: "continuous",
    min: 18,
    max: 85,
    step: 1,
    weight: "+0.018 per year above 30",
    description: "Applicant age in years (Cambodian median ~25, range 18–85).",
  },
  {
    name: "bmi",
    label: "BMI",
    type: "continuous",
    min: 16,
    max: 40,
    step: 0.1,
    weight: "Indirect via health score",
    description: "Body-mass index (Cambodia: generally lower, urban obesity rising).",
  },
  {
    name: "is_smoking",
    label: "Smoker",
    type: "binary",
    weight: "+0.25",
    description: "Current smoker (high among Cambodian men ~40%).",
  },
  {
    name: "is_exercise",
    label: "Exercises Regularly",
    type: "binary",
    weight: "−0.12",
    description: "Regular physical activity.",
  },
  {
    name: "has_family_history",
    label: "Family History",
    type: "binary",
    weight: "Indirect via GLM coefficients",
    description: "Family history of chronic disease.",
  },
  {
    name: "monthly_income_usd",
    label: "Monthly Income (USD)",
    type: "continuous",
    min: 60,
    max: 600,
    step: 1,
    weight: "Premium affordability (p_accept formula)",
    unit: "USD",
    description: "Monthly income in USD (Cambodia is heavily dollarized).",
  },
  {
    name: "region",
    label: "Region",
    type: "categorical",
    options: ["Phnom Penh", "Siem Reap", "Battambang", "Preah Sihanouk", "Kampong Cham", "Other Rural"],
    weight: "Income factor (Phnom Penh +30%, Rural −15%)",
    description: "Province / region of residence.",
  },
  {
    name: "occupation",
    label: "Occupation",
    type: "categorical",
    options: [
      "Rice Farmer",
      "Garment Factory Worker",
      "Moto/Tuk-tuk Driver",
      "Market Vendor",
      "Construction Worker",
      "Civil Servant",
      "Monk/Retired",
    ],
    weight: "life_risk × 1.8",
    description: "Primary occupation (Cambodia-specific risk proxies).",
  },
  {
    name: "pre_existing_conditions",
    label: "Pre-existing Conditions",
    type: "multi_select",
    options: [
      "Hypertension",
      "Diabetes",
      "Heart Disease",
      "COPD/Asthma",
      "Arthritis",
      "TB",
      "Hepatitis B",
    ],
    weight: "+0.22 per condition; +0.15 TB; +0.10 Hep-B",
    description: "Known pre-existing medical conditions.",
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// 2. BANDIT CONTEXT VECTOR — expanded, normalised features (27-dim)
//    Order MUST match the Python preprocessor exactly.
// ─────────────────────────────────────────────────────────────────────────────

export interface BanditFeatureStat {
  name: string;
  mean: number;
  std: number;
}

export const BANDIT_FEATURE_STATS: BanditFeatureStat[] = [
  { name: "age", mean: 42.6075, std: 11.20005197899394 },
  { name: "bmi", mean: 22.98285, std: 2.345316851315944 },
  { name: "is_smoking", mean: 0.245, std: 0.4301947625981556 },
  { name: "is_exercise", mean: 0.403, std: 0.4906234357201448 },
  { name: "has_family_history", mean: 0.166, std: 0.3721736914779364 },
  { name: "monthly_income_usd", mean: 165.729, std: 73.08265934233835 },
  { name: "condition_count", mean: 0.37, std: 0.5790229993850922 },
  { name: "has_hypertension", mean: 0.0595, std: 0.23661729410999519 },
  { name: "has_diabetes", mean: 0.0565, std: 0.2309424543227258 },
  { name: "has_heart_disease", mean: 0.039, std: 0.19364335484192896 },
  { name: "has_copd_asthma", mean: 0.047, std: 0.21169177287592372 },
  { name: "has_arthritis", mean: 0.025, std: 0.1561639958402653 },
  { name: "has_tb", mean: 0.061, std: 0.2393901706982003 },
  { name: "has_hepatitis_b", mean: 0.082, std: 0.2744333376767739 },
  { name: "region_Battambang", mean: 0.117, std: 0.3215006708246039 },
  { name: "region_Kampong Cham", mean: 0.144, std: 0.35117753748127983 },
  { name: "region_Other Rural", mean: 0.3835, std: 0.4863599726658288 },
  { name: "region_Phnom Penh", mean: 0.178, std: 0.38260840894744935 },
  { name: "region_Preah Sihanouk", mean: 0.0695, std: 0.25436607684698304 },
  { name: "region_Siem Reap", mean: 0.108, std: 0.3104580359662929 },
  { name: "occ_Civil Servant", mean: 0.086, std: 0.2804341663578645 },
  { name: "occ_Construction Worker", mean: 0.0865, std: 0.28117126211496024 },
  { name: "occ_Garment Factory Worker", mean: 0.21, std: 0.40741010234866276 },
  { name: "occ_Market Vendor", mean: 0.1435, std: 0.35066969446661433 },
  { name: "occ_Monk/Retired", mean: 0.058, std: 0.23380190689092534 },
  { name: "occ_Moto/Tuk-tuk Driver", mean: 0.117, std: 0.3215006708246039 },
  { name: "occ_Rice Farmer", mean: 0.299, std: 0.457934331455901 },
];

export const BANDIT_FEATURE_ORDER = BANDIT_FEATURE_STATS.map((f) => f.name);

// ─────────────────────────────────────────────────────────────────────────────
// 3. OCCUPATION RISK LOOKUP — from generate_cambodia_dataset.py
// ─────────────────────────────────────────────────────────────────────────────

export const OCCUPATION_RISKS: Record<
  string,
  { health_risk: number; life_risk: number; income_base: number }
> = {
  "Rice Farmer": { health_risk: 0.30, life_risk: 0.25, income_base: 120 },
  "Garment Factory Worker": { health_risk: 0.25, life_risk: 0.20, income_base: 180 },
  "Moto/Tuk-tuk Driver": { health_risk: 0.40, life_risk: 0.45, income_base: 200 },
  "Market Vendor": { health_risk: 0.20, life_risk: 0.15, income_base: 160 },
  "Construction Worker": { health_risk: 0.45, life_risk: 0.40, income_base: 220 },
  "Civil Servant": { health_risk: 0.15, life_risk: 0.12, income_base: 350 },
  "Monk/Retired": { health_risk: 0.35, life_risk: 0.55, income_base: 100 },
};

// ─────────────────────────────────────────────────────────────────────────────
// 4. ACTIONS
// ─────────────────────────────────────────────────────────────────────────────

export interface ActionDef {
  id: number;
  label: string;
  loadingPercent: number;
  badgeColor: string; // Tailwind colour class fragment, e.g. "green", "amber", "blue", "red"
  description: string;
}

export const ACTIONS: ActionDef[] = [
  {
    id: 0,
    label: "STANDARD",
    loadingPercent: 0,
    badgeColor: "green",
    description: "Standard terms — no premium loading.",
  },
  {
    id: 1,
    label: "RATED",
    loadingPercent: 25,
    badgeColor: "amber",
    description: "Rated — +25% premium loading.",
  },
  {
    id: 2,
    label: "DECLINE",
    loadingPercent: 0,
    badgeColor: "red",
    description: "Decline — application rejected.",
  },
  {
    id: 3,
    label: "REFER",
    loadingPercent: 0,
    badgeColor: "blue",
    description: "Refer — manual underwriter review.",
  },
];

export const ACTION_STANDARD = 0;
export const ACTION_RATED = 1;
export const ACTION_DECLINE = 2;
export const ACTION_REFER = 3;

// ─────────────────────────────────────────────────────────────────────────────
// 5. REWARD FUNCTION — deterministic expected-reward port from Python
//    (matches expected_rewards() in underwriting_bandit.py)
// ─────────────────────────────────────────────────────────────────────────────

export function computeExpectedRewards(
  mortalityMultiplier: number,
  monthlyIncomeUsd: number
): number[] {
  const basePremium = 200 * mortalityMultiplier;
  const expectedClaims = 150 * mortalityMultiplier;
  const adverseFactor = mortalityMultiplier <= 2.0 ? 1.0 : 1.35;

  const pAccept = (premium: number) => {
    const ratio = (premium / 12) / monthlyIncomeUsd;
    return Math.max(0.05, 0.95 - 3.5 * ratio);
  };

  const pStd = pAccept(basePremium);
  const pRtd = pAccept(basePremium * 1.25);

  const rStd =
    pStd * (basePremium - expectedClaims * adverseFactor) +
    (1 - pStd) * -25;
  const rRtd =
    pRtd * (basePremium * 1.25 - expectedClaims) + (1 - pRtd) * -25;
  const rDcl = -10.0;
  const optimal = Math.max(rStd, rRtd, rDcl);
  const rRef = 0.7 * optimal - 35.0;

  return [rStd, rRtd, rDcl, rRef];
}

/**
 * Compute the mortality multiplier from raw input features.
 * Mirrors the logic in generate_cambodia_dataset.py.
 */
export function computeMortalityMultiplier(
  inputs: Record<string, number | string | string[]>
): number {
  const age = Number(inputs.age ?? 30);
  const occupation = String(inputs.occupation ?? "Rice Farmer");
  const isSmoking = Boolean(inputs.is_smoking);
  const isExercise = Boolean(inputs.is_exercise);
  const conditions = Array.isArray(inputs.pre_existing_conditions)
    ? (inputs.pre_existing_conditions as string[])
    : [];

  const occ = OCCUPATION_RISKS[occupation];
  const occLifeRisk = occ?.life_risk ?? 0.25;

  let mm = 1.0;
  mm += (age - 30) * 0.018;
  mm += occLifeRisk * 1.8;
  mm += isSmoking ? 0.25 : 0;
  mm -= isExercise ? 0.12 : 0;
  mm += conditions.length * 0.22;
  mm += conditions.includes("TB") ? 0.15 : 0;
  mm += conditions.includes("Hepatitis B") ? 0.10 : 0;

  return Math.min(Math.max(mm, 0.5), 5.0);
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. PSI REFERENCE DISTRIBUTIONS — extracted from cambodia_dataset.csv
// ─────────────────────────────────────────────────────────────────────────────

export interface PsiReference {
  type: "categorical" | "binned";
  displayName?: string;
  bins?: number[]; // continuous: bin edges (length = dist.length + 1)
  labels?: string[]; // categorical: bin labels
  dist: number[]; // probabilities summing to 1
}

export const PSI_REFERENCE: Record<string, PsiReference> = {
  region: {
    type: "categorical",
    labels: ["Battambang", "Kampong Cham", "Other Rural", "Phnom Penh", "Preah Sihanouk", "Siem Reap"],
    dist: [0.117, 0.144, 0.3835, 0.178, 0.0695, 0.108],
  },
  occupation: {
    type: "categorical",
    labels: [
      "Civil Servant",
      "Construction Worker",
      "Garment Factory Worker",
      "Market Vendor",
      "Monk/Retired",
      "Moto/Tuk-tuk Driver",
      "Rice Farmer",
    ],
    dist: [0.086, 0.0865, 0.21, 0.1435, 0.058, 0.117, 0.299],
  },
  age: {
    type: "binned",
    displayName: "Age",
    bins: [19, 30, 33, 36, 39, 41, 44, 47, 51, 58, 85],
    dist: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
  },
  bmi: {
    type: "binned",
    displayName: "BMI",
    bins: [16.0, 19.9, 21.0, 21.7, 22.4, 22.9, 23.5, 24.2, 25.0, 26.0, 30.4],
    dist: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
  },
  monthly_income_usd: {
    type: "binned",
    displayName: "Monthly Income",
    bins: [60.0, 91.0, 108.0, 124.0, 138.0, 152.0, 166.0, 183.0, 209.0, 267.0, 498.0],
    dist: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// 7. ALGORITHM PARAMETERS — from thesis experiments
// ─────────────────────────────────────────────────────────────────────────────

export const ALGO_PARAMS = {
  linucb: {
    alpha: 1.0, // exploration parameter (Li et al. 2010)
  },
  linTS: {
    v2: 1.0, // posterior covariance scaling (Agrawal & Goyal 2013)
  },
  epsilonGreedy: {
    epsilon: 0.15, // EXP-007 benchmark value
  },
  nRounds: 5000, // simulation length from Python experiments
  seed: 42,
};

// ─────────────────────────────────────────────────────────────────────────────
// 8. CONTEXT VECTOR BUILDER — converts raw inputs → normalised 27-dim vector
//    MUST stay in sync with BANDIT_FEATURE_ORDER.
// ─────────────────────────────────────────────────────────────────────────────

export function buildContextVector(
  inputs: Record<string, number | string | string[]>
): number[] {
  const age = Number(inputs.age ?? 30);
  const bmi = Number(inputs.bmi ?? 23);
  const isSmoking = Number(inputs.is_smoking ?? 0);
  const isExercise = Number(inputs.is_exercise ?? 0);
  const hasFamilyHistory = Number(inputs.has_family_history ?? 0);
  const monthlyIncome = Number(inputs.monthly_income_usd ?? 165);
  const region = String(inputs.region ?? "Phnom Penh");
  const occupation = String(inputs.occupation ?? "Rice Farmer");
  const conditions = Array.isArray(inputs.pre_existing_conditions)
    ? (inputs.pre_existing_conditions as string[])
    : [];

  const hasHypertension = conditions.includes("Hypertension") ? 1 : 0;
  const hasDiabetes = conditions.includes("Diabetes") ? 1 : 0;
  const hasHeartDisease = conditions.includes("Heart Disease") ? 1 : 0;
  const hasCopdAsthma = conditions.includes("COPD/Asthma") ? 1 : 0;
  const hasArthritis = conditions.includes("Arthritis") ? 1 : 0;
  const hasTb = conditions.includes("TB") ? 1 : 0;
  const hasHepatitisB = conditions.includes("Hepatitis B") ? 1 : 0;
  const conditionCount =
    hasHypertension +
    hasDiabetes +
    hasHeartDisease +
    hasCopdAsthma +
    hasArthritis +
    hasTb +
    hasHepatitisB;

  const raw: Record<string, number> = {
    age,
    bmi,
    is_smoking: isSmoking,
    is_exercise: isExercise,
    has_family_history: hasFamilyHistory,
    monthly_income_usd: monthlyIncome,
    condition_count: conditionCount,
    has_hypertension: hasHypertension,
    has_diabetes: hasDiabetes,
    has_heart_disease: hasHeartDisease,
    has_copd_asthma: hasCopdAsthma,
    has_arthritis: hasArthritis,
    has_tb: hasTb,
    has_hepatitis_b: hasHepatitisB,
    "region_Battambang": region === "Battambang" ? 1 : 0,
    "region_Kampong Cham": region === "Kampong Cham" ? 1 : 0,
    "region_Other Rural": region === "Other Rural" ? 1 : 0,
    "region_Phnom Penh": region === "Phnom Penh" ? 1 : 0,
    "region_Preah Sihanouk": region === "Preah Sihanouk" ? 1 : 0,
    "region_Siem Reap": region === "Siem Reap" ? 1 : 0,
    "occ_Civil Servant": occupation === "Civil Servant" ? 1 : 0,
    "occ_Construction Worker": occupation === "Construction Worker" ? 1 : 0,
    "occ_Garment Factory Worker": occupation === "Garment Factory Worker" ? 1 : 0,
    "occ_Market Vendor": occupation === "Market Vendor" ? 1 : 0,
    "occ_Monk/Retired": occupation === "Monk/Retired" ? 1 : 0,
    "occ_Moto/Tuk-tuk Driver": occupation === "Moto/Tuk-tuk Driver" ? 1 : 0,
    "occ_Rice Farmer": occupation === "Rice Farmer" ? 1 : 0,
  };

  // Z-score normalisation using precomputed dataset statistics
  const vec = BANDIT_FEATURE_ORDER.map((name) => {
    const val = raw[name] ?? 0;
    const stat = BANDIT_FEATURE_STATS.find((s) => s.name === name)!;
    return (val - stat.mean) / (stat.std > 0 ? stat.std : 1);
  });

  return vec;
}
