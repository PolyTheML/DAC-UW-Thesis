/* Defense Demo Frontend — Adaptive Underwriting Thesis Defense */
const TOTAL_SCENES = 10;
let currentScene = 1;
const charts = {};
const state = {
  exp005: null, exp007: null, coef: null, thesis: null,
  s3: { humanReward: 0, linucbReward: 0, pulls: 0, means: [45, 50, -10, 20], counts: [0,0,0,0], sums: [0,0,0,0], linucb: { A:[], b:[] } },
  arena: { interval: null, round: 0, data: null },
  fairnessTab: 'region',
  hitl: { total: 0, align: 0, cost: 0, rewards: [] },
};
const ACTIONS = ['STANDARD','RATED','DECLINE','REFER'];
const ACTION_COLORS = ['#10b981','#f59e0b','#ef4444','#6366f1'];
const NAMES = ['Sopheap Chea','Dara Phan','Sokha Kim','Vanna Meas','Chanda Lon','Ratanak Sao'];

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function fmt$(n){ if(n==null)return '—'; const s=n<0?'-$':'$'; return s+Math.abs(n).toLocaleString('en-US',{maximumFractionDigits:0}); }
function fmt1(n){ return (n||0).toFixed(1); }
function fmt2(n){ return (n||0).toFixed(2); }
async function apiPost(p,b){ const r=await fetch(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}); if(!r.ok)throw new Error('HTTP '+r.status); return r.json(); }
async function apiGet(p){ const r=await fetch(p); if(!r.ok)throw new Error('HTTP '+r.status); return r.json(); }

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
function init(){
  const dots = document.getElementById('nav-dots');
  for(let i=1;i<=TOTAL_SCENES;i++){
    const d=document.createElement('div'); d.className='nav-dot'+(i===1?' active':''); d.onclick=()=>showScene(i); dots.appendChild(d);
  }
  document.addEventListener('keydown',e=>{ if(e.key==='ArrowRight'||e.key===' ')nextScene(); if(e.key==='ArrowLeft')prevScene(); });
  loadData();
  showScene(1);
}
function showScene(n){
  if(n<1||n>TOTAL_SCENES)return;
  document.querySelectorAll('.scene').forEach((el,i)=>el.classList.toggle('active', i+1===n));
  document.querySelectorAll('.nav-dot').forEach((d,i)=>d.classList.toggle('active', i+1===n));
  document.getElementById('scene-indicator').textContent = `Scene ${n} of ${TOTAL_SCENES}`;
  document.getElementById('progress-fill').style.width = ((n-1)/(TOTAL_SCENES-1)*100)+'%';
  currentScene=n;
  if(n===1) renderOpeningChart();
  if(n===2) updateScene2();
  if(n===3) renderArmTrays();
  if(n===4) initArena();
  if(n===5) renderBenchmark();
  if(n===6) renderCoefficients(0);
  if(n===7) renderFairness();
  if(n===8){ renderHitlCanonical(); hitlRecommend(); }
  if(n===9) renderDrift();
}
function nextScene(){ showScene(currentScene+1); }
function prevScene(){ showScene(currentScene-1); }

// ---------------------------------------------------------------------------
// Data Loading
// ---------------------------------------------------------------------------
async function loadData(){
  try{ state.exp005 = await (await fetch('/static/exp005_results_seed42.json')).json(); }catch(e){ console.warn('exp005',e); }
  try{ state.exp007 = await (await fetch('/static/exp007_results_seed42.json')).json(); }catch(e){ console.warn('exp007',e); }
  try{ state.coef   = await (await fetch('/static/coefficients_linucb_seed42.json')).json(); }catch(e){ console.warn('coef',e); }
  try{ state.thesis = await (await fetch('/static/thesis_results.json')).json(); }catch(e){ console.warn('thesis',e); }
}

