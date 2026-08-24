const certificateApi = window.API_BASE_URL;
const certificateToken = localStorage.getItem('internxcel_token');
const certificateRequirements = document.querySelector('[data-certificate-requirements]');
const certificateMessage = document.querySelector('[data-certificate-message]');
const certificateError = document.querySelector('[data-certificate-error]');
const generateButton = document.querySelector('[data-generate-certificate]');

if (!certificateToken) {
  window.location.href = '../login.html';
} else {
  fetch(`${certificateApi}/api/certificate/me`, {headers: {Authorization: `Bearer ${certificateToken}`}})
    .then(async (response) => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Unable to load certificate status.');
      return data;
    })
    .then((data) => {
      const requirements = data.requirements || {};
      certificateRequirements.innerHTML = `
        <span>${requirements.completed_modules ?? 0}/${requirements.total_modules ?? 0} modules complete</span>
        <span>${requirements.approved_tasks ?? 0}/${requirements.total_tasks ?? 0} tasks approved</span>
      `;

      if (data.unlocked) {
        certificateMessage.textContent = data.certificate_id ? `Certificate ${data.certificate_id} is ready to download.` : 'Your certificate is ready to generate.';
        generateButton.disabled = false;
        generateButton.textContent = 'Download certificate ↓';
        generateButton.dataset.certificateId = data.certificate_id || '';
      } else {
        certificateMessage.textContent = 'Complete all modules and approved tasks to unlock your certificate.';
        generateButton.disabled = true;
      }
    })
    .catch((error) => {
      certificateMessage.textContent = 'Certificate availability could not be checked.';
      certificateError.textContent = error.message;
    });
}

generateButton?.addEventListener('click', async () => {
  const certificateId = generateButton.dataset.certificateId || '';
  generateButton.disabled = true;
  generateButton.textContent = certificateId ? 'Preparing PDF...' : 'Generating certificate...';

  try {
    let id = certificateId;
    if (!id) {
      const response = await fetch(`${certificateApi}/api/certificate/generate`, {
        method: 'POST',
        headers: {Authorization: `Bearer ${certificateToken}`},
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail?.message || data.detail || 'Certificate requirements are incomplete.');
      id = data.certificate_id;
    }

    const downloadResponse = await fetch(`${certificateApi}/api/certificate/${id}/download`, {
      headers: {Authorization: `Bearer ${certificateToken}`},
    });
    if (!downloadResponse.ok) throw new Error('Unable to download the certificate.');

    const blob = await downloadResponse.blob();
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = 'internxcel-certificate.pdf';
    link.click();
    URL.revokeObjectURL(downloadUrl);

    certificateMessage.textContent = `Certificate ${id} downloaded successfully.`;
    generateButton.textContent = 'Downloaded ✓';
  } catch (error) {
    certificateError.textContent = error.message;
    generateButton.disabled = false;
    generateButton.textContent = 'Generate certificate';
  }
});
