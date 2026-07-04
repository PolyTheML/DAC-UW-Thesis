# Underwriting Desk — Streamlit port

Pragmatic Streamlit port of the FastAPI/vanilla-JS Underwriting Desk
(`demo/desk/`), built 2026-07-04. Reuses `demo/desk/scoring.py` and
`demo/desk/learning.py` directly — no duplicated modelling math.

## One-command launch

From the repository root:

```bash
pip install -r demo/streamlit_app/requirements.txt   # streamlit only; other deps in top-level requirements.txt
streamlit run demo/streamlit_app/app.py
```

Opens at <http://localhost:8501>.

## What's different from the FastAPI version

Everything is at feature parity **except** the "Watch it Learn" animation.
Streamlit has no client-side animation-loop primitive (no `setInterval`
equivalent), so the Play/Reset/Speed controls are replaced by a **round
scrub slider** — drag it to see the cumulative-reward divergence build up,
instead of watching it auto-play. The live lift-at-this-round readout
updates as you scrub, which the original JS version didn't show mid-animation.

Everything else is full parity:
- 4 preset applicant profiles (Low/Borderline/High Risk, Referral case) +
  Load CDHS sample + Clear
- Decision badge, confidence bar (τ=6 softmax margin, illustrative)
- LinUCB-vs-Static-XGB side-by-side comparison card with real threshold reasoning
- HITL card on REFER decisions with canonical EXP-008 numbers
- Persistent fairness guardrail panel (region/occupation PSI, EXP-006)
- Algorithm select + exploration presets (Greedy/Balanced/Exploratory) +
  continuous α override slider for LinUCB

## Deploying to Streamlit Community Cloud

1. Push this branch to GitHub (already done for `thesis/ch5-structural-pass`).
2. On share.streamlit.io: New app → pick this repo/branch → main file path
   `demo/streamlit_app/app.py`.
3. Streamlit Cloud auto-detects `demo/streamlit_app/requirements.txt` as the
   app's own deps; it does **not** automatically pick up the top-level
   `requirements.txt`. If the deploy fails on a missing package (numpy,
   pandas, scikit-learn, xgboost), add an "Advanced settings" dependency
   file pointing at the repo-root `requirements.txt`, or copy the needed
   lines into `demo/streamlit_app/requirements.txt`.
4. `.streamlit/config.toml` at the repo root sets the dark theme; Streamlit
   Cloud picks it up automatically since it's at the repo root.

## Tests

```bash
python -m pytest tests/test_streamlit_app.py -q
```

Uses `streamlit.testing.v1.AppTest` (no browser needed) to smoke-test app
boot and preset-button decisions.