// ---------------------------------------------------------------------------
// Scene 1: Opening
// ---------------------------------------------------------------------------
function renderOpeningChart(){
  const ctx = document.getElementById('chart-opening'); if(!ctx)return;
  if(charts.opening) charts.opening.destroy();
  charts.opening = new Chart(ctx,{
    type:'bar', data:{
      labels:['Thailand','Vietnam','Laos','Cambodia'],
      datasets:[
        {label:'Insurance Penetration %', data:[40,8,4,1.5], backgroundColor:'#cbd5e1', borderRadius:4},
        {label:'Mobile Penetration %', data:[135,140,110,124], backgroundColor:'#2E5FA3', borderRadius:4}
      ]
    },
    options:{indexAxis:'y', responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}}, scales:{x:{grid:{display:false}},y:{grid:{display:false}}}}
  });
}
async function loadRandomApplicantScene1(){
  try{ const d=await apiGet('/api/applicant/random'); const a=d.applicant; const card=document.getElementById('applicant-card-s1');
    const name=NAMES[Math.floor(Math.random()*NAMES.length)];
    card.querySelector('.font-semibold').textContent=name;
    card.querySelector('.text-xs.text-gray-500').textContent=`${a.occupation} · ${a.region} · ${a.age}${a.gender[0]} · $${a.monthly_income_usd}/mo`;
    card.querySelectorAll('.bg-gray-50.rounded-lg.p-2')[0].querySelector('.font-semibold').textContent=a.bmi;
    card.querySelectorAll('.bg-gray-50.rounded-lg.p-2')[1].querySelector('.font-semibold').textContent=a.self_reported_health;
    const conds=(a.pre_existing_conditions||'').split(',').filter(Boolean).length;
    card.querySelectorAll('.bg-gray-50.rounded-lg.p-2')[2].querySelector('.font-semibold').textContent=conds?conds+' condition(s)':'None';
  }catch(e){ console.warn(e); }
}

// ---------------------------------------------------------------------------
// Scene 2: Static Failure
// ---------------------------------------------------------------------------
const SCENE2_PROFILES = [
  {age:55,gender:'Female',bmi:31,occupation:'Civil Servant',region:'Phnom Penh',income:420,multiplier:1.6,smoking:0,conditions:'',health:'Good',wealth:'Richer',education:'Secondary'},
  {age:28,gender:'Male',bmi:22,occupation:'Construction Worker',region:'Preah Sihanouk',income:280,multiplier:1.3,smoking:0,conditions:'',health:'Good',wealth:'Middle',education:'Primary'},
];
let s2idx=0;
async function updateScene2(){
  const p=SCENE2_PROFILES[s2idx];
  const bmi=parseFloat(document.getElementById('bmi-slider-s2').value);
  document.getElementById('bmi-val-s2').textContent=bmi.toFixed(1);
  const body={...p, bmi, monthly_income_usd:p.income, mortality_multiplier:p.multiplier, pre_existing_conditions:p.conditions, self_reported_health:p.health, wealth_quintile:p.wealth, education:p.education, mode:'simple'};
  try{
    const sim=await apiPost('/api/simulate',body);
    const container=document.getElementById('bandit-action-cards-s2'); container.innerHTML='';
    const vals=[sim.expected_rewards.STANDARD, sim.expected_rewards.RATED, sim.expected_rewards.DECLINE, sim.expected_rewards.REFER];
    const opt=Math.max(...vals);
    vals.forEach((v,i)=>{
      const isOpt=Math.abs(v-opt)<0.01;
      const div=document.createElement('div'); div.className=`flex items-center justify-between bg-white rounded-lg border ${isOpt?'border-thesis-400 ring-1 ring-thesis-200':'border-gray-200'} px-3 py-2`;
      div.innerHTML=`<span class="text-sm font-medium ${isOpt?'text-thesis-700':'text-gray-700'}">${ACTIONS[i]}${isOpt?' ★':''}</span><span class="font-mono font-bold ${v>=0?'text-gray-900':'text-red-600'}">${fmt$(v)}</span>`;
      container.appendChild(div);
    });
  }catch(e){ console.warn(e); }
}
function flipScenario(){ s2idx=(s2idx+1)%SCENE2_PROFILES.length; updateScene2(); }

