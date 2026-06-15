// Watch it Learn view: canonical headline + animated divergence chart + action mix.
const Learn = (function () {
  let chart = null;
  let data = null;       // last /api/learn/run payload
  let timer = null;
  let frame = 0;
  // Single-seed illustrative horizon: 3000 rounds reaches ≈ the canonical +25.2%
  // headline (single-seed +25.6%) and shows the full cold-start→divergence arc.
  const N_ROUNDS = 3000;
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

  function play() {
    if (!data) return;
    stop();
    const total = data.rounds.length;
    const stepSize = Math.max(1, Math.floor(total / 80)); // ~80 frames
    timer = setInterval(() => {
      frame = Math.min(total, frame + stepSize);
      drawTo(frame);
      if (frame >= total) {
        stop();
        document.getElementById('mix-early').innerHTML = mixRows(data.adaptive.early_mix);
        document.getElementById('mix-late').innerHTML = mixRows(data.adaptive.late_mix);
      }
    }, 40);
  }

  async function loadAndReset() {
    stop(); frame = 0;
    document.getElementById('lift-readout').textContent = '';
    document.getElementById('learn-note').textContent = 'Running…';
    const algo = document.getElementById('algo').value;
    data = await API.learn({ algorithm: algo, seed: 42, n_rounds: N_ROUNDS });
    document.getElementById('learn-note').textContent = data.illustrative_note;
    document.getElementById('mix-early').innerHTML = '';
    document.getElementById('mix-late').innerHTML = '';
    drawTo(1);
  }

  async function init() {
    await renderHeadline();
    buildChart();
    document.getElementById('btn-play').addEventListener('click', play);
    document.getElementById('btn-reset').addEventListener('click', loadAndReset);
    document.getElementById('algo').addEventListener('change', loadAndReset);
    await loadAndReset();
  }

  return { init };
})();
