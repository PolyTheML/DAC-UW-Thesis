# Adaptive Health Insurance Underwriting — Final Defense Demo

**Author:** Chanpoly (ITC Cambodia)  
**Defense date:** ~2026-06-26  
**Package created:** 2026-04-29

---

## What's Included

This is a self-contained, offline-capable demo of the thesis:

> *"Adaptive Health Insurance Underwriting via Contextual Bandits: A Reinforcement Learning Approach for Cambodia"*

### Three Interactive Demos

| Demo | Route | What It Shows |
|------|-------|---------------|
| **Standard** | `/demo` | LinUCB / LinTS / ε-Greedy on single applicants with live learning curves + PSI |
| **Human-in-the-Loop** | `/hitl` | Bandit queues REFER cases for human override, learns from feedback, tracks alignment |
| **Drift Detection** | `/drift` | Static LinUCB fails vs. Discounted LinUCB recovers when a Hep-B outbreak shifts the applicant pool |

### Experiments (Python)

| Experiment | File | Key Result |
|------------|------|------------|
| EXP-005 | `../stress_testing/rl/experiments/exp_005_underwriting_convergence.py` | LinUCB +67% reward vs Static XGB |
| EXP-006 | `../stress_testing/rl/experiments/exp_006_fairness_audit.py` | No demographic parity violation; PSI GREEN |
| EXP-007 | `../stress_testing/rl/experiments/exp_007_benchmark_comparison.py` | LinTS lowest regret ($5,641) |
| EXP-008 | `../stress_testing/rl/experiments/exp_008_human_in_the_loop.py` | HITL +4.3% vs baseline; 5% human cost |

---

## How to Run (Defense Day)

### Option 1: Node.js Server (Recommended — full interactivity)

Requires **Node.js 18+** installed on the defense laptop.

```powershell
# 1. Navigate to this folder
cd final-demo

# 2. Start the server
node server.js

# 3. Open browser
cmd /c start http://localhost:3000
```

All three demos will work with full API routes (bandit decisions, simulations, PSI computation).

### Option 2: Static Export (Limited — read-only pages)

If Node.js is not available, open `dist/index.html` in a browser. The landing page and pre-rendered content will display, but interactive simulations require the server.

---

## Demo Talking Points

### Standard Demo (`/demo`)
1. Configure an applicant (e.g., 55-year-old smoker with TB)
2. Select LinUCB, run decision
3. Show: action badge, risk score, Q-values, top-5 feature contributions
4. Run 10–15 decisions, watch cumulative reward + regret curves grow
5. Show PSI monitor turning GREEN/AMBER/RED as approved portfolio drifts

### Human-in-the-Loop Demo (`/hitl`)
1. Enable "Simulated Underwriter" (conservatism = 0.5)
2. Submit applicants until bandit selects REFER
3. Show: case appears in queue, auto-resolves in ~300ms
4. Watch alignment score converge (~54%) and human cost accumulate
5. Toggle to manual mode, override a case yourself, see bandit adapt

### Drift Detection Demo (`/drift`)
1. Run race with default params (2,000 rounds, drift at 1,000)
2. Point to the red "Hep-B Outbreak — Preah Sihanouk" marker
3. Explain: static bandit's reward curve flattens, adaptive bandit bends back up
4. Show final metrics: +X% improvement, regret reduction %
5. Reference PSI status: static = RED (3.007), adaptive = GREEN (recovered)

---

## Tech Stack

- Next.js 14 (App Router, Edge Runtime)
- TypeScript bandit engine: LinUCB, LinTS, ε-Greedy, DiscountedLinUCB
- Custom linear algebra: Gauss-Jordan, Cholesky, MVN sampling (27×27 matrices)
- PSI computation matching Python fairness audit
- No external backend dependency — all bandit math runs server-side

---

## Files

```
final-demo/
  README.md          ← this file
  server.js          ← Next.js standalone server
  package.json       ← minimal runtime dependencies
  node_modules/      ← bundled dependencies
  dist/              ← built static assets + prerendered pages
```

---

## Troubleshooting

**Port 3000 is occupied:**
```powershell
$env:PORT = 3001; node server.js
```

**Windows Defender blocks Node.js:** Allow `node.exe` through firewall.

**Browser shows "Cannot connect":** Make sure `server.js` is running and try `http://127.0.0.1:3000` instead of `localhost`.

---

*Built by Kimi (experiment implementation) and Claude (thesis writing). Push-to-main collaboration via COLLAB.md.*
