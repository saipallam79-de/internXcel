const offerApi = window.API_BASE_URL;
const offerToken = localStorage.getItem('internxcel_token');
const downloadButton = document.querySelector('[data-download-offer]');
const statusElement = document.querySelector('[data-letter-status]');

function setLetterText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function formatDate(value) {
  if (!value) return 'Pending';
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'});
}

if (!offerToken) {
  window.location.href = '../login.html';
} else {
  fetch(`${offerApi}/api/internships/me`, {headers: {Authorization: `Bearer ${offerToken}`}})
    .then((response) => { if (!response.ok) throw new Error('No active internship found.'); return response.json(); })
    .then((internship) => fetch(`${offerApi}/api/offer-letter/${internship.id}`, {headers: {Authorization: `Bearer ${offerToken}`}}))
    .then((response) => { if (!response.ok) throw new Error('Offer letter is not available yet.'); return response.json(); })
    .then((letter) => {
      setLetterText('[data-student-name]', letter.student_name);
      setLetterText('[data-student-email]', letter.email);
      setLetterText('[data-domain]', `${letter.domain} Intern`);
      setLetterText('[data-offer-id]', letter.offer_id);
      setLetterText('[data-intern-id]', letter.intern_id);
      setLetterText('[data-start-date]', formatDate(letter.start_date));
      setLetterText('[data-start-date-detail]', formatDate(letter.start_date));
      setLetterText('[data-end-date]', formatDate(letter.end_date));
      setLetterText('[data-duration]', letter.duration_days);
      statusElement.textContent = `Personalized for ${letter.student_name} · ${letter.domain}`;
      downloadButton.disabled = false;
      downloadButton.dataset.internshipId = letter.internship_id;
    })
    .catch((error) => { statusElement.textContent = error.message; });
}

downloadButton?.addEventListener('click', async () => {
  const internshipId = downloadButton.dataset.internshipId;
  if (!internshipId) return;
  downloadButton.disabled = true;
  downloadButton.textContent = 'Generating PDF...';
  try {
    const response = await fetch(`${offerApi}/api/offer-letter/${internshipId}/download`, {headers: {Authorization: `Bearer ${offerToken}`}});
    if (!response.ok) throw new Error('Unable to generate the offer letter.');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'internxcel-offer-letter.pdf';
    link.click();
    URL.revokeObjectURL(url);
    downloadButton.textContent = 'Downloaded ✓';
  } catch (error) {
    statusElement.textContent = error.message;
    downloadButton.disabled = false;
    downloadButton.textContent = 'Download PDF ↓';
  }
});
