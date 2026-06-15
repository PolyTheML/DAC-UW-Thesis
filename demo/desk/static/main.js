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

  Desk.init();
})();
