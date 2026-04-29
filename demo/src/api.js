const BASE_URL = import.meta.env.VITE_API_URL || "https://dac-healthprice-api.onrender.com";

async function api(path, opts = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

export const listAlgorithms = () => api("/api/v1/rl/algorithms");
export const getApplicants = (page = 1, limit = 50) =>
  api(`/api/v1/rl/applicants?page=${page}&limit=${limit}`);
export const simulate = (body) =>
  api("/api/v1/rl/simulate", { method: "POST", body: JSON.stringify(body) });
export const decide = (body) =>
  api("/api/v1/rl/decide", { method: "POST", body: JSON.stringify(body) });
export const fairness = (algorithm, n_rounds = 5000, seed = 42) =>
  api(`/api/v1/rl/fairness?algorithm=${algorithm}&n_rounds=${n_rounds}&seed=${seed}`);
