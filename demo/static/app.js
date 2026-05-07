/**
 * Actuarial Reward Simulator — Frontend
 * FastAPI + vanilla JS + Chart.js
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const charts = {};
let currentExpected = {};

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
  ['simulator', 'pricing', 'arena', 'benchmark'].forEach(t => {
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
// Applicant Simulator
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
    mode: document.getElementById('sim-mode').value,
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

  simulateApplicant();
  updatePricingApplicantSummary();
}

async function simulateApplicant() {
  const body = getFormData();
  try {
    const simData = await apiPost('/api/simulate', body);
    currentExpected = simData.expected_rewards;

    let pricingData = null;
    try {
      pricingData = await apiPost('/api/pricing/optimize', body);
    } catch (e) {
      console.warn('Pricing optimisation failed:', e);
    }

    const legacyBest = Math.max(...Object.values(simData.expected_rewards));
    const optimisedProfit = pricingData ? pricingData.optimal_expected_profit : null;
    const trueBestIsOptimised = pricingData && optimisedProfit > legacyBest;

    const actions = ['OPTIMISED', 'STANDARD', 'RATED', 'DECLINE', 'REFER'];
    const colors = ['#2E5FA3', '#10b981', '#f59e0b', '#ef4444', '#6366f1'];
    const values = {
      OPTIMISED: pricingData ? pricingData.optimal_expected_profit : null,
      STANDARD: simData.expected_rewards.STANDARD,
      RATED: simData.expected_rewards.RATED,
      DECLINE: simData.expected_rewards.DECLINE,
      REFER: simData.expected_rewards.REFER,
    };

    const cardContainer = document.getElementById('reward-cards');
    cardContainer.innerHTML = '';

    actions.forEach((act, i) => {
      const val = values[act];
      if (val === null) return;
      const isOpt = act === 'OPTIMISED' ? trueBestIsOptimised : (simData.optimal_action === act && !trueBestIsOptimised);
      const card = document.createElement('div');
      card.className = `action-card bg-white rounded-xl border ${isOpt ? 'border-thesis-400 ring-1 ring-thesis-200' : 'border-gray-200'} p-4 relative overflow-hidden`;

      let label = act;
      let sublabel = isOpt ? 'Optimal action' : 'Expected value';
      if (act === 'OPTIMISED') {
        label = `Optimised (${fmtNum(pricingData.optimal_multiplier, 2)}×)`;
        sublabel = `Premium ${fmtMoney(pricingData.optimal_premium_usd)} · P(accept) ${(pricingData.optimal_p_accept * 100).toFixed(1)}%`;
      }

      card.innerHTML = `
        <div class="absolute top-0 right-0 w-16 h-16 opacity-10" style="background:${colors[i]}; border-radius: 0 0 0 100%"></div>
        <div class="text-xs font-medium text-gray-500 uppercase tracking-wide">${label}${isOpt ? ' ★' : ''}</div>
        <div class="text-2xl font-bold mt-1 ${val >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(val)}</div>
        <div class="text-xs text-gray-400 mt-1">${sublabel}</div>
      `;
      cardContainer.appendChild(card);
    });

    renderRewardChart(values);
  } catch (e) {
    alert('Simulation failed: ' + e.message);
  }
}

async function runStochastic() {
  const body = getFormData();
  try {
    const data = await apiPost('/api/simulate/stochastic?seed=' + Math.floor(Math.random() * 99999), body);
    const container = document.getElementById('stochastic-results');
    let html = '<div class="grid grid-cols-2 md:grid-cols-4 gap-3">';
    Object.entries(data.outcomes).forEach(([act, info]) => {
      const exp = currentExpected[act] || 0;
      const diff = info.reward - exp;
      html += `
        <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div class="text-xs font-semibold text-gray-600 uppercase">${act}</div>
          <div class="text-lg font-bold ${info.reward >= 0 ? 'text-gray-900' : 'text-red-600'}">${fmtMoney(info.reward)}</div>
          <div class="text-xs text-gray-500 mt-1">vs exp ${diff >= 0 ? '+' : ''}${fmtMoney(diff, 0)}</div>
          <div class="text-xs text-gray-400 mt-1 leading-tight">${info.outcome}</div>
        </div>
      `;
    });
    html += '</div>';
    container.innerHTML = html;
  } catch (e) {
    alert('Stochastic simulation failed: ' + e.message);
  }
}

function renderRewardChart(values) {
  const ctx = document.getElementById('reward-chart').getContext('2d');
  const labels = ['Optimised', 'Standard', 'Rated (+25%)', 'Decline', 'Refer'];
  const dataValues = [values.OPTIMISED, values.STANDARD, values.RATED, values.DECLINE, values.REFER];
  const colors = ['#2E5FA3', '#10b981', '#f59e0b', '#ef4444', '#6366f1'];

  if (charts.reward) charts.reward.destroy();
  charts.reward = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Expected Reward (USD)',
        data: dataValues,
        backgroundColor: colors,
        borderRadius: 6,
        barThickness: 40,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } },
      }
    }
  });
}

// ---------------------------------------------------------------------------
// Pricing Engine
// ---------------------------------------------------------------------------

function updatePricingApplicantSummary() {
  const age = document.getElementById('age').value;
  const region = document.getElementById('region').value;
  const occ = document.getElementById('occupation').value;
  const mort = document.getElementById('mortality_multiplier').value;
  document.getElementById('pricing-applicant-summary').innerText =
    `Age ${age}, ${region}, ${occ}, Mortality ${mort}×`;
}

function copyApplicantFromSimulator() {
  switchTab('pricing');
  updatePricingApplicantSummary();
  runPricingOptimize();
}

async function runPricingOptimize() {
  const body = getFormData();
  body.mode = document.getElementById('pricing-mode').value;

  document.getElementById('pricing-spinner').classList.remove('hidden');
  document.getElementById('pricing-btn-text').textContent = 'Optimising...';

  try {
    const data = await apiPost('/api/pricing/optimize', body);
    updatePricingApplicantSummary();

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
    // Regret curve
    renderLineChart('arena-chart-regret', 'Cumulative Regret', data.trajectory.rounds, data.trajectory.cumulative_regrets, '#ef4444');
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

function renderLineChart(canvasId, label, xData, yData, color) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  if (charts[canvasId]) charts[canvasId].destroy();

  // Downsample for performance if needed
  let xs = xData, ys = yData;
  if (xs.length > 2000) {
    const step = Math.ceil(xs.length / 1500);
    xs = xs.filter((_, i) => i % step === 0);
    ys = ys.filter((_, i) => i % step === 0);
  }

  charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: xs,
      datasets: [{
        label,
        data: ys,
        borderColor: color,
        backgroundColor: color + '15',
        fill: true,
        pointRadius: 0,
        tension: 0.3,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { display: false } },
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
// Init
// ---------------------------------------------------------------------------
document.getElementById('sim-mode').addEventListener('change', function() {
  const desc = document.getElementById('mode-desc');
  if (this.value === 'realistic') {
    desc.innerHTML = 'Realistic model: includes $25 fixed + 5% variable expenses, 8% lapse probability, and 2.5x CLV multiplier.';
  } else {
    desc.innerHTML = 'Base model: premium &minus; claims. No expenses, no lapse.';
  }
  simulateApplicant();
});

document.addEventListener('DOMContentLoaded', () => {
  simulateApplicant();
  updatePricingApplicantSummary();
});
