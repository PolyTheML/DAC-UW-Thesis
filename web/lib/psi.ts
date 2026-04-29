/**
 * Population Stability Index (PSI) computation.
 * Matches the implementation in exp_006_fairness_audit.py.
 */

import { PSI_REFERENCE } from "@/config/underwriting-features";

export interface PsiResult {
  value: number;
  status: "GREEN" | "AMBER" | "RED";
}

const EPS = 1e-8;

export function computePsi(expectedDist: number[], actualDist: number[]): number {
  const eSum = expectedDist.reduce((a, b) => a + b, 0);
  const aSum = actualDist.reduce((a, b) => a + b, 0);
  const eNorm = expectedDist.map((v) => v / (eSum + EPS));
  const aNorm = actualDist.map((v) => v / (aSum + EPS));

  let psi = 0.0;
  for (let i = 0; i < eNorm.length; i++) {
    const e = eNorm[i];
    const a = aNorm[i];
    if (e > EPS) {
      psi += (a - e) * Math.log((a + EPS) / (e + EPS));
    } else if (a > EPS) {
      psi += a - e;
    }
  }
  return psi;
}

export function psiStatus(psi: number): "GREEN" | "AMBER" | "RED" {
  if (psi < 0.1) return "GREEN";
  if (psi < 0.25) return "AMBER";
  return "RED";
}

/**
 * Build an actual distribution array for a categorical feature.
 */
export function buildCategoricalDist(
  values: string[],
  labels: string[]
): number[] {
  const counts = new Array(labels.length).fill(0);
  for (const v of values) {
    const idx = labels.indexOf(v);
    if (idx >= 0) counts[idx]++;
  }
  return counts;
}

/**
 * Build an actual distribution array for a binned continuous feature.
 */
export function buildBinnedDist(values: number[], bins: number[]): number[] {
  const counts = new Array(bins.length - 1).fill(0);
  for (const v of values) {
    for (let i = 0; i < bins.length - 1; i++) {
      if (v >= bins[i] && v < bins[i + 1]) {
        counts[i]++;
        break;
      }
      // last bin is inclusive on both sides
      if (i === bins.length - 2 && v >= bins[i] && v <= bins[i + 1]) {
        counts[i]++;
        break;
      }
    }
  }
  return counts;
}

export function computePsiForFeature(
  featureName: string,
  values: number[] | string[]
): PsiResult {
  const ref = PSI_REFERENCE[featureName];
  if (!ref) {
    // TODO: no reference defined for this feature
    return { value: 0, status: "GREEN" };
  }

  // PSI is unreliable with very small samples; require at least 5 observations
  if (values.length < 5) {
    return { value: 0, status: "GREEN" };
  }

  let actualDist: number[];
  if (ref.type === "categorical") {
    actualDist = buildCategoricalDist(values as string[], ref.labels ?? []);
  } else {
    actualDist = buildBinnedDist(values as number[], ref.bins ?? []);
  }

  const psi = computePsi(ref.dist, actualDist);
  return { value: psi, status: psiStatus(psi) };
}
