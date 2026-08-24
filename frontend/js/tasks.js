const tasksApi = window.API_BASE_URL;
const tasksToken = localStorage.getItem('internxcel_token');
const taskList = document.querySelector('[data-task-list]');
const taskStatus = document.querySelector('[data-task-status]');
const submissionPanel = document.querySelector('[data-submission-panel]');
const taskForm = document.querySelector('[data-task-form]');

if (!tasksToken) window.location.href = '../login.html';
else fetch(`${tasksApi}/api/tasks`, {headers: {Authorization: `Bearer ${tasksToken}`}})
  .then((response) => {
    if (response.status === 404) {
      taskStatus.textContent = 'No active internship yet.';
      taskList.innerHTML = '<p class="empty-state">Your task board opens after enrollment. <a href="../internship/index.html">Choose your internship path</a> to get started.</p>';
      return null;
    }
    if (!response.ok) throw new Error('Unable to load your tasks.');
    return response.json();
  })
  .then((tasks) => {
    if (!tasks) return;
    taskStatus.textContent = tasks.length ? `${tasks.length} practical task${tasks.length === 1 ? '' : 's'} in your current domain.` : 'No tasks are available yet.';
    taskList.innerHTML = tasks.map((task) => `<article class="task-row"><div><span>${task.module_status === 'locked' ? 'LOCKED' : task.module_number === 0 ? 'PREREQUISITE ONBOARDING' : `MODULE ${String(task.module_number).padStart(2, '0')}`}</span><h2>${task.title}</h2><p>${task.description || ''}</p><small>${task.instructions || ''}</small><small>${task.required_links || task.submission_type || 'Submission required'}</small></div><button class="button button-primary" type="button" data-open-task="${task.id}" data-task-title="${task.title}" ${task.module_status === 'locked' ? 'disabled' : ''}>${task.module_status === 'locked' ? 'Locked' : task.status === 'completed' ? 'Completed ✓' : 'Submit work →'}</button></article>`).join('');
    taskList.querySelectorAll('[data-open-task]').forEach((button) => button.addEventListener('click', () => {
      submissionPanel.hidden = false;
      taskForm.elements.task_id.value = button.dataset.openTask;
      document.querySelector('[data-submission-title]').textContent = button.dataset.taskTitle;
      submissionPanel.scrollIntoView({behavior: 'smooth'});
    }));
  })
  .catch(() => { taskStatus.textContent = 'Something went wrong. Please refresh and try again.'; });

taskForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = taskForm.querySelector('button[type="submit"]');
  const message = document.querySelector('[data-task-message]');
  const values = Object.fromEntries(new FormData(taskForm).entries());
  const taskId = values.task_id;
  delete values.task_id;
  Object.keys(values).forEach((key) => { if (!values[key]) delete values[key]; });
  button.disabled = true;
  button.textContent = 'Submitting...';
  try {
    const response = await fetch(`${tasksApi}/api/tasks/${taskId}/submit`, {method: 'POST', headers: {'Content-Type': 'application/json', Authorization: `Bearer ${tasksToken}`}, body: JSON.stringify(values)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Submission failed.');
    message.textContent = 'Submitted for review ✓';
    message.classList.add('success');
    button.textContent = 'Submitted ✓';
  } catch (error) {
    message.textContent = error.message;
    button.disabled = false;
    button.textContent = 'Submit for review →';
  }
});
