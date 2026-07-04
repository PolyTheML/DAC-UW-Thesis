// Watch it Learn view: canonical headline + animated divergence chart + action mix.
// Two user controls (spec 2026-06-15-learn-speed-control-design):
//   • Exploration preset (Greedy/Balanced/Exploratory) — re-runs the curve; the server
//     resolves the preset to alpha (LinUCB) / v2 (LinTS) and echoes it in data.param.
//   • Animation speed (Slow/Normal/Fast) — client-only playback pacing, applied live.
const Learn = (function () {
  let chart = null;
  let data = null;       // last /api/learn/run payload
  let timer = null;
  let frame = 0;
  let exploration = 'Balanced'; // default preset = today's behaviour (alpha/v2 = 1.0)
  let speed = 'Normal';         // default pacing = today's behaviour (~80 frames)
  // Single-seed illustrative horizon: 3000 rounds reaches ≈ the canonical +25.2%
  // headline (single-seed +25.6%) and shows the full cold-start→divergence arc.
  const N_ROUNDS = 3000;
  // Animation pacing (spec §5): fixed 40 ms tick; vary the number of frames.
  const SPEED_FRAMES = { Slow: 160, Normal: 80, Fast: 40 };
  const ACTIONS = ['STANDARD', 'RATED', 'DECLINE', 'REFER'];

  async function renderHeadline() {
    const c = await API.canonical();
    document.getElementById('headline').innerHTML = `
      <div><div class="big">+${c.lift_pct}%</div><div class="tag">vs ${c.comparator}</div></div>
      <div class="tag">${c.n_seeds} seeds · p ${c.p_value} · d = ${c.cohen_d}</div>
      <div class="tag" title="${c.ceiling_note}">scope: admissible policies
        (ceiling: ${c.ceiling_policy})</div>
      <div class="tag">thesis Ch.5</div>`;
  }

  function buildChart() {
    const ctx = document.getElementById('chart').getContext('2d');
    chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [
        { label: 'Adaptive policy', data: [], borderColor: '#3b82f6',
          borderWidth: 2, pointRadius: 0, tension: .1 },
        { label: 'Static XGB', data: [], borderColor: '#93a1b5',
          borderWidth: 2, pointRadius: 0, borderDash: [5, 4], tension: .1 },
      ]},
      options: {
        animation: false, responsive: true,
        scales: { x: { ticks: { color: '#93a1b5', maxTicksLimit: 8 } },
                  y: { ticks: { color: '#93a1b5' } } },
        plugins: { legend: { labels: { color: '#e8edf4' } } },
      },
    });
  }

  function mixRows(mix) {
    return ACTIONS.map(a => {
      const pct = Math.round((mix[a] || 0) * 100);
      return `<div class="bar-row"><span>${a}</span>
        <div class="bar-track"><div class="bar" style="width:${Math.max(2,pct)}%"></div></div>
        <span>${pct}%</span></div>`;
    }).join('');
  }

  function drawTo(n) {
    chart.data.labels = data.rounds.slice(0, n);
    chart.data.datasets[0].data = data.adaptive.cumulative.slice(0, n);
    chart.data.datasets[1].data = data.static.cumulative.slice(0, n);
    chart.update();
    document.getElementById('round-readout').textContent = `round ${n}`;
    if (n >= data.rounds.length) {
      document.getElementById('lift-readout').textContent =
        `+${data.lift_pct}% (illustrative, seed ${data.seed})`;
    }
  }

  function stop() { if (timer) { clearInterval(timer); timer = null; } }

  // Frames-per-run depends on the live `speed` state, so the pace of an in-progress
  // animation changes on the next tick when the user clicks a Speed segment (spec §5).
  function currentStepSize() {
    const total = data.rounds.length;
    return Math.max(1, Math.ceil(total / SPEED_FRAMES[speed]));
  }

  function play() {
    if (!data) return;
    stop();
    const total = data.rounds.length;
    timer = setInterval(() => {
      frame = Math.min(total, frame + currentStepSize()); // read speed live each tick
      drawTo(frame);
      if (frame >= total) {
        stop();
        document.getElementById('mix-early').innerHTML = mixRows(data.adaptive.early_mix);
        document.getElementById('mix-late').innerHTML = mixRows(data.adaptive.late_mix);
      }
    }, 40);
  }

  function setActive(groupSel, btn) {
    document.querySelectorAll(`${groupSel} .seg-btn`).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }

  let isLoading = false;

  function setBusy(busy) {
    document.getElementById('btn-play').disabled = busy;
    document.getElementById('btn-reset').disabled = busy;
  }

  function showError(msg) {
    let el = document.getElementById('error-banner');
    if (!el) {
      el = document.createElement('div');
      el.id = 'error-banner';
      el.className = 'learn-error';
      document.getElementById('learn-card').prepend(el);
    }
    el.innerHTML = '';
    const span = document.createElement('span');
    span.textContent = msg;
    const btn = document.createElement('button');
    btn.textContent = 'Retry';
    btn.addEventListener('click', loadAndReset);
    el.append(span, btn);
  }

  function hideError() {
    const el = document.getElementById('error-banner');
    if (el) el.remove();
  }

  async function loadAndReset() {
    if (isLoading) return;
    stop(); frame = 0;
    isLoading = true;
    setBusy(true);
    hideError();
    document.getElementById('lift-readout').textContent = '';
    document.getElementById('learn-note').textContent =
      'Simulating 3,000 applicant decisions — the first run can take up to a minute on the free server…';
    const algo = document.getElementById('algo').value;
    try {
      data = await API.learn({ algorithm: algo, seed: 42, n_rounds: N_ROUNDS, exploration });
      const sym = data.param.name === 'alpha' ? 'α' : 'v²';
      document.getElementById('param-readout').textContent =
        `${sym} = ${data.param.value} · ${data.exploration}`;
      document.getElementById('learn-note').textContent =
        `${data.illustrative_note} · ${data.exploration}`;
      document.getElementById('mix-early').innerHTML = '';
      document.getElementById('mix-late').innerHTML = '';
      drawTo(1);
    } catch (e) {
      showError('Could not reach the simulation server — it may be waking up (free tier). Retry in a few seconds.');
    } finally {
      isLoading = false;
      setBusy(false);
    }
  }

  async function init() {
    try {
      await renderHeadline();
    } catch (e) {
      document.getElementById('headline').innerHTML =
        '<span class="muted">Headline unavailable — server waking up. It will appear on the next reload.</span>';
    }
    buildChart();
    document.getElementById('btn-play').addEventListener('click', play);
    document.getElementById('btn-reset').addEventListener('click', loadAndReset);
    document.getElementById('algo').addEventListener('change', loadAndReset);
    document.querySelectorAll('#seg-exploration .seg-btn').forEach(btn =>
      btn.addEventListener('click', () => {
        exploration = btn.dataset.exploration;
        setActive('#seg-exploration', btn);
        loadAndReset(); // re-run the curve with the new preset
      }));
    document.querySelectorAll('#seg-speed .seg-btn').forEach(btn =>
      btn.addEventListener('click', () => {
        speed = btn.dataset.speed;
        setActive('#seg-speed', btn);
        // no re-run / no restart: a running animation picks up the new pace next tick
      }));
    await loadAndReset();
  }

  return { init };
})();
