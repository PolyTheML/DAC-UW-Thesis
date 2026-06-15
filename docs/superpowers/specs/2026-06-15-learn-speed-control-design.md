# Watch-it-Learn Speed Controls (Design Spec)

**Date:** 2026-06-15
**Status:** Approved in brainstorm (this session); ready for implementation plan.
**Scope:** Small enhancement to the just-built Underwriting Desk demo (`demo/desk/`, see [`2026-06-15-underwriting-desk-rebuild-design.md`](2026-06-15-underwriting-desk-rebuild-design.md)). Adds two user controls to the **Watch it Learn** view. No change to the Underwriting Desk view, the engine, or any thesis number.

## 1. Motivation

The Watch-it-Learn view animates one fixed bandit-vs-static run (LinUCB/LinTS, α/v² hard-coded to 1.0, fixed playback pacing). The user wants to **tune the speed of the learning curve** in two distinct senses, confirmed in brainstorm:

1. **How fast it *learns*** — the bandit's exploration rate, which changes the *shape* of the cumulative-reward curve.
2. **How fast it *plays*** — the on-screen animation pacing, for live control during the defense.

## 2. Goals / Non-goals

**Goals**
- Expose the bandit exploration rate as **behavior presets** (Greedy / Balanced / Exploratory) that re-run the live curve.
- Expose **animation playback speed** (Slow / Normal / Fast) as a client-only pacing control.
- Reuse the existing engine knobs (`LinUCB(alpha=…)`, `LinTS(v2=…)`); introduce no new modelling math.
- Preserve the canonical-vs-illustrative discipline exactly.

**Non-goals (unchanged / deferred):** the Underwriting Desk view; the canonical headline source; new algorithms; raw-number sliders (presets were chosen over continuous sliders); persisting control state across reloads.

## 3. Locked decisions (brainstorm 2026-06-15)

1. **Both** speeds are tunable (learning rate + animation playback).
2. **Control style = labeled presets** (segmented buttons), not continuous sliders.
3. **Exploration mapping is server-side** (in `learning.py`): the client sends a behavior label; the server resolves it to the right parameter for the selected algorithm and **echoes the resolved value** so the UI can display it.
4. **Default = Balanced** (α=1.0 / v²=1.0) — preserves today's behavior as the default.
5. **Preset anchors are thesis-grounded, adjustable constants** (see §4).

## 4. Exploration presets (re-run the curve)

The client sends one of `Greedy | Balanced | Exploratory`. The server maps it per algorithm:

| Preset | LinUCB `alpha` | LinTS `v2` | Meaning |
|--------|----------------|------------|---------|
| Greedy | 0.0 | 0.25 | exploit only (no UCB bonus) / tight posterior |
| **Balanced** (default) | 1.0 | 1.0 | thesis default; EXP-012 regret-minimizing α |
| Exploratory | 3.0 | 4.0 | heavy exploration / wide posterior |

These six values are module-level constants in `learning.py` (`EXPLORATION_PRESETS`), easy to retune if a punchier on-screen contrast is wanted later.

**Honesty note (carried into the demo, not a bug):** per EXP-011 the UCB bonus is *not* the load-bearing mechanism (Greedy-only α=0 ≈ Full LinUCB). So for **LinUCB**, Greedy and Balanced curves will look nearly identical — the true, counterintuitive finding. **LinTS**'s v² produces a more visible spread (v²=4 = noisier, wobblier early curve). This is acceptable and educationally honest.

## 5. Animation speed (client-only, instant)

Slow / Normal / Fast change *playback pacing only* — no re-run, no data change, no server call. Implementation: fixed 40 ms tick; vary the number of animation frames.

| Speed | Frames | Approx. duration |
|-------|--------|------------------|
| Slow | 160 | ~6.4 s |
| **Normal** (default) | 80 | ~3.2 s |
| Fast | 40 | ~1.6 s |

