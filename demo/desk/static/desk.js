// Underwriting Desk view: grouped applicant form + result card.
const Desk = (function () {
  let FIELDS = null;
  let selectedConditions = new Set();
  let loadedMortality = 1.0; // carried from a loaded CDHS sample; manual = 1.0

  const ACTIONS = ['STANDARD', 'RATED', 'DECLINE', 'REFER'];

  // Calibrated preset profiles (2026-07-04): verified against the frozen theta
  // (demo/static/coefficients_linucb_seed42.json) and StaticXGBBaseline directly —
  // decisions below are not assumed, they are deterministic outputs of both scorers.
  // high_risk: bandit DECLINE, xgb DECLINE (conf 98.7%) — agreement.
  // low_risk: bandit STANDARD, xgb STANDARD (conf 92.7%) — agreement.
  // borderline: bandit RATED, xgb STANDARD (conf 50.6%, xgb mortality 1.36 under its
  // 1.5 STANDARD cutoff) — disagreement; the bandit estimates STANDARD would be a net
  // loss (-$21) here where XGB's threshold rule sees a comfortably low mortality
  // prediction and auto-approves, leaving ~$30/applicant on the table (seed 42).
  const PRESETS = {
    high_risk: {
      age: 65, gender: 'Male', bmi: 34.0,
      region: 'Prey Veng', occupation: 'Rice Farmer',
      is_smoking: 1, alcohol_use: 1, is_exercise: 0, has_family_history: 1,
      conditions: ['Hypertension', 'Diabetes', 'Heart Disease'],
      monthly_income_usd: 120, education: 'No education',
      wealth_quintile: 'Poorest', self_reported_health: 'Poor',
      mortality_multiplier: 3.5,
    },
    low_risk: {
      age: 24, gender: 'Female', bmi: 21.0,
      region: 'Prey Veng', occupation: 'Market Vendor',
      is_smoking: 0, alcohol_use: 0, is_exercise: 1, has_family_history: 0,
      conditions: [],
      monthly_income_usd: 250, education: 'Secondary',
      wealth_quintile: 'Richest', self_reported_health: 'Good',
      mortality_multiplier: 1.0,
    },
    borderline: {
      age: 38, gender: 'Male', bmi: 32.0,
      region: 'Prey Veng', occupation: 'Civil Servant',
      is_smoking: 0, alcohol_use: 0, is_exercise: 1, has_family_history: 0,
      conditions: [],
      monthly_income_usd: 150, education: 'Primary',
      wealth_quintile: 'Richer', self_reported_health: 'Good',
      mortality_multiplier: 1.36,
    },
  };

  function opt(list, val) {
    return list.map(v => `<option ${v === val ? 'selected' : ''}>${v}</option>`).join('');
  }

  function renderForm(values) {
    const v = values || {};
    const f = FIELDS;
    document.getElementById('form').innerHTML = `
      <div class="group-title">Demographics</div>
      <div class="row">
        <div><label>Age</label><input id="f-age" type="number" value="${v.age ?? 35}"></div>
        <div><label>Gender</label><select id="f-gender">${opt(['Male','Female'], v.gender ?? 'Male')}</select></div>
      </div>
      <div class="row">
        <div><label>Region</label><select id="f-region">${opt(f.regions, v.region)}</select></div>
        <div><label>Occupation</label><select id="f-occupation">${opt(f.occupations, v.occupation)}</select></div>
      </div>
      <div class="group-title">Health &amp; lifestyle</div>
      <div class="row">
        <div><label>BMI</label><input id="f-bmi" type="number" step="0.1" value="${v.bmi ?? 23}"></div>
        <div><label>Self-reported health</label><select id="f-health">${opt(f.health_statuses, v.self_reported_health ?? 'Fair')}</select></div>
      </div>
      <div class="chips" id="lifestyle">
        ${[['is_smoking','Smoker'],['alcohol_use','Alcohol'],['is_exercise','Exercises'],['has_family_history','Family history']]
          .map(([k,lab]) => `<span class="chip ${v[k] ? 'on' : ''}" data-k="${k}">${lab}</span>`).join('')}
      </div>
      <label>Pre-existing conditions</label>
      <div class="chips" id="conditions">
        ${f.conditions.map(c => `<span class="chip ${selectedConditions.has(c) ? 'on' : ''}" data-c="${c}">${c}</span>`).join('')}
      </div>
      <div class="group-title">Socioeconomic</div>
      <div class="row">
        <div><label>Monthly income (USD)</label><input id="f-income" type="number" value="${v.monthly_income_usd ?? 250}"></div>
        <div><label>Education</label><select id="f-education">${opt(f.educations, v.education ?? 'Primary')}</select></div>
      </div>
      <label>Wealth quintile</label>
      <select id="f-wealth">${opt(f.wealth_quintiles, v.wealth_quintile ?? 'Middle')}</select>
    `;
    // Toggle handlers for binary lifestyle chips + condition chips.
    document.querySelectorAll('#lifestyle .chip').forEach(ch =>
      ch.addEventListener('click', () => ch.classList.toggle('on')));
    document.querySelectorAll('#conditions .chip').forEach(ch =>
      ch.addEventListener('click', () => {
        ch.classList.toggle('on');
        const c = ch.dataset.c;
        if (selectedConditions.has(c)) selectedConditions.delete(c); else selectedConditions.add(c);
      }));
  }

  function readForm() {
    const lifestyle = {};
    document.querySelectorAll('#lifestyle .chip').forEach(ch =>
      lifestyle[ch.dataset.k] = ch.classList.contains('on') ? 1 : 0);
    return {
      age: parseInt(document.getElementById('f-age').value, 10),
      gender: document.getElementById('f-gender').value,
      bmi: parseFloat(document.getElementById('f-bmi').value),
      is_smoking: lifestyle.is_smoking || 0,
      alcohol_use: lifestyle.alcohol_use || 0,
      is_exercise: lifestyle.is_exercise || 0,
      has_family_history: lifestyle.has_family_history || 0,
      monthly_income_usd: parseFloat(document.getElementById('f-income').value),
      pre_existing_conditions: Array.from(selectedConditions).join(', '),
      region: document.getElementById('f-region').value,
      occupation: document.getElementById('f-occupation').value,
      education: document.getElementById('f-education').value,
      wealth_quintile: document.getElementById('f-wealth').value,
      self_reported_health: document.getElementById('f-health').value,
      mortality_multiplier: loadedMortality,
    };
  }

  function bar(name, val, lo, hi, win) {
    const span = (hi - lo) || 1;
    const pct = Math.max(2, Math.round(((val - lo) / span) * 100));
    return `<div class="bar-row ${win ? 'win' : ''}">
      <span>${name}</span>
      <div class="bar-track"><div class="bar" style="width:${pct}%"></div></div>
      <span>$${val.toFixed(0)}</span></div>`;
  }

  // Thresholds calibrated against the P3 preset table (2026-07-04): borderline
  // lands at 50.6% confidence, low/high risk at 92.7%/98.7% — the presets never
  // land near the plan's original 40/75 split, so the cut-points move to 55/85
  // to keep Low/High Risk GREEN and Borderline clearly separated (RED).
  function confidenceBadge(pct) {
    if (pct < 55) return { label: '⚠️ Margin thin — human review territory', color: 'var(--red)' };
    if (pct < 85) return { label: '👁 Bandit decides, monitored', color: 'var(--accent)' };
    return { label: '✅ High margin, automated', color: 'var(--green)' };
  }

  function renderConfidence(conf) {
    const pct = Math.round(conf * 100);
    const { label, color } = confidenceBadge(pct);
    const tip = 'How decisively this decision beats the runner-up action under the ' +
      'learned value model (softmax margin, τ=6). Illustrative — not a calibrated ' +
      'probability. Low margin = actions nearly tied = the natural case for human review.';
    return `
      <div style="margin-top:.75rem;" title="${tip}">
        <div style="display:flex;justify-content:space-between;" class="muted">
          <span>Decision confidence (illustrative)</span><span>${pct}%</span>
        </div>
        <div class="bar-track" style="height:8px;border-radius:4px;overflow:hidden;">
          <div style="width:${pct}%;height:100%;background:${color};transition:width .4s;"></div>
        </div>
        <div class="muted" style="color:${color};margin-top:.3rem;">${label}</div>
      </div>`;
  }

  function renderComparison(d) {
    const bandit = d.decision;
    const xgb = d.static_xgb;
    const er = d.estimated_rewards;
    const disagree = bandit !== xgb.action;
    const xgbBorder = disagree ? 'var(--amber)' : 'var(--green)';
    const gap = (er[bandit] - er[xgb.action]).toFixed(0);
    return `
    <div class="group-title">Adaptive vs static — same applicant</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;">
      <div style="border:1px solid var(--accent);border-radius:8px;padding:.75rem;">
        <div class="muted" style="color:var(--accent);font-weight:600;">LINUCB · ADAPTIVE</div>
        <div style="font-size:1.3rem;font-weight:700;">${bandit}</div>
        <div class="muted">Value estimate: $${er[bandit].toFixed(0)}</div>
      </div>
      <div style="border:1px solid ${xgbBorder};border-radius:8px;padding:.75rem;">
        <div class="muted" style="color:${xgbBorder};font-weight:600;">
          STATIC XGB · BASELINE ${disagree ? '⚡ DISAGREES' : '✓ AGREES'}</div>
        <div style="font-size:1.3rem;font-weight:700;">${xgb.action}</div>
        <div class="muted">Value estimate: $${er[xgb.action].toFixed(0)}</div>
        <div class="muted" style="margin-top:.35rem;">${xgb.reasoning}</div>
      </div>
    </div>
    ${disagree ? `<div class="muted" style="color:var(--amber);margin-top:.5rem;">
      ⚡ Decision conflict — under the learned value model the static choice leaves
      $${gap} per applicant on the table (illustrative, seed 42). Compounded over
      5,000 applicants, differences like this are the +25.2% headline
      (20 seeds, admissible policies).
    </div>` : ''}`;
  }

  function renderResult(d) {
    const er = d.estimated_rewards;
    const vals = ACTIONS.map(a => er[a]);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const fair = d.fairness;
    const prem = d.premium;
    document.getElementById('result').innerHTML = `
      <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
        <span class="badge decision-badge b-${d.decision}">${d.decision}</span>
        <span class="badge z-${fair.badge_status}" title="${fair.note}">
          Guardrail: ${fair.badge_status}</span>
      </div>
      ${renderConfidence(d.confidence)}
      <div class="group-title">Estimated reward by action</div>
      ${ACTIONS.map(a => bar(a, er[a], lo, hi, a === d.decision)).join('')}
      ${renderComparison(d)}
      <div class="group-title">Recommended premium</div>
      <div style="font-size:1.2rem;font-weight:700">${prem.display}
        ${prem.multiplier ? `<span class="muted" style="font-size:.8rem">×${prem.multiplier}</span>` : ''}</div>
      <div class="group-title">Why this decision</div>
      ${d.drivers.map(dr => `<div class="driver"><span>${dr.label}</span>
        <span class="${dr.direction}">${dr.direction === 'up' ? '▲' : '▼'}
        ${Math.abs(dr.contribution).toFixed(1)}</span></div>`).join('')}
      <div class="group-title">Fairness guardrail (model-level)</div>
      <div class="muted">Region ${fair.region.psi} (${fair.region.status}) ·
        Occupation ${fair.occupation.psi} (${fair.occupation.status})<br>
        Canonical EXP-006 (20-seed): region ${fair.canonical.region_zone} ·
        occupation ${fair.canonical.occupation_zone}</div>
      <div class="note">${d.illustrative_note}</div>`;
  }

  async function score() {
    document.getElementById('form-err').textContent = '';
    try {
      const data = await API.score(readForm());
      renderResult(data);
    } catch (e) {
      document.getElementById('form-err').textContent = 'Could not score: ' + e.message;
    }
  }

  async function loadSample() {
    const { applicant } = await API.random();
    loadedMortality = applicant.mortality_multiplier ?? 1.0;
    selectedConditions = new Set(
      (applicant.pre_existing_conditions || '').split(',').map(s => s.trim()).filter(Boolean));
    renderForm(applicant);
  }

  function clearForm() {
    loadedMortality = 1.0;
    selectedConditions = new Set();
    renderForm({});
  }

  function loadPreset(key) {
    const p = PRESETS[key];
    loadedMortality = p.mortality_multiplier;
    selectedConditions = new Set(p.conditions);
    renderForm(p);
    score();
  }

  async function init() {
    FIELDS = await API.fields();
    renderForm({});
    document.getElementById('btn-load').addEventListener('click', loadSample);
    document.getElementById('btn-clear').addEventListener('click', clearForm);
    document.getElementById('btn-score').addEventListener('click', score);
    document.getElementById('preset-low').addEventListener('click', () => loadPreset('low_risk'));
    document.getElementById('preset-borderline').addEventListener('click', () => loadPreset('borderline'));
    document.getElementById('preset-high').addEventListener('click', () => loadPreset('high_risk'));
  }

  return { init, loadPreset };
})();
