/**
 * Contextual bandit algorithms ported from Python:
 *   - LinUCB  (Li et al. 2010)
 *   - Linear Thompson Sampling  (Agrawal & Goyal 2013)
 *   - Epsilon-Greedy
 *
 * All algorithms operate on the 27-dim normalised context vector defined in
 * config/underwriting-features.ts.
 */

import {
  eye,
  zeros,
  invertMatrix,
  matVecMul,
  dot,
  outerProduct,
  addMat,
  addVec,
  scaleMat,
  sampleMultivariateNormal,
} from "./math";

export type AlgoName = "linucb" | "linTS" | "epsilonGreedy" | "discountedLinUCB";

export interface BanditState {
  A: number[][][]; // [action][feature][feature]
  b: number[][]; // [action][feature]
  theta: number[][]; // [action][feature] — cached for LinUCB / EpsGreedy
  alpha?: number; // LinUCB
  v2?: number; // LinTS
  epsilon?: number; // EpsilonGreedy
  rngSeed?: number;
  lambda?: number; // DiscountedLinUCB forgetting factor
}

export interface DecisionResult {
  action: number;
  qValues: number[];
  featureContributions: number[];
}

// ─────────────────────────────────────────────────────────────────────────────
// LinUCB
// ─────────────────────────────────────────────────────────────────────────────

export function createLinUCBState(
  nActions: number,
  _nFeatures: number,
  alpha: number
): BanditState {
  return {
    A: Array.from({ length: nActions }, () => eye(_nFeatures)),
    b: Array.from({ length: nActions }, () => zeros(_nFeatures)),
    theta: Array.from({ length: nActions }, () => zeros(_nFeatures)),
    alpha,
  };
}

export function linucbDecide(
  state: BanditState,
  context: number[]
): DecisionResult {
  const nActions = state.A.length;
  const p = zeros(nActions);
  const contributions: number[][] = [];

  for (let a = 0; a < nActions; a++) {
    const A_inv = invertMatrix(state.A[a]);
    const theta = matVecMul(A_inv, state.b[a]);
    state.theta[a] = theta;

    const exploitation = dot(theta, context);
    const exploration =
      (state.alpha ?? 1.0) * Math.sqrt(dot(context, matVecMul(A_inv, context)));
    p[a] = exploitation + exploration;

    // element-wise contribution for interpretability
    contributions[a] = theta.map((t, i) => t * context[i]);
  }

  const action = p.indexOf(Math.max(...p));
  return {
    action,
    qValues: p,
    featureContributions: contributions[action],
  };
}

export function linucbUpdate(
  state: BanditState,
  action: number,
  context: number[],
  reward: number
): void {
  state.A[action] = addMat(state.A[action], outerProduct(context, context));
  state.b[action] = addVec(state.b[action], context.map((c) => c * reward));
}

// ─────────────────────────────────────────────────────────────────────────────
// Discounted LinUCB (Non-stationary adaptation)
// ─────────────────────────────────────────────────────────────────────────────

export function createDiscountedLinUCBState(
  nActions: number,
  _nFeatures: number,
  alpha: number,
  lambda: number
): BanditState {
  return {
    A: Array.from({ length: nActions }, () => eye(_nFeatures)),
    b: Array.from({ length: nActions }, () => zeros(_nFeatures)),
    theta: Array.from({ length: nActions }, () => zeros(_nFeatures)),
    alpha,
    lambda,
  };
}

export function discountedLinUCBDecide(
  state: BanditState,
  context: number[]
): DecisionResult {
  // Decision logic is identical to standard LinUCB
  return linucbDecide(state, context);
}

export function discountedLinUCBUpdate(
  state: BanditState,
  action: number,
  context: number[],
  reward: number
): void {
  const lam = state.lambda ?? 0.995;
  // Forget old information: A = λ * A, b = λ * b
  state.A[action] = scaleMat(state.A[action], lam);
  state.b[action] = state.b[action].map((v) => v * lam);
  // Then add new observation
  state.A[action] = addMat(state.A[action], outerProduct(context, context));
  state.b[action] = addVec(state.b[action], context.map((c) => c * reward));
}

// ─────────────────────────────────────────────────────────────────────────────
// Linear Thompson Sampling
// ─────────────────────────────────────────────────────────────────────────────

let _rngCounter = 0;
function lcgRand(seed: number): () => number {
  let s = seed;
  return () => {
    s = (1103515245 * s + 12345) % 2147483647;
    return (s & 0x7fffffff) / 2147483647;
  };
}

export function createLinTSState(
  nActions: number,
  nFeatures: number,
  v2: number,
  seed = 42
): BanditState {
  return {
    A: Array.from({ length: nActions }, () => eye(nFeatures)),
    b: Array.from({ length: nActions }, () => zeros(nFeatures)),
    theta: Array.from({ length: nActions }, () => zeros(nFeatures)),
    v2,
    rngSeed: seed + _rngCounter++,
  };
}

