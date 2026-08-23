const verifyApi = window.API_BASE_URL;
const verifyForm = document.querySelector('#verify-form');
const verifyMessage = document.querySelector('#verification-message');
const verifyResult = document.querySelector('#verification-result');

verifyForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = verifyForm.querySelector('button');
  const certificateId = document.querySelector('#certificate-id').value.trim();
  button.disabled = true;
  button.textContent = 'Checking...';
  verifyMessage.textContent = '';
  verifyResult.hidden = true;
  try {
    const response = await fetch(`${verifyApi}/api/certificate/verify/${encodeURIComponent(certificateId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Certificate not found or invalid.');
    document.querySelector('[data-verify-student]').textContent = data.student;
    document.querySelector('[data-verify-domain]').textContent = data.domain;
    document.querySelector('[data-verify-status]').textContent = data.status;
    document.querySelector('[data-verify-date]').textContent = data.issue_date;
    verifyResult.hidden = false;
    button.textContent = 'Verified ✓';
  } catch (error) {
    verifyMessage.textContent = error.message;
    button.disabled = false;
    button.textContent = 'Verify certificate →';
  }
});