// ---------------------------------------------------------------------------
// Scene 3: Explore vs Exploit (client-side simulation)
// ---------------------------------------------------------------------------
function renderArmTrays(){
  const c=document.getElementById('arm-trays'); c.innerHTML='';
  ACTIONS.forEach((a,i)=>{
    const div=document.createElement('div'); div.className='bg-white rounded-xl border border-gray-200 p-4 text-center action-card cursor-pointer';
    div.onclick=()=>manualPull(i);
    div.innerHTML=`<div class="text-xs font-semibold text-gray-500 uppercase mb-2">${a}</div><div class="text-2xl font-bold text-gray-900 mb-1" id="arm-mean-${i}">?</div><div class="text-xs text-gray-400">Empirical mean</div><div class="mt-2 text-xs text-thesis-600 font-medium" id="arm-count-${i}">0 pulls</div>`;
    c.appendChild(div);
  });
  resetArms();
}
function resetArms(){
  state.s3={ humanReward:0, linucbReward:0, pulls:0, means:[45,50,-10,20], counts:[0,0,0,0], sums:[0,0,0,0], linucb:{A:ACTIONS.map(()=>1), b:ACTIONS.map(()=>0)} };
  document.getElementById('human-reward').textContent=fmt$(0);
  document.getElementById('linucb-reward').textContent=fmt$(0);
  ACTIONS.forEach((_,i)=>{ document.getElementById(`arm-mean-${i}`).textContent='?'; document.getElementById(`arm-count-${i}`).textContent='0 pulls'; });
}
function manualPull(arm){
  const trueMean=state.s3.means[arm];
  const reward=trueMean + (Math.random()*20-10);
  state.s3.counts[arm]++;
  state.s3.sums[arm]+=reward;
  state.s3.humanReward+=reward;
  const emp=state.s3.sums[arm]/state.s3.counts[arm];
  document.getElementById(`arm-mean-${arm}`).textContent=fmt$(emp);
  document.getElementById(`arm-count-${arm}`).textContent=state.s3.counts[arm]+' pull'+(state.s3.counts[arm]>1?'s':'');
  document.getElementById('human-reward').textContent=fmt$(state.s3.humanReward);
}
function letLinUCBDecide(){
  // simple epsilon-greedy-ish client side for demo speed
  for(let t=0;t<20;t++){
    let bestArm=0, bestVal=-Infinity;
    for(let a=0;a<4;a++){
      const n=state.s3.counts[a]||1;
      const mean=(state.s3.sums[a]||0)/n;
      const bonus=Math.sqrt(2*Math.log(state.s3.pulls+2)/n);
      const ucb=mean+bonus;
      if(ucb>bestVal){bestVal=ucb; bestArm=a;}
    }
    const reward=state.s3.means[bestArm]+(Math.random()*20-10);
    state.s3.counts[bestArm]++;
    state.s3.sums[bestArm]+=reward;
    state.s3.linucbReward+=reward;
    state.s3.pulls++;
    document.getElementById(`arm-mean-${bestArm}`).textContent=fmt$(state.s3.sums[bestArm]/state.s3.counts[bestArm]);
    document.getElementById(`arm-count-${bestArm}`).textContent=state.s3.counts[bestArm]+' pulls';
  }
  document.getElementById('linucb-reward').textContent=fmt$(state.s3.linucbReward);
}

