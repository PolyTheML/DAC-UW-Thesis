# DAC Thesis Demo — Adaptive Underwriting Bandit

Standalone React demo app for the thesis: *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*.

## Features

- **Simulator** — Run LinUCB, LinTS, Epsilon-Greedy, or Static XGB on the Cambodia dataset and view cumulative reward / regret curves.
- **Benchmark** — Compare all 4 algorithms side-by-side with bar charts.
- **Fairness Audit** — Compute PSI and approval-rate parity by region and occupation.
- **Applicant Explorer** — Step through individual applicants and see the bandit's decision + expected rewards for all 4 actions.

## Tech Stack

- React 19 + Vite
- Recharts (visualisations)
- DAC HealthPrice API backend (`https://dac-healthprice-api.onrender.com`)

## Local Development

```bash
npm install
npm run dev
```

The dev server proxies `/api` requests to the Render backend automatically.

## Environment Variables

Create `.env.local`:

```
VITE_API_URL=https://dac-healthprice-api.onrender.com
```

## Build for Production

```bash
npm run build
```

Output goes to `dist/`.

## Deploy to Vercel

### Option 1: Vercel CLI

```bash
npm i -g vercel
vercel --prod
```

### Option 2: GitHub → Vercel

1. Push this `demo/` folder to a GitHub repo (e.g. `PolyTheML/dac-thesis-bandit-demo`).
2. Import the repo in [Vercel Dashboard](https://vercel.com).
3. Set framework preset to **Vite**.
4. Add environment variable `VITE_API_URL=https://dac-healthprice-api.onrender.com`.
5. Deploy.

## Backend Requirements

The demo expects the DAC platform backend to expose these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rl/algorithms` | GET | List algorithms |
| `/api/v1/rl/applicants` | GET | Paginated dataset |
| `/api/v1/rl/simulate` | POST | Run simulation |
| `/api/v1/rl/decide` | POST | Single decision |
| `/api/v1/rl/fairness` | GET | Fairness audit |

These routes are defined in `C:\DAC-UW-Agent\app\routes\bandit_underwriting.py`.
