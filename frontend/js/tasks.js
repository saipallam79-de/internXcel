const tasksApi = 'http://127.0.0.1:8000';
const tasksToken = localStorage.getItem('internxcel_token');
const taskList = document.querySelector('[data-task-list]');
const taskStatus = document.querySelector('[data-task-status]');
const submissionPanel = document.querySelector('[data-submission-panel]');
const taskForm = document.querySelector('[data-task-form]');

if (!tasksToken) window.location.href = '../login.html';
else fetch(`${tasksApi}/api/tasks`, {headers: {Authorization: `Bearer ${tasksToken}`}})
  .then((response) => response.json())
  .then((tasks) => {
    taskStatus.textContent = tasks.length ? `${tasks.length} practical task${tasks.length === 1 ? '' : 's'} in your current domain.` : 'No pending tasks. You are all caught up.';
    taskList.innerHTML = tasks.map((task) => `<article class="task-row"><div><span>TASK ${String(task.id).padStart(2, '0')}</span><h2>${task.title}</h2><p>${task.description || ''}</p><small>${task.submission_type || 'github_url'} · ${task.deadline || 'No deadline'}</small></div><button class="button button-primary" type="button" data-open-task="${task.id}" data-task-title="${task.title}">Submit work →</button></article>`).join('');
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