// ---------------------------------------------------------------------------
// Scene 4: Bandit Arena
// ---------------------------------------------------------------------------
function initArena(){
  // Canonical 20-seed headline (authoritative)
  const t = state.thesis && state.thesis.exp005;
  if(t){
    document.getElementById('arena-canon-lift').textContent='+'+t.lift_pct+'%';
    document.getElementById('arena-canon-linucb').textContent=fmt$(t.linucb_reward);
    document.getElementById('arena-canon-static').textContent=fmt$(t.static_reward);
    document.getElementById('arena-canon-stats').textContent='Wilcoxon p '+t.reward_p+" · Cohen's d = "+t.reward_cohen_d;
    document.getElementById('arena-ent-early').textContent=t.entropy_early.toFixed(3);
    document.getElementById('arena-ent-late').textContent=t.entropy_late.toFixed(3);
  }
  // Illustrative single-seed live run (seed 42)
  if(!state.exp005) return;
  const d=state.exp005;
  document.getElementById('arena-linucb-final').textContent=fmt$(d.LinUCB.cumulative_reward);
  document.getElementById('arena-static-final').textContent=fmt$(d.StaticXGB.cumulative_reward);
  const lift=((d.LinUCB.cumulative_reward/d.StaticXGB.cumulative_reward-1)*100).toFixed(1);
  document.getElementById('arena-lift').textContent='single-seed lift +'+lift+'% (illustrative — not the headline)';
  renderArenaCharts();
}
function renderArenaCharts(){
  const d=state.exp005;
  const ctxR=document.getElementById('chart-arena-reward');
  if(charts.arenaReward) charts.arenaReward.destroy();
  charts.arenaReward=new Chart(ctxR,{type:'line',data:{labels:d.LinUCB.trajectory.rounds,datasets:[
    {label:'LinUCB', data:d.LinUCB.trajectory.cumulative_rewards, borderColor:'#2E5FA3', backgroundColor:'rgba(46,95,163,0.05)', borderWidth:2, pointRadius:0, fill:true, tension:0.1},
    {label:'Static XGB', data:d.StaticXGB.trajectory.cumulative_rewards, borderColor:'#9ca3af', backgroundColor:'rgba(156,163,175,0.05)', borderWidth:2, pointRadius:0, borderDash:[5,5], fill:true, tension:0.1}
  ]}, options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:8}},y:{grid:{color:'#f3f4f6'}}}}});

  // Compute action distributions per 500-round bins for stacked area
  const bins=10; const binSize=500;
  const labels=[]; const datasets=ACTIONS.map((a,i)=>({label:a, data:[], backgroundColor:ACTION_COLORS[i], fill:true}));
  for(let b=0;b<bins;b++){ labels.push(`${b*binSize+1}-${(b+1)*binSize}`); const acts=d.LinUCB.trajectory.actions.slice(b*binSize,(b+1)*binSize); const counts=[0,0,0,0]; acts.forEach(a=>counts[a]++); const total=counts.reduce((a,b)=>a+b,0); counts.forEach((c,i)=>datasets[i].data.push(total?c/total:0)); }
  const ctxA=document.getElementById('chart-arena-actions');
  if(charts.arenaActions) charts.arenaActions.destroy();
  charts.arenaActions=new Chart(ctxA,{type:'bar',data:{labels,datasets},options:{responsive:true,maintainAspectRatio:false,scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,max:1,grid:{color:'#f3f4f6'}}},plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}}}});
}
function playArena(){}
function pauseArena(){}

// ---------------------------------------------------------------------------
// Scene 5: Benchmark
// ---------------------------------------------------------------------------
function renderBenchmark(){
  if(!state.exp007) return;
  const d=state.exp007;
  const ctx=document.getElementById('chart-benchmark');
  if(charts.benchmark) charts.benchmark.destroy();
  const colors={'LinTS':'#1e3a8a','LinUCB':'#2E5FA3','EpsilonGreedy':'#f59e0b','StaticXGB':'#9ca3af'};
  charts.benchmark=new Chart(ctx,{type:'line',data:{labels:d[0].trajectory.rounds,datasets:d.map(r=>({label:r.algorithm,data:r.trajectory.cumulative_regrets,borderColor:colors[r.algorithm],backgroundColor:colors[r.algorithm]+'10',borderWidth:2,pointRadius:0,tension:0.1}))},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{x:{grid:{display:false},ticks:{maxTicksLimit:8}},y:{grid:{color:'#f3f4f6'},title:{display:true,text:'Cumulative Regret ($)'}}}}});

  const podium=document.getElementById('benchmark-podium'); podium.innerHTML='';
  const ranked=[...d].sort((a,b)=>a.cumulative_regret-b.cumulative_regret);
  const medals=['🥇','🥈','🥉','4th'];
  ranked.forEach((r,i)=>{
    const div=document.createElement('div'); div.className='flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 border border-gray-200';
    div.innerHTML=`<div class="flex items-center gap-2"><span class="text-lg">${medals[i]}</span><span class="text-sm font-medium text-gray-800">${r.algorithm}</span></div><span class="font-mono font-bold text-gray-900">${fmt$(r.cumulative_regret)}</span>`;
    podium.appendChild(div);
  });
}

