const adminApi = 'http://127.0.0.1:8000';
const adminToken = localStorage.getItem('internxcel_token');
const adminHeaders = {Authorization: `Bearer ${adminToken}`};

function adminFetch(path, options = {}) {
  return fetch(`${adminApi}${path}`, { ...options, headers: {...adminHeaders, ...(options.headers || {})} }).then(async (response) => {
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Admin request failed.');
    return data;
  });
}

if (!adminToken) window.location.href = '../login.html';

const adminMessage = document.querySelector('[data-admin-message]');
if (adminMessage) {
  adminFetch('/api/admin/stats').then((stats) => {
    Object.entries(stats).forEach(([key, value]) => document.querySelector(`[data-stat="${key}"]`)?.replaceChildren(String(value)));
    adminMessage.textContent = 'Live platform metrics';
  }).catch((error) => { adminMessage.textContent = error.message; });
}

document.querySelector('[data-generate-offers]')?.addEventListener('click', async (event) => {
  const button = event.currentTarget;
  const result = document.querySelector('[data-offer-result]');
  button.disabled = true;
  button.textContent = 'Generating...';
  try {
    const data = await adminFetch('/api/offer-letter/generate-all', {method: 'POST'});
    result.textContent = `${data.generated} offer letters generated successfully.`;
    button.textContent = 'Generated ✓';
  } catch (error) {
    result.textContent = error.message;
    button.disabled = false;
    button.textContent = 'Try again →';
  }
});

async function loadStudents() {
  const rows = document.querySelector('[data-student-rows]');
  if (!rows) return;
  const search = document.querySelector('[data-student-search]').value;
  const status = document.querySelector('[data-student-status]').value;
  document.querySelector('[data-student-message]').textContent = 'Loading students...';
  try {
    const query = new URLSearchParams({...(search ? {search} : {}), ...(status ? {status} : {})});
    const students = await adminFetch(`/api/admin/students?${query}`);
    rows.innerHTML = students.length ? students.map((student) => `<tr><td><strong>${student.name}</strong><small>${student.email}</small></td><td>${student.college}</td><td>${student.domain || 'Not enrolled'}</td><td>${student.progress}%</td><td><span class="table-status ${student.status}">${student.status}</span></td><td><button class="table-action" type="button" data-student-id="${student.id}" data-next-status="${student.status === 'active' ? 'suspended' : 'active'}">${student.status === 'active' ? 'Suspend' : 'Reactivate'}</button></td></tr>`).join('') : '<tr><td colspan="6" class="empty-state">No students match this filter.</td></tr>';
    document.querySelector('[data-student-message]').textContent = `${students.length} student record${students.length === 1 ? '' : 's'} found.`;
    rows.querySelectorAll('[data-student-id]').forEach((button) => button.addEventListener('click', async () => {
      button.disabled = true;
      await adminFetch(`/api/admin/students/${button.dataset.studentId}/status?status=${button.dataset.nextStatus}`, {method: 'PATCH'});
      loadStudents();
    }));
  } catch (error) { document.querySelector('[data-student-message]').textContent = error.message; }
}

document.querySelector('[data-student-filter]')?.addEventListener('click', loadStudents);
if (document.querySelector('[data-student-rows]')) loadStudents();

async function loadReviews() {
  const list = document.querySelector('[data-review-list]');
  if (!list) return;
  const status = document.querySelector('[data-review-status]').value;
  document.querySelector('[data-review-message]').textContent = 'Loading submissions...';
  try {
    const reviews = await adminFetch(`/api/admin/submissions?${status ? `status=${status}` : ''}`);
    list.innerHTML = reviews.length ? reviews.map((review) => `<article class="review-card"><div><span>${review.status.replace('_', ' ').toUpperCase()}</span><h2>${review.student} · ${review.task}</h2><p>${review.domain} · ${review.module}</p><small>${review.github_url || review.live_url || 'No external link'} · ${new Date(review.submitted_at).toLocaleDateString()}</small></div><div class="review-actions"><button class="button button-primary" data-review-id="${review.id}" data-review-state="approved">Approve</button><button class="table-action" data-review-id="${review.id}" data-review-state="changes_requested">Request changes</button><button class="table-action danger" data-review-id="${review.id}" data-review-state="rejected">Reject</button></div></article>`).join('') : '<p class="empty-state">No submissions in this queue.</p>';
    document.querySelector('[data-review-message]').textContent = `${reviews.length} submission${reviews.length === 1 ? '' : 's'} loaded.`;
    list.querySelectorAll('[data-review-id]').forEach((button) => button.addEventListener('click', async () => {
      button.disabled = true;
      await adminFetch(`/api/admin/submissions/${button.dataset.reviewId}/review`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({status: button.dataset.reviewState})});
      loadReviews();
    }));
  } catch (error) { document.querySelector('[data-review-message]').textContent = error.message; }
}

document.querySelector('[data-review-filter]')?.addEventListener('click', loadReviews);
if (document.querySelector('[data-review-list]')) loadReviews();
