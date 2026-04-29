# Adaptive Health Insurance Underwriting Demo

**Thesis**: *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*  
**Author**: Chanpoly (ITC Cambodia) · Advisor: Has Sothea · DAC

A full-stack Next.js 14 (App Router) demo that ports the thesis Python experiments to an interactive web application deployable on Vercel.

---

## What's inside

| Layer | File | Purpose |
|-------|------|---------|
| Config | `config/underwriting-features.ts` | Source-of-truth feature definitions, action space, reward function, PSI references, and algorithm parameters — extracted directly from the Python codebase. |
| Bandits | `lib/bandits.ts` | LinUCB, Linear Thompson Sampling, and ε-Greedy implemented in TypeScript with small-matrix linear algebra. |
| PSI | `lib/psi.ts` | Population Stability Index computation matching the Python fairness audit. |
| Session | `lib/session-store.ts` | In-memory session state (bandit matrices, decision history, approved-portfolio distributions). |
| API | `app/api/decide/route.ts` | Edge Runtime API that runs the bandit decision server-side. |
| API | `app/api/session/route.ts` | Fetches session history and current PSI values. |
| UI | `components/ApplicantForm.tsx` | 100% config-driven form — no hardcoded field names. |
| UI | `components/DecisionOutput.tsx` | Action badge, risk score, Q-values, top feature contributions. |
| UI | `components/LearningCharts.tsx` | Cumulative reward & regret curves via Recharts. |
| UI | `components/PSIMonitor.tsx` | PSI bar chart per feature with Stable/Watch/Alert thresholds. |
| UI | `components/AlgorithmSelector.tsx` | Toggle between LinUCB / Thompson Sampling / ε-Greedy with parameter slider. |

---

## How to run locally

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## How to deploy to Vercel

1. Push the `web/` directory to a Git repository.
2. Import the repo on [vercel.com](https://vercel.com).
3. Vercel auto-detects Next.js via `vercel.json`.
4. No environment variables are required.

---

## How to update features when the codebase changes

1. **Regenerate the Cambodia dataset** (if distributions changed):
   ```bash
   python case-study/generate_cambodia_dataset.py
   ```

2. **Recompute normalization statistics**:
   Run the Python snippet in `config/underwriting-features.ts` comments or use:
   ```bash
   python -c "import pandas as pd; df=pd.read_csv('case-study/cambodia_dataset.csv'); ..."
   ```
   Paste the resulting means/stds into `BANDIT_FEATURE_STATS`.

3. **Recompute PSI reference distributions**:
   Update `PSI_REFERENCE` with new value counts or percentile bins.

4. **Update reward logic**:
   If `expected_rewards()` or `make_reward_simulator()` changes in Python, port the new formula to `computeExpectedRewards()` in `config/underwriting-features.ts`.

5. **Update feature list**:
   If new input features are added to the preprocessor in `underwriting_bandit.py`, add them to `INPUT_FEATURES` in the config. The form and bandit vector will adapt automatically because every component is driven by the config arrays.

---

## Architecture notes

- **Edge Runtime**: `app/api/decide/route.ts` uses `export const runtime = "edge"` for low latency. The bandit matrices (4 × 27×27) are tiny and fit easily in Edge memory.
- **Session state**: Stored in a global `Map`. This is fine for a demo but should be replaced with Redis / Vercel KV for production scale.
- **Deterministic rewards**: The API uses the deterministic `expected_rewards` oracle rather than stochastic sampling. This makes the demo reproducible and stable across refreshes.
- **No hardcoded feature names**: Every component imports `INPUT_FEATURES`, `BANDIT_FEATURE_ORDER`, or `BANDIT_FEATURE_STATS` from the config. Adding or removing a feature in the config automatically updates the form, the context vector builder, and the decision output.