// ---------------------------------------------------------------------------
// Scene 6: Coefficients
// ---------------------------------------------------------------------------
function renderCoefficients(actionIdx){
  if(!state.coef) return;
  const c=state.coef;
  document.querySelectorAll('#coef-action-buttons button').forEach((btn,i)=>{
    btn.className='w-full text-left px-3 py-2 rounded-lg text-sm font-medium border '+(i===actionIdx?'bg-thesis-100 text-thesis-700 border-thesis-200':'bg-white text-gray-700 border-gray-200 hover:bg-gray-50');
  });
  const vals=c.theta[actionIdx];
  const featureLabels=c.features.map((f,i)=>{ const v=vals[i]; return {name:f,value:v,abs:Math.abs(v)}; }).sort((a,b)=>b.abs-a.abs).slice(0,12);
  const ctx=document.getElementById('chart-coefficients');
  if(charts.coef) charts.coef.destroy();
  charts.coef=new Chart(ctx,{type:'bar',data:{labels:featureLabels.map(f=>f.name),datasets:[{label:'Coefficient θ',data:featureLabels.map(f=>f.value),backgroundColor:featureLabels.map(f=>f.value>=0?'#2E5FA3':'#ef4444'),borderRadius:4}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{color:'#f3f4f6'}},y:{grid:{display:false}}}}});

  const insights=[
    'For STANDARD, income and low mortality are the strongest positive drivers.',
    'For RATED, mortality multiplier dominates. The bandit learns to price risk, not geography.',
    'For DECLINE, smoking and condition count are the top positive predictors of uninsurability.',
    'For REFER, coefficients are near zero — the bandit learns this is a fallback action.'
  ];
  document.getElementById('coef-insight').textContent=insights[actionIdx];
}

// ---------------------------------------------------------------------------
// Scene 7: Fairness
// ---------------------------------------------------------------------------
// Fairness is driven entirely by canonical 20-seed thesis numbers (thesis_results.json -> exp006).
// The thesis reports min/max approval rates per dimension + the EEOC four-fifths (80%) rule;
// we render those real extremes against the 80%-of-max floor (no fabricated per-group rates).
function setFairnessTab(tab){ state.fairnessTab=tab; document.getElementById('tab-region').className='text-xs px-3 py-1.5 rounded-md '+(tab==='region'?'bg-thesis-500 text-white':'bg-white border border-gray-300 text-gray-700'); document.getElementById('tab-occupation').className='text-xs px-3 py-1.5 rounded-md '+(tab==='occupation'?'bg-thesis-500 text-white':'bg-white border border-gray-300 text-gray-700'); renderFairness(); }
function renderFairness(){
  const t = state.thesis && state.thesis.exp006;
  const dim = state.fairnessTab;
  const d = t && t[dim];
  if(!d) return;
  const minPct = d.approval_min*100, maxPct = d.approval_max*100;
  const floor = maxPct * (t.eeoc_threshold_pct/100); // EEOC 4/5 floor relative to the max group
  const ctx=document.getElementById('chart-fairness');
  if(charts.fairness) charts.fairness.destroy();
  charts.fairness=new Chart(ctx,{type:'bar',data:{
    labels:['Lowest-approval group','Highest-approval group'],
    datasets:[
      {label:'Approval rate %', data:[minPct,maxPct], backgroundColor:[minPct>=floor?'#10b981':'#ef4444','#2E5FA3'], borderRadius:4, order:1},
      {label:`EEOC 4/5 floor (${t.eeoc_threshold_pct}% of max)`, data:[floor,floor], type:'line', borderColor:'#f59e0b', borderWidth:2, pointRadius:0, borderDash:[6,4], order:0}
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}},scales:{y:{grid:{color:'#f3f4f6'},max:100,title:{display:true,text:'Approval rate (%)'}},x:{grid:{display:false}}}}
  });
  // Scorecard (canonical values)
  document.getElementById('fair-dim-label').textContent = dim==='region'?'Region':'Occupation';
  const parityBadge=document.getElementById('fair-parity-badge');
  parityBadge.textContent = d.parity_pct.toFixed(2)+'% (min/max)';
  parityBadge.className='stamp '+(d.parity_pct>=t.eeoc_threshold_pct?'stamp-green':'stamp-red');
  const psiBadge=document.getElementById('fair-psi-badge');
  psiBadge.textContent = d.psi_max_sliding.toFixed(4)+' '+d.psi_zone;
  psiBadge.className='stamp '+(d.psi_zone==='GREEN'?'stamp-green':d.psi_zone==='AMBER'?'stamp-amber':'stamp-red');
  const eeoc=document.getElementById('fair-eeoc-badge');
  const pass=d.parity_pct>=t.eeoc_threshold_pct;
  eeoc.textContent = pass?('PASS ≥'+t.eeoc_threshold_pct+'%'):'FAIL';
  eeoc.className='stamp '+(pass?'stamp-green':'stamp-red');
  document.getElementById('fair-perm-note').textContent = 'Permutation test p='+d.permutation_p+' — '+d.permutation_note;
}