`stepSize = ceil(total_rounds / frames)`. The running animation reads the current stepSize each tick, so a speed change **applies live** to an in-progress animation (no restart). Normal = today's behavior.

## 6. Backend changes (`demo/desk/`)

**`learning.py`:**
- Add `EXPLORATION_PRESETS = {"Greedy": {...}, "Balanced": {...}, "Exploratory": {...}}` mapping preset → `{"alpha": float, "v2": float}`.
- `run_learn(algorithm, seed=42, n_rounds=2000, exploration="Balanced")`: resolve the preset; instantiate `LinUCB(alpha=preset["alpha"])` or `LinTS(v2=preset["v2"], seed=seed)`. Raise `ValueError` for an unknown preset.
- Payload gains: `"exploration": "<preset>"` and `"param": {"name": "alpha"|"v2", "value": <float>}` (the resolved value, for the UI readout).

**`app.py`:**
- `LearnRunIn` gains `exploration: str = Field("Balanced", pattern="^(Greedy|Balanced|Exploratory)$")`.
- `learn_run` passes `payload.exploration` through to `run_learn`.

## 7. Frontend changes (`demo/desk/static/`)

**`index.html`:** add two segmented control groups to the Watch-it-Learn toolbar — Exploration `[Greedy][Balanced][Exploratory]` and Speed `[Slow][Normal][Fast]` — plus a small `.seg`/`.seg.active` CSS rule for the active segment. A small readout shows the active resolved parameter (e.g., "α = 1.0 · Balanced").

**`learn.js`:**
- Track `exploration` (default "Balanced") and `speed` (default "Normal").
- Exploration button click → set state, mark active, call `loadAndReset()` (re-runs `/api/learn/run` with the new preset). Algorithm change continues to re-run and now carries the current preset.
- Speed button click → set state, mark active, recompute `stepSize`; if an animation is running, it picks up the new pace on the next tick (no restart).
- `loadAndReset()` sends `{ algorithm, seed: 42, n_rounds: N_ROUNDS, exploration }`; on response, update the readout from `data.param` (e.g., `α = 1.0`) and the `data.exploration` label.
- The persistent note stays "Illustrative · single seed (42)", now suffixed with the active preset (e.g., "· Exploratory").

## 8. Canonical vs illustrative discipline (unchanged)

The canonical headline strip stays `+25.2% · 20 seeds · p<0.001 · d=2.98` from `thesis_results.json`, regardless of controls. The live curve and lift readout remain single-seed **illustrative**, now additionally labelled with the active exploration preset. A non-Balanced preset is, if anything, *more* clearly illustrative. Never quote a live number as the result.

## 9. Testing (`tests/test_desk_app.py`)

- `/api/learn/run` with `exploration="Greedy"` returns 200; `data["param"]` is `{"name":"alpha","value":0.0}` for LinUCB.
- `/api/learn/run` with `exploration="Exploratory"` (LinTS) returns `{"name":"v2","value":4.0}`.
- Greedy vs Exploratory produce **different** adaptive trajectories (knob is actually wired through): `adaptive.cumulative` differs.
- Invalid `exploration` (e.g., `"Wild"`) → 422.
- Existing learn test updated to assert the new `exploration`/`param` keys exist with the default ("Balanced").

## 10. Files touched

- `demo/desk/learning.py` — presets + `run_learn(exploration=…)` + payload echo.
- `demo/desk/app.py` — `LearnRunIn.exploration` enum; pass-through.
- `demo/desk/static/learn.js` — two control groups, wiring, readout.
- `demo/desk/static/index.html` — toolbar markup + active-segment CSS.
- `tests/test_desk_app.py` — new + updated assertions.

## 11. Out of scope / risks

- **Continuous α/v² sliders** — explicitly rejected in favor of presets.
- **Per-algorithm visible spread differs** (LinUCB subtle per EXP-011; LinTS more visible) — intended; anchors are tunable constants if a stronger contrast is wanted.
- **Control-state persistence** across reloads — not needed.
- No change to Render config, the old demo, or the deferred cutover.