export function linTSDecide(
  state: BanditState,
  context: number[]
): DecisionResult {
  const nActions = state.A.length;
  const p = zeros(nActions);
  const contributions: number[][] = [];
  const rng = lcgRand(state.rngSeed ?? 42);

  for (let a = 0; a < nActions; a++) {
    const A_inv = invertMatrix(state.A[a]);
    const muHat = matVecMul(A_inv, state.b[a]);
    const cov = scaleMat(A_inv, state.v2 ?? 1.0);
    const muTilde = sampleMultivariateNormal(muHat, cov, rng);
    state.theta[a] = muTilde;
    p[a] = dot(muTilde, context);
    contributions[a] = muTilde.map((t, i) => t * context[i]);
  }

  const action = p.indexOf(Math.max(...p));
  return {
    action,
    qValues: p,
    featureContributions: contributions[action],
  };
}

export function linTSUpdate(
  state: BanditState,
  action: number,
  context: number[],
  reward: number
): void {
  state.A[action] = addMat(state.A[action], outerProduct(context, context));
  state.b[action] = addVec(state.b[action], context.map((c) => c * reward));
}

// ─────────────────────────────────────────────────────────────────────────────
// Epsilon-Greedy
// ─────────────────────────────────────────────────────────────────────────────

export function createEpsilonGreedyState(
  nActions: number,
  nFeatures: number,
  epsilon: number,
  seed = 42
): BanditState {
  return {
    A: Array.from({ length: nActions }, () => eye(nFeatures)),
    b: Array.from({ length: nActions }, () => zeros(nFeatures)),
    theta: Array.from({ length: nActions }, () => zeros(nFeatures)),
    epsilon,
    rngSeed: seed + _rngCounter++,
  };
}

export function epsilonGreedyDecide(
  state: BanditState,
  context: number[]
): DecisionResult {
  const rng = lcgRand(state.rngSeed ?? 42);
  const nActions = state.A.length;

  if (rng() < (state.epsilon ?? 0.1)) {
    const action = Math.floor(rng() * nActions);
    return {
      action,
      qValues: zeros(nActions).map((_, i) => (i === action ? 1 : 0)),
      featureContributions: zeros(context.length),
    };
  }

  const p = zeros(nActions);
  const contributions: number[][] = [];
  for (let a = 0; a < nActions; a++) {
    const A_inv = invertMatrix(state.A[a]);
    const theta = matVecMul(A_inv, state.b[a]);
    state.theta[a] = theta;
    p[a] = dot(theta, context);
    contributions[a] = theta.map((t, i) => t * context[i]);
  }

  const action = p.indexOf(Math.max(...p));
  return {
    action,
    qValues: p,
    featureContributions: contributions[action],
  };
}

export function epsilonGreedyUpdate(
  state: BanditState,
  action: number,
  context: number[],
  reward: number
): void {
  state.A[action] = addMat(state.A[action], outerProduct(context, context));
  state.b[action] = addVec(state.b[action], context.map((c) => c * reward));
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory
// ─────────────────────────────────────────────────────────────────────────────

export function createBanditState(
  algo: AlgoName,
  nFeatures: number,
  params?: { alpha?: number; v2?: number; epsilon?: number; lambda?: number }
): BanditState {
  const nActions = 4;
  switch (algo) {
    case "linucb":
      return createLinUCBState(nActions, nFeatures, params?.alpha ?? 1.0);
    case "linTS":
      return createLinTSState(nActions, nFeatures, params?.v2 ?? 1.0);
    case "epsilonGreedy":
      return createEpsilonGreedyState(
        nActions,
        nFeatures,
        params?.epsilon ?? 0.15
      );
    case "discountedLinUCB":
      return createDiscountedLinUCBState(
        nActions,
        nFeatures,
        params?.alpha ?? 1.0,
        params?.lambda ?? 0.995
      );
    default:
      throw new Error(`Unknown algorithm: ${algo}`);
  }
}

export function banditDecide(
  state: BanditState,
  algo: AlgoName,
  context: number[]
): DecisionResult {
  switch (algo) {
    case "linucb":
      return linucbDecide(state, context);
    case "linTS":
      return linTSDecide(state, context);
    case "epsilonGreedy":
      return epsilonGreedyDecide(state, context);
    case "discountedLinUCB":
      return discountedLinUCBDecide(state, context);
    default:
      throw new Error(`Unknown algorithm: ${algo}`);
  }
}

export function banditUpdate(
  state: BanditState,
  algo: AlgoName,
  action: number,
  context: number[],
  reward: number
): void {
  switch (algo) {
    case "linucb":
      linucbUpdate(state, action, context, reward);
      break;
    case "linTS":
      linTSUpdate(state, action, context, reward);
      break;
    case "epsilonGreedy":
      epsilonGreedyUpdate(state, action, context, reward);
      break;
    case "discountedLinUCB":
      discountedLinUCBUpdate(state, action, context, reward);
      break;
    default:
      throw new Error(`Unknown algorithm: ${algo}`);
  }
}
