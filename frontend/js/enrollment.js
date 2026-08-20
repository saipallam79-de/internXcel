const enrollmentApi = 'http://127.0.0.1:8000';
const enrollmentToken = localStorage.getItem('internxcel_token');
const enrollmentForm = document.querySelector('#enrollment-form');
const enrollmentMessage = document.querySelector('[data-enrollment-message]');

enrollmentForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = enrollmentForm.querySelector('button');
  if (!enrollmentToken) {
    enrollmentMessage.textContent = 'Please log in or create an account before enrolling.';
    window.setTimeout(() => { window.location.href = '../login.html'; }, 700);
    return;
  }
  button.disabled = true;
  button.textContent = 'Creating your internship...';
  enrollmentMessage.textContent = '';
  try {
    const response = await fetch(`${enrollmentApi}/api/internships/apply`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', Authorization: `Bearer ${enrollmentToken}`},
      body: JSON.stringify({domain_id: Number(new FormData(enrollmentForm).get('domain_id'))}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Enrollment failed. Please try again.');
    enrollmentMessage.textContent = `Enrolled successfully. Your ID is ${data.intern_id}.`;
    enrollmentMessage.classList.add('success');
    button.textContent = 'Enrollment ready ✓';
    window.setTimeout(() => { window.location.href = '../dashboard/index.html'; }, 700);
  } catch (error) {
    enrollmentMessage.textContent = error.message;
    button.disabled = false;
    button.textContent = 'Confirm enrollment →';
  }
});
