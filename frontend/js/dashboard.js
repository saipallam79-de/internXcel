const dashboardApi = 'http://127.0.0.1:8000';
const dashboardToken = localStorage.getItem('internxcel_token');
const dashboardHeaders = {Authorization: `Bearer ${dashboardToken}`};

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function renderDashboard(data) {
  const firstName = data.student.name.split(' ')[0];
  setText('[data-welcome-name]', `${firstName}.`);
  setText('[data-avatar]', data.student.name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase());
  setText('[data-domain-name]', data.internship.domain);
  setText('[data-intern-id]', data.internship.intern_id);
  setText('[data-internship-status]', data.internship.status);
  setText('[data-progress-value]', data.internship.progress);
  setText('[data-module-count]', `${data.modules.completed} of ${data.modules.total} modules complete`);
  setText('[data-current-module]', data.modules.current?.title || 'All modules complete');
  setText('[data-current-module-number]', data.modules.current ? `Module ${data.modules.current.module_number} · Ready next` : 'Certificate unlocked');
  setText('[data-pending-tasks]', data.tasks.pending);
  setText('[data-reward-points]', data.rewards.points);
  setText('[data-certificate-status]', data.documents.certificate ? 'Certificate available to download' : 'Complete the path to unlock');
  const bar = document.querySelector('[data-progress-bar]');
  if (bar) bar.style.width = `${data.internship.progress}%`;
  const notifications = document.querySelector('[data-notifications]');
  if (notifications && data.notifications.length) {
    notifications.innerHTML = data.notifications.map((item) => `<div class="activity-item"><span>✦</span><div><strong>${item.title}</strong><small>${item.message}</small></div></div>`).join('');
  }
  setText('[data-notification-count]', data.notifications.length);
}

if (!dashboardToken) {
  window.location.href = '../login.html';
} else {
  fetch(`${dashboardApi}/api/dashboard/summary`, {headers: dashboardHeaders})
    .then((response) => {
      if (!response.ok) throw new Error('Session expired');
      return response.json();
    })
    .then(renderDashboard)
    .catch(() => {
      localStorage.removeItem('internxcel_token');
      window.location.href = '../login.html';
    });
}

document.querySelectorAll('[data-logout]').forEach((link) => link.addEventListener('click', () => localStorage.removeItem('internxcel_token')));
document.querySelector('[data-sidebar-toggle]')?.addEventListener('click', () => document.body.classList.toggle('sidebar-open'));
