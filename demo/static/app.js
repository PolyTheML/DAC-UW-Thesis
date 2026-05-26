/**
 * Actuarial Reward Simulator — Frontend
 * FastAPI + vanilla JS + Chart.js
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const charts = {};

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function fmtMoney(n) {
  if (n === undefined || n === null) return '—';
  const s = n < 0 ? '-$' : '$';
  return s + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function fmtNum(n, d = 2) {
  if (n === undefined || n === null) return '—';
  return n.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

function entropy(distObj) {
  let e = 0;
  Object.values(distObj).forEach(p => {
    if (p > 0) e -= p * Math.log(p);
  });
  return e;
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function apiGet(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------
function switchTab(name) {
  ['pricing', 'arena', 'benchmark', 'hitl'].forEach(t => {
    document.getElementById(`panel-${t}`).classList.toggle('hidden', t !== name);
    const btn = document.getElementById(`tab-${t}`);
    if (t === name) {
      btn.classList.remove('tab-inactive');
      btn.classList.add('tab-active');
    } else {
      btn.classList.remove('tab-active');
      btn.classList.add('tab-inactive');
    }
  });
}

// ---------------------------------------------------------------------------
// Applicant form (shared input — drives the Pricing Engine tab)
// ---------------------------------------------------------------------------
function getFormData() {
  const conds = [];
  document.querySelectorAll('.cond-check:checked').forEach(cb => conds.push(cb.value));
  return {
    age: parseInt(document.getElementById('age').value),
    gender: document.getElementById('gender').value,
    bmi: parseFloat(document.getElementById('bmi').value),
    is_smoking: document.getElementById('is_smoking').checked ? 1 : 0,
    alcohol_use: document.getElementById('alcohol_use').checked ? 1 : 0,
    is_exercise: document.getElementById('is_exercise').checked ? 1 : 0,
    has_family_history: document.getElementById('has_family_history').checked ? 1 : 0,
    monthly_income_usd: parseFloat(document.getElementById('monthly_income_usd').value),
    pre_existing_conditions: conds.join(', '),
    region: document.getElementById('region').value,
    occupation: document.getElementById('occupation').value,
    education: document.getElementById('education').value,
    wealth_quintile: document.getElementById('wealth_quintile').value,
    self_reported_health: document.getElementById('self_reported_health').value,
    mortality_multiplier: parseFloat(document.getElementById('mortality_multiplier').value),
  };
}

async function loadRandomApplicant() {
  const data = await apiGet('/api/applicant/random');
  const a = data.applicant;
  document.getElementById('age').value = a.age;
  document.getElementById('gender').value = a.gender;
  document.getElementById('bmi').value = a.bmi;
  document.getElementById('is_smoking').checked = !!a.is_smoking;
  document.getElementById('alcohol_use').checked = !!a.alcohol_use;
  document.getElementById('is_exercise').checked = !!a.is_exercise;
  document.getElementById('has_family_history').checked = !!a.has_family_history;
  document.getElementById('monthly_income_usd').value = a.monthly_income_usd;
  document.getElementById('region').value = a.region;
  document.getElementById('occupation').value = a.occupation;
  document.getElementById('education').value = a.education;
  document.getElementById('wealth_quintile').value = a.wealth_quintile;
  document.getElementById('self_reported_health').value = a.self_reported_health;
  document.getElementById('mortality_multiplier').value = a.mortality_multiplier;
  document.getElementById('mort-label').innerText = a.mortality_multiplier;

  // Conditions
  const conds = (a.pre_existing_conditions || '').split(',').map(s => s.trim()).filter(Boolean);
  document.querySelectorAll('.cond-check').forEach(cb => {
    cb.checked = conds.includes(cb.value);
  });

  runPricingOptimize();
}

// ---------------------------------------------------------------------------
// Pricing Engine
// ---------------------------------------------------------------------------

async function runPricingOptimize() {
  const body = getFormData();
  body.mode = document.getElementById('pricing-mode').value;
  body.adverse_factor = parseFloat(document.getElementById('pricing-adverse').value);

  document.getElementById('pricing-spinner').classList.remove('hidden');
  document.getElementById('pricing-btn-text').textContent = 'Optimising...';

  try {
    const data = await apiPost('/api/pricing/optimize', body);

    // Summary cards
    const summary = document.getElementById('pricing-summary');
    summary.innerHTML = `
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Optimal Multiplier</div>
        <div class="text-xl font-bold text-thesis-600 mt-1">${fmtNum(data.optimal_multiplier, 2)}×</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Premium (USD/yr)</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${fmtMoney(data.optimal_premium_usd)}</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Expected Profit</div>
        <div class="text-xl font-bold ${data.optimal_expected_profit >= 0 ? 'text-gray-900' : 'text-red-600'} mt-1">${fmtMoney(data.optimal_expected_profit)}</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">P(Accept)</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${(data.optimal_p_accept * 100).toFixed(1)}%</div>
      </div>
    `;

    // Profit curve
    renderPricingCurve(data.curve, data.optimal_multiplier);

    // Legacy comparison
    const tbody = document.getElementById('pricing-legacy-body');
    const legacy = data.legacy;
    const actions = ['STANDARD', 'RATED', 'DECLINE', 'REFER'];
    const rowLabels = ['Expected Reward (USD)'];
    tbody.innerHTML = `
      <tr class="hover:bg-gray-50 transition">
        <td class="px-4 py-3 font-medium text-gray-700">Expected Reward</td>
        ${actions.map(a => `<td class="px-4 py-3 text-right font-mono ${legacy[a] >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(legacy[a])}</td>`).join('')}
      </tr>
      <tr class="hover:bg-gray-50 transition">
        <td class="px-4 py-3 font-medium text-gray-700">Diff vs Optimal</td>
        ${actions.map(a => {
          const diff = legacy[a] - data.optimal_expected_profit;
          return `<td class="px-4 py-3 text-right font-mono ${diff >= 0 ? 'text-green-600' : 'text-red-600'}">${diff >= 0 ? '+' : ''}${fmtMoney(diff)}</td>`;
        }).join('')}
      </tr>
    `;

  } catch (e) {
    alert('Pricing optimisation failed: ' + e.message);
  } finally {
    document.getElementById('pricing-spinner').classList.add('hidden');
    document.getElementById('pricing-btn-text').textContent = 'Optimise Premium';
  }
}

function renderPricingCurve(curve, optimalMultiplier) {
  const ctx = document.getElementById('pricing-curve-chart').getContext('2d');
  const mults = curve.map(c => c.multiplier);
  const profits = curve.map(c => c.expected_profit);
  const pAccs = curve.map(c => c.p_accept * 100);
  const optIdx = mults.findIndex(m => Math.abs(m - optimalMultiplier) < 0.001);
  const pointRadii = mults.map((_, i) => i === optIdx ? 6 : 0);
  const pointColors = mults.map((_, i) => i === optIdx ? '#ef4444' : '#2E5FA3');

  if (charts.pricingCurve) charts.pricingCurve.destroy();

  charts.pricingCurve = new Chart(ctx, {
    type: 'line',
    data: {
      labels: mults,
      datasets: [
        {
          label: 'Expected Profit (USD)',
          data: profits,
          borderColor: '#2E5FA3',
          backgroundColor: '#2E5FA315',
          fill: true,
          pointRadius: pointRadii,
          pointBackgroundColor: pointColors,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          tension: 0.4,
          borderWidth: 2,
          yAxisID: 'y',
        },
        {
          label: 'P(Accept) %',
          data: pAccs,
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          fill: false,
          pointRadius: 0,
          tension: 0.4,
          borderWidth: 2,
          borderDash: [5, 5],
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 }, usePointStyle: true } },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              if (ctx.dataset.label === 'Expected Profit (USD)') {
                return `Profit: ${fmtMoney(ctx.raw)} @ ${ctx.label}×`;
              }
              return `${ctx.dataset.label}: ${fmtNum(ctx.raw, 1)}%`;
            }
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Premium Multiplier' },
          grid: { display: false },
        },
        y: {
          title: { display: true, text: 'Expected Profit (USD)' },
          grid: { color: '#f3f4f6' },
        },
        y1: {
          position: 'right',
          title: { display: true, text: 'P(Accept) %' },
          grid: { display: false },
          min: 0,
          max: 100,
        }
      }
    }
  });
}

async function runPricingBatch() {
  const seed = parseInt(document.getElementById('pricing-batch-seed').value);

  document.getElementById('batch-spinner').classList.remove('hidden');
  document.getElementById('batch-btn-text').textContent = 'Running...';

  try {
    const data = await apiPost('/api/pricing/batch', {
      algorithm: 'LinUCB', n_rounds: 2000, seed, alpha: 1.0, epsilon: 0.1, v2: 1.0
    });

    const s = data.summary;
    const summary = document.getElementById('batch-summary');
    summary.innerHTML = `
      <div class="bg-gray-50 rounded-lg border border-gray-100 p-3">
        <div class="text-xs font-medium text-gray-500 uppercase">Avg Multiplier</div>
        <div class="text-lg font-bold text-gray-900 mt-1">${fmtNum(s.avg_multiplier, 3)}×</div>
      </div>
      <div class="bg-gray-50 rounded-lg border border-gray-100 p-3">
        <div class="text-xs font-medium text-gray-500 uppercase">Median</div>
        <div class="text-lg font-bold text-gray-900 mt-1">${fmtNum(s.median_multiplier, 3)}×</div>
      </div>
      <div class="bg-gray-50 rounded-lg border border-gray-100 p-3">
        <div class="text-xs font-medium text-gray-500 uppercase">Std Dev</div>
        <div class="text-lg font-bold text-gray-900 mt-1">${fmtNum(s.std_multiplier, 3)}</div>
      </div>
      <div class="bg-gray-50 rounded-lg border border-gray-100 p-3">
        <div class="text-xs font-medium text-gray-500 uppercase">Min / Max</div>
        <div class="text-lg font-bold text-gray-900 mt-1">${fmtNum(s.min_multiplier, 2)} – ${fmtNum(s.max_multiplier, 2)}</div>
      </div>
      <div class="bg-gray-50 rounded-lg border border-gray-100 p-3">
        <div class="text-xs font-medium text-gray-500 uppercase">Avg Profit</div>
        <div class="text-lg font-bold text-gray-900 mt-1">${fmtMoney(s.avg_expected_profit)}</div>
      </div>
    `;

    renderBatchHistogram(data.histogram);

    // Table (top 20)
    const tbody = document.getElementById('batch-table-body');
    tbody.innerHTML = '';
    data.results.slice(0, 20).forEach(r => {
      const a = r.applicant;
      const row = document.createElement('tr');
      row.className = 'hover:bg-gray-50 transition';
      row.innerHTML = `
        <td class="px-3 py-2 text-gray-700">${a.age}</td>
        <td class="px-3 py-2 text-gray-700">${a.region}</td>
        <td class="px-3 py-2 text-gray-700">${a.occupation}</td>
        <td class="px-3 py-2 text-right font-mono text-gray-900">${fmtNum(r.optimal_multiplier, 2)}×</td>
        <td class="px-3 py-2 text-right font-mono text-gray-900">${fmtMoney(r.optimal_premium_usd)}</td>
        <td class="px-3 py-2 text-right font-mono ${r.optimal_expected_profit >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(r.optimal_expected_profit)}</td>
        <td class="px-3 py-2 text-right font-mono text-gray-600">${(r.optimal_p_accept * 100).toFixed(1)}%</td>
      `;
      tbody.appendChild(row);
    });

    // PSI monitor
    if (data.psi) {
      renderPSI(data.psi);
    }

  } catch (e) {
    alert('Batch optimisation failed: ' + e.message);
  } finally {
    document.getElementById('batch-spinner').classList.add('hidden');
    document.getElementById('batch-btn-text').textContent = 'Run Batch';
  }
}

function renderPSI(psiData) {
  const container = document.getElementById('psi-cards');
  const colorMap = {
    GREEN:  { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    AMBER:  { bg: 'bg-amber-50',  border: 'border-amber-200',  text: 'text-amber-700',  dot: 'bg-amber-500'  },
    RED:    { bg: 'bg-red-50',    border: 'border-red-200',    text: 'text-red-700',    dot: 'bg-red-500'    },
  };

  const order = ['region', 'occupation', 'age_bin', 'wealth_quintile'];
  container.innerHTML = '';

  order.forEach(key => {
    const item = psiData[key];
    if (!item) return;
    const c = colorMap[item.status] || colorMap.GREEN;
    const card = document.createElement('div');
    card.className = `${c.bg} rounded-lg border ${c.border} p-3`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="text-xs font-medium text-gray-500 uppercase">${item.label}</div>
        <span class="w-2 h-2 rounded-full ${c.dot}"></span>
      </div>
      <div class="text-lg font-bold ${c.text} mt-1">${item.psi.toFixed(4)}</div>
      <div class="text-xs ${c.text} mt-0.5 opacity-80">${item.status}</div>
    `;
    container.appendChild(card);
  });

  renderPSIChart(psiData);
}

function renderPSIChart(psiData) {
  const ctx = document.getElementById('psi-chart').getContext('2d');
  if (charts.psi) charts.psi.destroy();

  const order = ['region', 'occupation', 'age_bin', 'wealth_quintile'];
  const labels = [];
  const values = [];
  const bgColors = [];

  order.forEach(key => {
    const item = psiData[key];
    if (!item) return;
    labels.push(item.label);
    values.push(item.psi);
    if (item.status === 'GREEN') bgColors.push('#10b981');
    else if (item.status === 'AMBER') bgColors.push('#f59e0b');
    else bgColors.push('#ef4444');
  });

  charts.psi = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'PSI',
        data: values,
        backgroundColor: bgColors,
        borderRadius: 4,
        barPercentage: 0.6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `PSI: ${ctx.raw.toFixed(4)}`
          }
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#f3f4f6' },
          title: { display: true, text: 'PSI' },
        },
        x: { grid: { display: false } },
      }
    }
  });
}

function renderPSIBarChart(psiData, canvasId, chartKey) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[chartKey]) charts[chartKey].destroy();

  const order = ['region', 'occupation', 'age_bin', 'wealth_quintile'];
  const labels = [];
  const values = [];
  const bgColors = [];
  order.forEach(key => {
    const item = psiData[key];
    if (!item) return;
    labels.push(item.label);
    values.push(item.psi);
    if (item.status === 'GREEN') bgColors.push('#10b981');
    else if (item.status === 'AMBER') bgColors.push('#f59e0b');
    else bgColors.push('#ef4444');
  });

  const maxVal = values.length ? Math.max(...values) : 0;
  const suggestedMax = Math.max(0.30, maxVal * 1.15);

  // Inline plugin: vertical reference lines at the 0.10 / 0.25 thresholds
  const thresholdLines = {
    id: 'psiThresholdLines',
    afterDraw(chart) {
      const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;
      [[0.10, '#f59e0b'], [0.25, '#ef4444']].forEach(([v, color]) => {
        const px = x.getPixelForValue(v);
        ctx.save();
        ctx.beginPath();
        ctx.setLineDash([4, 4]);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = color;
        ctx.moveTo(px, top);
        ctx.lineTo(px, bottom);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = color;
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(v.toFixed(2), px, top - 3);
        ctx.restore();
      });
    }
  };

  charts[chartKey] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'PSI', data: values, backgroundColor: bgColors, borderRadius: 4, barPercentage: 0.6 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 12 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => `PSI: ${c.raw.toFixed(4)}` } },
      },
      scales: {
        x: { beginAtZero: true, suggestedMax, grid: { color: '#f3f4f6' }, title: { display: true, text: 'PSI' } },
        y: { grid: { display: false } },
      }
    },
    plugins: [thresholdLines],
  });
}

function renderBatchHistogram(histogram) {
  const ctx = document.getElementById('batch-histogram-chart').getContext('2d');
  if (charts.batchHistogram) charts.batchHistogram.destroy();

  const labels = histogram.bins.slice(0, -1).map((b, i) => {
    const next = histogram.bins[i + 1];
    return `${b}–${next}×`;
  });
  labels[labels.length - 1] = histogram.bins[histogram.bins.length - 2] + '–' + histogram.bins[histogram.bins.length - 1] + '×';

  charts.batchHistogram = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Applicant Count',
        data: histogram.counts,
        backgroundColor: '#2E5FA3',
        borderRadius: 4,
        barPercentage: 0.8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Count: ${ctx.raw}`
          }
        }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } },
      }
    }
  });
}

// ---------------------------------------------------------------------------
// Bandit Arena
// ---------------------------------------------------------------------------
document.getElementById('arena-algo').addEventListener('change', function() {
  const algo = this.value;
  document.getElementById('arena-param-alpha').classList.toggle('hidden', algo !== 'LinUCB');
  document.getElementById('arena-param-epsilon').classList.toggle('hidden', algo !== 'EpsilonGreedy');
  document.getElementById('arena-param-v2').classList.toggle('hidden', algo !== 'LinTS');
});

async function runArena() {
  const algo = document.getElementById('arena-algo').value;
  const rounds = parseInt(document.getElementById('arena-rounds').value);
  const seed = parseInt(document.getElementById('arena-seed').value);
  const alpha = parseFloat(document.getElementById('arena-alpha').value);
  const epsilon = parseFloat(document.getElementById('arena-epsilon').value);
  const v2 = parseFloat(document.getElementById('arena-v2').value);

  document.getElementById('arena-spinner').classList.remove('hidden');
  document.getElementById('arena-btn-text').textContent = 'Running...';

  try {
    const data = await apiPost('/api/bandit/run', {
      algorithm: algo, n_rounds: rounds, seed, alpha, epsilon, v2
    });

    // Summary cards
    const summary = document.getElementById('arena-summary');
    const ent = entropy(data.action_distribution);
    summary.innerHTML = `
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Cumulative Reward</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${fmtMoney(data.cumulative_reward)}</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Cumulative Regret</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${fmtMoney(data.cumulative_regret)}</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Avg Regret (last 500)</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${fmtMoney(data.avg_regret_last_500)}</div>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <div class="text-xs font-medium text-gray-500 uppercase">Action Entropy</div>
        <div class="text-xl font-bold text-gray-900 mt-1">${ent.toFixed(3)}</div>
      </div>
    `;

    // Reward curve
    renderLineChart('arena-chart-reward', 'Cumulative Reward', data.trajectory.rounds, data.trajectory.cumulative_rewards, '#2E5FA3');
    // Regret curve — overlay the Õ(d√t) bound for linear bandits only
    let regretOverlay = null;
    if (algo === 'LinUCB' || algo === 'LinTS') {
      const d = data.n_features;
      const cumRegrets = data.trajectory.cumulative_regrets;
      const calT = Math.min(200, cumRegrets.length);
      const empAtCal = calT >= 1 ? cumRegrets[calT - 1] : 0;
      if (empAtCal > 0) {
        const c = empAtCal / (d * Math.sqrt(calT));
        regretOverlay = {
          label: `Theoretical bound  c·d·√t  (d=${d})`,
          color: '#9333ea',
          compute: (t) => c * d * Math.sqrt(t),
        };
      }
    }
    renderLineChart('arena-chart-regret', 'Cumulative Regret', data.trajectory.rounds, data.trajectory.cumulative_regrets, '#ef4444', regretOverlay);
    // Pie
    renderPieChart('arena-chart-pie', data.action_distribution);
    // Early vs Late bar
    renderComparisonBar('arena-chart-compare', data.early_action_distribution, data.late_action_distribution);

  } catch (e) {
    alert('Arena run failed: ' + e.message);
  } finally {
    document.getElementById('arena-spinner').classList.add('hidden');
    document.getElementById('arena-btn-text').textContent = 'Run Bandit';
  }
}

function renderLineChart(canvasId, label, xData, yData, color, overlay = null) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[canvasId]) charts[canvasId].destroy();

  // Downsample for performance if needed
  let xs = xData, ys = yData;
  if (xs.length > 2000) {
    const step = Math.ceil(xs.length / 1500);
    xs = xs.filter((_, i) => i % step === 0);
    ys = ys.filter((_, i) => i % step === 0);
  }

  const datasets = [{
    label,
    data: ys,
    borderColor: color,
    backgroundColor: color + '15',
    fill: true,
    pointRadius: 0,
    tension: 0.3,
    borderWidth: 2,
  }];

  // Optional theoretical overlay — sampled against the (possibly downsampled) xs
  if (overlay) {
    datasets.push({
      label: overlay.label,
      data: xs.map(t => overlay.compute(t)),
      borderColor: overlay.color,
      backgroundColor: 'transparent',
      fill: false,
      pointRadius: 0,
      borderDash: [6, 4],
      tension: 0,
      borderWidth: 2,
    });
  }

  charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels: xs, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: overlay
          ? { display: true, position: 'bottom', labels: { boxWidth: 12, font: { size: 11 }, usePointStyle: true } }
          : { display: false },
      },
      scales: {
        x: { display: false },
        y: { grid: { color: '#f3f4f6' } },
      }
    }
  });
}

function renderPieChart(canvasId, dist) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[canvasId]) charts[canvasId].destroy();
  charts[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(dist),
      datasets: [{
        data: Object.values(dist),
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6366f1'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.label}: ${(ctx.raw * 100).toFixed(1)}%`
          }
        }
      }
    }
  });
}

function renderComparisonBar(canvasId, early, late) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[canvasId]) charts[canvasId].destroy();
  const labels = Object.keys(early);
  charts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Early', data: labels.map(l => early[l]), backgroundColor: '#94a3b8', borderRadius: 4 },
        { label: 'Late', data: labels.map(l => late[l]), backgroundColor: '#2E5FA3', borderRadius: 4 },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } },
      scales: {
        y: { beginAtZero: true, max: 1, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } },
      }
    }
  });
}

// ---------------------------------------------------------------------------
// Benchmark Race
// ---------------------------------------------------------------------------
async function runBenchmark() {
  const rounds = parseInt(document.getElementById('bench-rounds').value);
  const seed = parseInt(document.getElementById('bench-seed').value);

  document.getElementById('bench-spinner').classList.remove('hidden');
  document.getElementById('bench-btn-text').textContent = 'Running...';

  try {
    const data = await apiPost('/api/bandit/compare', {
      algorithm: 'LinUCB', n_rounds: rounds, seed, alpha: 1.0, epsilon: 0.1, v2: 1.0
    });

    // Table
    const tbody = document.getElementById('bench-table-body');
    tbody.innerHTML = '';
    const colors = { LinUCB: '#2E5FA3', LinTS: '#6366f1', EpsilonGreedy: '#f59e0b', StaticXGB: '#94a3b8' };
    data.results.forEach(r => {
      const dist = r.action_distribution;
      const row = document.createElement('tr');
      row.className = 'hover:bg-gray-50 transition';
      row.innerHTML = `
        <td class="px-4 py-3 font-medium text-gray-900 flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full inline-block" style="background:${colors[r.algorithm] || '#ccc'}"></span>
          ${r.algorithm}
        </td>
        <td class="px-4 py-3 text-right font-mono ${r.cumulative_reward >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(r.cumulative_reward)}</td>
        <td class="px-4 py-3 text-right font-mono text-gray-600">${fmtMoney(r.cumulative_regret)}</td>
        <td class="px-4 py-3 text-right font-mono text-gray-600">${fmtMoney(r.avg_regret_last_500)}</td>
        <td class="px-4 py-3 text-center text-xs text-gray-500">${dist.STANDARD}</td>
        <td class="px-4 py-3 text-center text-xs text-gray-500">${dist.RATED}</td>
        <td class="px-4 py-3 text-center text-xs text-gray-500">${dist.DECLINE}</td>
        <td class="px-4 py-3 text-center text-xs text-gray-500">${dist.REFER}</td>
      `;
      tbody.appendChild(row);
    });

    // Charts
    const rewardDatasets = data.results.map(r => ({
      label: r.algorithm,
      data: r.trajectory.cumulative_rewards,
      borderColor: colors[r.algorithm] || '#999',
      backgroundColor: (colors[r.algorithm] || '#999') + '10',
      fill: false,
      pointRadius: 0,
      tension: 0.3,
      borderWidth: 2,
    }));

    const regretDatasets = data.results.map(r => ({
      label: r.algorithm,
      data: r.trajectory.cumulative_regrets,
      borderColor: colors[r.algorithm] || '#999',
      backgroundColor: (colors[r.algorithm] || '#999') + '10',
      fill: false,
      pointRadius: 0,
      tension: 0.3,
      borderWidth: 2,
    }));

    renderMultiLineChart('bench-chart-reward', 'Cumulative Reward', data.results[0].trajectory.rounds, rewardDatasets);
    renderMultiLineChart('bench-chart-regret', 'Cumulative Regret', data.results[0].trajectory.rounds, regretDatasets);

  } catch (e) {
    alert('Benchmark failed: ' + e.message);
  } finally {
    document.getElementById('bench-spinner').classList.add('hidden');
    document.getElementById('bench-btn-text').textContent = 'Run Race';
  }
}

function renderMultiLineChart(canvasId, label, rounds, datasets) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[canvasId]) charts[canvasId].destroy();

  // Downsample
  let xs = rounds;
  const step = xs.length > 2000 ? Math.ceil(xs.length / 1500) : 1;
  if (step > 1) {
    xs = xs.filter((_, i) => i % step === 0);
    datasets.forEach(ds => { ds.data = ds.data.filter((_, i) => i % step === 0); });
  }

  charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: { labels: xs, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 }, usePointStyle: true } }
      },
      scales: {
        x: { display: false },
        y: { grid: { color: '#f3f4f6' } },
      }
    }
  });
}

// ---------------------------------------------------------------------------
// HITL (Human-in-the-Loop) Underwriter Review
// ---------------------------------------------------------------------------
let hitlCurrent = null;  // { index, applicant, bandit_action, bandit_action_name, expected_rewards }
let hitlHistory = [];    // local cache of reviews

async function hitlNextApplicant() {
  document.getElementById('hitl-spinner').classList.remove('hidden');
  document.getElementById('hitl-btn-text').textContent = 'Loading...';
  try {
    const data = await apiGet('/api/hitl/recommend');
    hitlCurrent = data;

    // Show applicant card
    const card = document.getElementById('hitl-applicant-card');
    card.classList.remove('hidden');
    const a = data.applicant;
    const details = document.getElementById('hitl-applicant-details');
    details.innerHTML = `
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Age</div><div class="font-semibold">${a.age}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Gender</div><div class="font-semibold">${a.gender}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">BMI</div><div class="font-semibold">${a.bmi}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Income</div><div class="font-semibold">$${a.monthly_income_usd}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Region</div><div class="font-semibold">${a.region}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Occupation</div><div class="font-semibold">${a.occupation}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Wealth</div><div class="font-semibold">${a.wealth_quintile}</div></div>
      <div class="bg-gray-50 rounded p-2"><div class="text-xs text-gray-500">Mortality</div><div class="font-semibold">${a.mortality_multiplier}×</div></div>
    `;

    // Show recommendation
    const rec = data.expected_rewards;
    const recDiv = document.getElementById('hitl-recommendation');
    const actionColor = data.bandit_action_name === 'STANDARD' ? 'text-emerald-700 bg-emerald-50 border-emerald-200' :
                        data.bandit_action_name === 'RATED' ? 'text-amber-700 bg-amber-50 border-amber-200' :
                        data.bandit_action_name === 'DECLINE' ? 'text-red-700 bg-red-50 border-red-200' :
                        'text-indigo-700 bg-indigo-50 border-indigo-200';
    recDiv.innerHTML = `
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-medium text-gray-500">Bandit Recommends</span>
        <span class="text-xs font-bold px-2 py-0.5 rounded border ${actionColor}">${data.bandit_action_name}</span>
      </div>
      <div class="grid grid-cols-4 gap-2 text-xs">
        <div>STANDARD: <span class="font-mono">${fmtMoney(rec.STANDARD)}</span></div>
        <div>RATED: <span class="font-mono">${fmtMoney(rec.RATED)}</span></div>
        <div>DECLINE: <span class="font-mono">${fmtMoney(rec.DECLINE)}</span></div>
        <div>REFER: <span class="font-mono">${fmtMoney(rec.REFER)}</span></div>
      </div>
    `;

    // Show override buttons
    document.getElementById('hitl-override-buttons').classList.remove('hidden');

    // Refresh metrics
    await hitlRefreshMetrics();
  } catch (e) {
    alert('Failed to load applicant: ' + e.message);
  } finally {
    document.getElementById('hitl-spinner').classList.add('hidden');
    document.getElementById('hitl-btn-text').textContent = 'Next Applicant';
  }
}

async function hitlSubmitReview(overrideAction) {
  if (!hitlCurrent) {
    alert('No applicant loaded. Click "Next Applicant" first.');
    return;
  }
  const underwriter = document.getElementById('hitl-underwriter').value || 'Underwriter';
  try {
    const data = await apiPost('/api/hitl/review', {
      index: hitlCurrent.index,
      bandit_action: hitlCurrent.bandit_action,
      override_action: overrideAction,
      underwriter: underwriter,
    });

    // Cache review locally for history display
    hitlHistory.push({
      bandit: hitlCurrent.bandit_action_name,
      override: ['STANDARD', 'RATED', 'DECLINE'][overrideAction],
      reward: data.reward,
      region: hitlCurrent.applicant.region,
      occupation: hitlCurrent.applicant.occupation,
    });

    // Update metrics display
    hitlRenderMetrics(data.metrics);

    // Show history
    hitlRenderHistory();

    // Clear current applicant so user must click Next
    hitlCurrent = null;
    document.getElementById('hitl-override-buttons').classList.add('hidden');
    document.getElementById('hitl-recommendation').innerHTML = '<span class="italic text-gray-500">Review submitted. Click "Next Applicant" to continue.</span>';

    // Refresh full metrics + PSI
    await hitlRefreshMetrics();
  } catch (e) {
    alert('Review submission failed: ' + e.message);
  }
}

async function hitlRefreshMetrics() {
  try {
    const data = await apiGet('/api/hitl/metrics');
    hitlRenderMetrics(data);
    if (data.psi) {
      renderPSIToContainer(data.psi, 'hitl-psi-cards');
      renderPSIBarChart(data.psi, 'hitl-psi-chart', 'hitlPsi');
    }
    hitlRenderRewardChart(data.recent_rewards);
  } catch (e) {
    console.warn('Metrics refresh failed:', e);
  }
}

function hitlRenderMetrics(m) {
  document.getElementById('hitl-m-total').textContent = m.total_reviews;
  document.getElementById('hitl-m-override').textContent = m.override_rate !== null ? (m.override_rate * 100).toFixed(1) + '%' : '—';
  document.getElementById('hitl-m-align').textContent = m.alignment_rate !== null ? (m.alignment_rate * 100).toFixed(1) + '%' : '—';
  document.getElementById('hitl-m-avg').textContent = m.avg_reward !== null ? fmtMoney(m.avg_reward) : '—';
  document.getElementById('hitl-m-cum').textContent = fmtMoney(m.cumulative_reward);
  document.getElementById('hitl-m-cost').textContent = fmtMoney(m.human_cost);
}

function hitlRenderHistory() {
  const tbody = document.getElementById('hitl-history-body');
  if (hitlHistory.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="px-3 py-6 text-center text-gray-400 italic">No reviews yet.</td></tr>';
    return;
  }
  tbody.innerHTML = '';
  hitlHistory.slice().reverse().slice(0, 20).forEach((r, i) => {
    const row = document.createElement('tr');
    row.className = 'hover:bg-gray-50 transition';
    row.innerHTML = `
      <td class="px-3 py-2 text-gray-500">${hitlHistory.length - i}</td>
      <td class="px-3 py-2 text-gray-700">${r.bandit}</td>
      <td class="px-3 py-2 font-medium ${r.override === 'DECLINE' ? 'text-red-600' : 'text-emerald-600'}">${r.override}</td>
      <td class="px-3 py-2 text-right font-mono ${r.reward >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(r.reward)}</td>
      <td class="px-3 py-2 text-gray-700">${r.region}</td>
      <td class="px-3 py-2 text-gray-700">${r.occupation}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderPSIToContainer(psiData, containerId) {
  const container = document.getElementById(containerId);
  const colorMap = {
    GREEN:  { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    AMBER:  { bg: 'bg-amber-50',  border: 'border-amber-200',  text: 'text-amber-700',  dot: 'bg-amber-500'  },
    RED:    { bg: 'bg-red-50',    border: 'border-red-200',    text: 'text-red-700',    dot: 'bg-red-500'    },
  };
  const order = ['region', 'occupation', 'age_bin', 'wealth_quintile'];
  container.innerHTML = '';
  order.forEach(key => {
    const item = psiData[key];
    if (!item) return;
    const c = colorMap[item.status] || colorMap.GREEN;
    const card = document.createElement('div');
    card.className = `${c.bg} rounded-lg border ${c.border} p-3`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="text-xs font-medium text-gray-500 uppercase">${item.label}</div>
        <span class="w-2 h-2 rounded-full ${c.dot}"></span>
      </div>
      <div class="text-lg font-bold ${c.text} mt-1">${item.psi.toFixed(4)}</div>
      <div class="text-xs ${c.text} mt-0.5 opacity-80">${item.status}</div>
    `;
    container.appendChild(card);
  });
}

function hitlRenderRewardChart(rewards) {
  const ctx = document.getElementById('hitl-chart-reward').getContext('2d');
  if (charts.hitlReward) charts.hitlReward.destroy();
  if (!rewards || rewards.length === 0) return;
  const labels = rewards.map((_, i) => i + 1);
  charts.hitlReward = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Reward (USD)',
        data: rewards,
        borderColor: '#2E5FA3',
        backgroundColor: '#2E5FA315',
        fill: true,
        pointRadius: 2,
        tension: 0.3,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { grid: { color: '#f3f4f6' } },
      }
    }
  });
}

async function hitlExportCSV() {
  try {
    const data = await apiGet('/api/hitl/export');
    if (!data.csv) {
      alert('No reviews to export.');
      return;
    }
    const blob = new Blob([data.csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hitl_reviews_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert('Export failed: ' + e.message);
  }
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  runPricingOptimize();
  hitlRefreshMetrics();
});
