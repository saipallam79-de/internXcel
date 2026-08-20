const lorApi = 'http://127.0.0.1:8000';
const lorToken = localStorage.getItem('internxcel_token');
const lorButton = document.querySelector('[data-generate-lor]');
const lorMessage = document.querySelector('[data-lor-message]');
const lorError = document.querySelector('[data-lor-error]');

if (!lorToken) window.location.href = '../login.html';
else fetch(`${lorApi}/api/lor/me`, {headers: {Authorization: `Bearer ${lorToken}`}})
  .then((response) => response.json())
  .then((data) => {
    document.querySelector('[data-lor-requirements]').innerHTML = `<span>${data.requirements.completed_modules}/${data.requirements.total_modules} modules completed</span><span>${data.requirements.approved_tasks}/${data.requirements.total_tasks} tasks approved</span>`;
    if (data.unlocked) {
      lorMessage.textContent = data.document_id ? `LOR ${data.document_id} is ready.` : 'Your recommendation is ready to generate.';
      lorButton.disabled = false;
      lorButton.textContent = data.document_id ? 'Download LOR ↓' : 'Generate LOR →';
      lorButton.dataset.documentId = data.document_id || '';
    } else lorMessage.textContent = 'Complete your internship and approved final work to unlock your personalized LOR.';
  })
  .catch((error) => { lorError.textContent = error.message; });

lorButton?.addEventListener('click', async () => {
  lorButton.disabled = true;
  lorButton.textContent = 'Preparing...';
  try {
    let documentId = lorButton.dataset.documentId;
    if (!documentId) {
      const generated = await fetch(`${lorApi}/api/lor/generate`, {method: 'POST', headers: {Authorization: `Bearer ${lorToken}`}});
      const data = await generated.json();
      if (!generated.ok) throw new Error(data.detail?.message || 'LOR requirements are incomplete.');
      documentId = data.document_id;
    }
    const response = await fetch(`${lorApi}/api/lor/${documentId}/download`, {headers: {Authorization: `Bearer ${lorToken}`}});
    if (!response.ok) throw new Error('Unable to download LOR.');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(await response.blob());
    link.download = 'internxcel-letter-of-recommendation.pdf';
    link.click();
    lorButton.textContent = 'Downloaded ✓';
  } catch (error) {
    lorError.textContent = error.message;
    lorButton.disabled = false;
    lorButton.textContent = 'Generate LOR';
  }
});
