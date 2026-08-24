const modulesApi = window.API_BASE_URL;
const modulesToken = localStorage.getItem('internxcel_token');
const pathElement = document.querySelector('[data-learning-path]');
const statusElement = document.querySelector('[data-learning-status]');

if (!modulesToken) window.location.href = '../login.html';
else fetch(`${modulesApi}/api/internships/me`, {headers: {Authorization: `Bearer ${modulesToken}`}})
  .then((response) => {
    if (response.status === 404) {
      statusElement.textContent = 'No active internship yet.';
      pathElement.innerHTML = '<p class="empty-state">Your learning path unlocks after enrollment. <a href="../internship/index.html">Choose your internship path</a> to begin.</p>';
      return null;
    }
    if (!response.ok) throw new Error('Unable to load your internship.');
    return response.json();
  })
  .then((internship) => {
    if (!internship) return;
    return fetch(`${modulesApi}/api/modules/learning-path/${internship.id}`, {headers: {Authorization: `Bearer ${modulesToken}`}});
  })
  .then((response) => {
    if (!response || response.status === 404) {
      statusElement.textContent = 'No learning path available yet.';
      pathElement.innerHTML = '<p class="empty-state">Your curriculum will appear after enrollment and domain setup.</p>';
      return null;
    }
    if (!response.ok) throw new Error('Unable to load your learning path.');
    return response.json();
  })
  .then((modules) => {
    if (!modules) return;
    const completed = modules.filter((module) => module.status === 'completed').length;
    statusElement.textContent = `${completed} of ${modules.length} milestones complete. Every next step unlocks after approved work.`;
    pathElement.innerHTML = modules.map((module) => `<article class="learning-module ${module.status}"><div class="module-status">${module.status === 'completed' ? '✓ Completed' : module.status === 'available' ? '◆ Available' : '🔒 Locked'}</div><div><small>${module.module_number === 0 ? 'PREREQUISITE ONBOARDING' : `MODULE ${String(module.module_number).padStart(2, '0')}`} · ${module.estimated_duration || 5} DAYS</small><h2>${module.title}</h2><p>${module.description || ''}</p><small>${module.learning_objectives || 'Practical skill building, project work, and review.'}</small></div>${module.status === 'available' ? `<a class="button button-primary" href="tasks.html?module_id=${module.id}">Open module →</a>` : '<span class="module-lock-note">Sequential path</span>'}</article>`).join('');
  })
  .catch(() => { statusElement.textContent = 'Something went wrong. Please refresh and try again.'; });
