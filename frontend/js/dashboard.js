const dashboardApi = window.API_BASE_URL;
const dashboardToken = localStorage.getItem('internxcel_token');
const dashboardHeaders = {Authorization: `Bearer ${dashboardToken}`};

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function getInitials(name) {
  return (name || 'U')
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase() || 'U';
}

function renderDashboard(data) {
  const displayName = data.student.name || 'Student';
  setText('[data-welcome-name]', displayName);
  setText('[data-avatar]', getInitials(displayName));
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
  setText('[data-next-step]', data.modules.current ? `Complete ${data.modules.current.title.toLowerCase()} and submit its practical task to unlock the next milestone.` : 'Your internship path is complete.');
  const bar = document.querySelector('[data-progress-bar]');
  if (bar) bar.style.width = `${data.internship.progress}%`;
  const notifications = document.querySelector('[data-notifications]');
  if (notifications && data.notifications.length) {
    notifications.innerHTML = data.notifications.map((item) => `<div class="activity-item"><span>✦</span><div><strong>${item.title}</strong><small>${item.message}</small></div></div>`).join('');
  }
  setText('[data-notification-count]', data.notifications.length);
}

function renderNoEnrollment(user) {
  if (user) {
    const displayName = user.full_name || 'Student';
    setText('[data-welcome-name]', displayName);
    setText('[data-avatar]', getInitials(displayName));
  }
  setText('[data-domain-name]', 'No internship enrolled yet');
  setText('[data-intern-id]', 'Not assigned');
  setText('[data-internship-status]', 'Not enrolled');
  setText('[data-progress-value]', '0');
  setText('[data-module-count]', 'Enroll to start your learning path');
  setText('[data-current-module]', 'Choose an internship path');
  setText('[data-current-module-number]', 'Start by selecting a domain');
  setText('[data-pending-tasks]', '0');
  setText('[data-reward-points]', '0');
  setText('[data-certificate-status]', 'Complete an internship to unlock');
  setText('[data-next-step]', 'Choose an internship path to begin your learning journey.');
  const bar = document.querySelector('[data-progress-bar]');
  if (bar) bar.style.width = '0%';
}

if (!dashboardToken) {
  window.location.href = '../login.html';
} else {
  fetch(`${dashboardApi}/api/dashboard/summary`, {headers: dashboardHeaders})
    .then(async (response) => {
      if (response.status === 404) {
        return fetch(`${dashboardApi}/api/auth/me`, {headers: dashboardHeaders})
          .then((profileResponse) => profileResponse.ok ? profileResponse.json() : null)
          .then(renderNoEnrollment)
          .then(() => null);
      }
      if (response.status === 401) throw new Error('Session expired');
      if (!response.ok) throw new Error('Unable to load your dashboard.');
      return response.json();
    })
    .then((data) => { if (data) renderDashboard(data); })
    .catch((error) => {
      if (error.message !== 'Session expired') {
        setText('[data-domain-name]', 'Dashboard unavailable');
        setText('[data-intern-id]', 'Please try again');
        setText('[data-internship-status]', 'Unavailable');
        setText('[data-current-module]', error.message);
        return;
      }
      localStorage.removeItem('internxcel_token');
      window.location.href = '../login.html';
    });
}

document.querySelectorAll('[data-logout]').forEach((link) => link.addEventListener('click', (event) => {
  event.preventDefault();
  window.clearInternXcelSession?.();
  window.location.href = '../index.html';
}));
document.querySelector('[data-sidebar-toggle]')?.addEventListener('click', () => document.body.classList.toggle('sidebar-open'));
