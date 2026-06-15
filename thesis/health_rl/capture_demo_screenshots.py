"""Capture real FastAPI demo screenshots for the defense deck (v3 Live Demo slide).

Launches uvicorn (demo.main:app) on a free port, drives the SPA with Playwright
chromium, captures three panels, then tears uvicorn down. Outputs PNGs into
figures/demo_shots/. Safe to re-run; failures degrade to "fewer shots" (the
builder falls back to labeled placeholders).

Run:
    python thesis/health_rl/capture_demo_screenshots.py
Prereq (one-time): python -m playwright install chromium
"""
from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "thesis" / "health_rl" / "figures" / "demo_shots"
PORT = 8123
BASE = f"http://127.0.0.1:{PORT}"


def _wait_up(timeout=40):
    for _ in range(timeout * 2):
        try:
            urllib.request.urlopen(BASE, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def _click_panel(page, label):
    """Best-effort: click a tab/button whose visible text matches `label`."""
    try:
        page.get_by_text(label, exact=False).first.click(timeout=2500)
        page.wait_for_timeout(1200)
    except Exception as e:
        print(f"  [warn] could not open '{label}': {e}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "demo.main:app", "--port", str(PORT)],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not _wait_up():
            print("uvicorn did not come up; aborting (placeholders will be used)")
            return 1
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(BASE, wait_until="networkidle")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT_DIR / "shot_dashboard.png"))
            print("  captured shot_dashboard.png")

            _click_panel(page, "Pricing")
            page.screenshot(path=str(OUT_DIR / "shot_pricing.png"))
            print("  captured shot_pricing.png")

            _click_panel(page, "Human")        # 'Human-in-the-loop' tab
            page.screenshot(path=str(OUT_DIR / "shot_hitl.png"))
            print("  captured shot_hitl.png")
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except Exception:
            server.kill()
    shots = sorted(OUT_DIR.glob("shot_*.png"))
    print(f"wrote {len(shots)} demo screenshots -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
