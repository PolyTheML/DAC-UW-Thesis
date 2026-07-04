// View toggle + bootstrap. Desk/Learn render functions live in desk.js / learn.js.
(function () {
  const tabDesk = document.getElementById('tab-desk');
  const tabLearn = document.getElementById('tab-learn');
  const viewDesk = document.getElementById('view-desk');
  const viewLearn = document.getElementById('view-learn');
  let learnInitialized = false;

  function show(which) {
    const desk = which === 'desk';
    tabDesk.classList.toggle('active', desk);
    tabLearn.classList.toggle('active', !desk);
    viewDesk.classList.toggle('active', desk);
    viewLearn.classList.toggle('active', !desk);
    if (!desk && !learnInitialized) { Learn.init(); learnInitialized = true; }
  }
  tabDesk.addEventListener('click', () => show('desk'));
  tabLearn.addEventListener('click', () => show('learn'));

  async function renderFairnessPanel() {
    try {
      const f = await fetch('/api/fairness').then(r => r.json());
      const cell = (id, d, zone) => {
        const el = document.getElementById(id);
        el.innerHTML = `${d.label}: <span class="badge z-${d.status}">${d.status}</span>
          ${d.psi.toFixed(3)} <span style="font-size:.7rem">(canonical: ${zone})</span>`;
        el.title = f.note;
      };
      cell('fair-region', f.region, f.canonical.region_zone);
      cell('fair-occupation', f.occupation, f.canonical.occupation_zone);
    } catch (e) { /* panel stays with placeholder dashes; non-fatal */ }
  }

  Desk.init();
  renderFairnessPanel();
})();