// ---------------------------------------------------------------------------
// Scene 8: HITL
// ---------------------------------------------------------------------------
async function hitlRecommend(){
  try{ const d=await apiGet('/api/hitl/recommend'); state.hitlCurrent=d; const a=d.applicant;
    document.getElementById('hitl-idx').textContent=d.index;
    document.getElementById('hitl-name').textContent=`${a.occupation} · ${a.region}`;
    document.getElementById('hitl-details').textContent=`${a.age}${a.gender[0]} · BMI ${a.bmi} · $${a.monthly_income_usd}/mo`;
    document.getElementById('hitl-rec').textContent=d.bandit_action_name;
    document.getElementById('hitl-rec').className='stamp '+(d.bandit_action_name==='REFER'?'stamp-amber':d.bandit_action_name==='DECLINE'?'stamp-red':'stamp-green');
  }catch(e){ console.warn(e); }
}
async function hitlOverride(action){
  if(!state.hitlCurrent)return;
  try{
    const d=await apiPost('/api/hitl/review',{index:state.hitlCurrent.index,bandit_action:state.hitlCurrent.bandit_action,override_action:action,underwriter:'DefenseDemo'});
    state.hitl.total++; state.hitl.cost+=35; state.hitl.rewards.push(d.reward);
    const align=(state.hitlCurrent.bandit_action===action)?1:0; state.hitl.align=((state.hitl.align*(state.hitl.total-1)+align)/state.hitl.total);
    document.getElementById('hitl-total').textContent=state.hitl.total;
    document.getElementById('hitl-align').textContent=(state.hitl.align*100).toFixed(1)+'%';
    document.getElementById('hitl-cost').textContent=fmt$(state.hitl.cost);
    hitlRecommend();
    renderHitlWaterfall();
  }catch(e){ console.warn(e); }
}
function renderHitlCanonical(){
  const t = state.thesis && state.thesis.exp008; if(!t) return;
  const set=(id,v)=>{const el=document.getElementById(id); if(el) el.textContent=v;};
  set('hitl-d-reward', fmt$(t.hitl_reward));
  set('hitl-d-baseline', fmt$(t.baseline_reward));
  set('hitl-d-lift', '+'+t.lift_pct+'%');
  set('hitl-d-queue', t.max_queue_depth.toFixed(2)+'%');
  set('hitl-d-cost', fmt$(t.human_cost));
  set('hitl-d-referral', t.referral_pct+'%');
  renderHitlWaterfall();
}
function renderHitlWaterfall(){
  // HITL cumulative reward (102,100) is already net of the 2,625 review cost, so we show
  // baseline -> improvement -> net (the cost is reported separately in the diagnostics card,
  // not subtracted again).
  const t = state.thesis && state.thesis.exp008;
  const baseline = t ? t.baseline_reward : 95872;
  const hitl = t ? t.hitl_reward : 102100;
  const lift = hitl - baseline;
  const ctx=document.getElementById('chart-hitl-waterfall'); if(charts.hitl) charts.hitl.destroy();
  charts.hitl=new Chart(ctx,{type:'bar',data:{labels:['Baseline','+HITL improvement','= HITL (net)'],datasets:[{data:[baseline,lift,hitl],backgroundColor:['#9ca3af','#10b981','#2E5FA3'],borderRadius:4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'#f3f4f6'}}}}});
}

// ---------------------------------------------------------------------------
// Scene 9: Drift
// ---------------------------------------------------------------------------
function renderDrift(){
  // Real EXP-009 evidence (figure is a static image); populate the canonical ratio cards.
  const t = state.thesis && state.thesis.exp009; if(!t) return;
  const wrap = document.getElementById('drift-ratios');
  if(wrap){
    wrap.innerHTML='';
    t.rows.forEach(r=>{
      const good = r.post_pre_ratio <= 0.5;
      const div=document.createElement('div'); div.className='flex items-center justify-between';
      div.innerHTML=`<span class="text-gray-700">${r.algorithm}</span><span class="stamp ${good?'stamp-green':'stamp-amber'}">${r.post_pre_ratio.toFixed(2)}×</span>`;
      wrap.appendChild(div);
    });
  }
  const cav=document.getElementById('drift-caveat'); if(cav) cav.textContent=t.caveat;
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
window.addEventListener('DOMContentLoaded', init);
