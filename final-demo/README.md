# DAC-UW Thesis Defense -- Offline Demo Package

**Defense-ready standalone build** of the adaptive health insurance underwriting demo.

## Quick Start (Windows)

Double-click `start-demo.bat` or run:
```bash
node server.js
```

Open http://localhost:3000 in your browser.

## Requirements

- Node.js 18+ (LTS recommended)
- ~150 MB disk space
- No internet connection required
- No build step required

## Demo Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page with links to all demos |
| `/demo` | Main underwriting dashboard (LinUCB / LinTS / ε-Greedy) |
| `/hitl` | Human-in-the-Loop demo with review queue |
| `/drift` | Drift detection race (Static vs Discounted LinUCB) |

## What to Show the Committee

1. **Main dashboard** (`/demo`): Single applicant → bandit decision → PSI monitor
2. **HITL** (`/hitl`): Toggle simulated underwriter → watch queue → override decisions → alignment score improves
3. **Drift** (`/drift`): Run "Hep-B Outbreak" scenario → static bandit fails, adaptive bandit recovers → PSI turns RED then GREEN

## Troubleshooting

- If port 3000 is taken: `set PORT=3001 && node server.js`
- If Node is not found: ensure Node.js is installed and on PATH

## Built

2026-04-29 from commit `454690e`
