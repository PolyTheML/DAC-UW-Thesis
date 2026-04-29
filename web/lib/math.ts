/**
 * Lightweight linear-algebra utilities for bandit algorithms.
 * Operates on small matrices (27×27) so simple nested-array implementations
 * are more than fast enough.
 */

export function zeros(n: number): number[] {
  return new Array(n).fill(0);
}

export function eye(n: number): number[][] {
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))
  );
}

export function matVecMul(M: number[][], v: number[]): number[] {
  return M.map((row) => row.reduce((sum, val, j) => sum + val * v[j], 0));
}

export function dot(a: number[], b: number[]): number {
  return a.reduce((sum, val, i) => sum + val * b[i], 0);
}

export function outerProduct(a: number[], b: number[]): number[][] {
  return a.map((ai) => b.map((bj) => ai * bj));
}

export function addMat(A: number[][], B: number[][]): number[][] {
  return A.map((row, i) => row.map((val, j) => val + B[i][j]));
}

export function scaleMat(A: number[][], s: number): number[][] {
  return A.map((row) => row.map((val) => val * s));
}

export function scaleVec(v: number[], s: number): number[] {
  return v.map((val) => val * s);
}

export function addVec(a: number[], b: number[]): number[] {
  return a.map((val, i) => val + b[i]);
}

/**
 * Matrix inversion via Gauss-Jordan elimination with partial pivoting.
 */
export function invertMatrix(M: number[][]): number[][] {
  const n = M.length;
  const A = M.map((row) => [...row]);
  const I = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))
  );

  for (let i = 0; i < n; i++) {
    let pivot = A[i][i];
    if (Math.abs(pivot) < 1e-10) {
      let maxRow = i;
      for (let k = i + 1; k < n; k++) {
        if (Math.abs(A[k][i]) > Math.abs(A[maxRow][i])) maxRow = k;
      }
      [A[i], A[maxRow]] = [A[maxRow], A[i]];
      [I[i], I[maxRow]] = [I[maxRow], I[i]];
      pivot = A[i][i];
    }

    for (let j = 0; j < n; j++) {
      A[i][j] /= pivot;
      I[i][j] /= pivot;
    }

    for (let k = 0; k < n; k++) {
      if (k !== i) {
        const factor = A[k][i];
        for (let j = 0; j < n; j++) {
          A[k][j] -= factor * A[i][j];
          I[k][j] -= factor * I[i][j];
        }
      }
    }
  }

  return I;
}

/**
 * Cholesky decomposition: A = L * L^T  (A must be symmetric positive-definite).
 * Returns lower-triangular L.
 */
export function cholesky(A: number[][]): number[][] {
  const n = A.length;
  const L: number[][] = Array.from({ length: n }, () => new Array(n).fill(0));

  for (let i = 0; i < n; i++) {
    for (let j = 0; j <= i; j++) {
      let sum = 0;
      for (let k = 0; k < j; k++) sum += L[i][k] * L[j][k];
      if (i === j) {
        const diag = A[i][i] - sum;
        // Add tiny jitter for numerical stability
        L[i][j] = Math.sqrt(Math.max(diag, 1e-12));
      } else {
        L[i][j] = (A[i][j] - sum) / L[j][j];
      }
    }
  }
  return L;
}

/**
 * Sample one standard-normal variate via Box-Muller.
 */
export function randn(rng: () => number): number {
  let u = 0,
    v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

/**
 * Sample from multivariate normal N(mean, cov).
 * Uses Cholesky decomposition of cov.
 */
export function sampleMultivariateNormal(
  mean: number[],
  cov: number[][],
  rng: () => number
): number[] {
  const n = mean.length;
  const L = cholesky(cov);
  const z = Array.from({ length: n }, () => randn(rng));
  const result = new Array(n).fill(0);

  for (let i = 0; i < n; i++) {
    let sum = 0;
    for (let j = 0; j <= i; j++) {
      sum += L[i][j] * z[j];
    }
    result[i] = mean[i] + sum;
  }
  return result;
}
