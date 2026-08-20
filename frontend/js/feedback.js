const feedbackApi = 'http://127.0.0.1:8000';
const feedbackToken = localStorage.getItem('internxcel_token');
const feedbackForm = document.querySelector('[data-feedback-form]');
const feedbackStatus = document.querySelector('[data-feedback-status]');
const ratingInputs = document.querySelectorAll('[data-rating] input');

if (!feedbackToken) window.location.href = '../login.html';
else {
  fetch(`${feedbackApi}/api/feedback`, {headers: {Authorization: `Bearer ${feedbackToken}`}}).then(() => {
    feedbackStatus.textContent = 'Feedback has already been submitted.';
  }).catch(async () => {
    const response = await fetch(`${feedbackApi}/api/dashboard/summary`, {headers: {Authorization: `Bearer ${feedbackToken}`}});
    const data = await response.json();
    if (data.internship?.status === 'completed') {
      feedbackStatus.textContent = 'We value your experience. Please share your feedback below.';
      feedbackForm.hidden = false;
      feedbackForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const rating = parseInt(document.querySelector('[data-rating] input:checked').value);
        const payload = {rating, comment: feedbackForm.comment.value, learned: feedbackForm.learned.value || null, recommend: feedbackForm.recommend.checked};
        try {
          const result = await fetch(`${feedbackApi}/api/feedback`, {method: 'POST', headers: {Authorization: `Bearer ${feedbackToken}`, 'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
          if (!result.ok) throw new Error('Unable to submit feedback.');
          document.querySelector('[data-feedback-error]').textContent = 'Thank you! Your feedback helps us improve.';
          feedbackForm.hidden = true;
        } catch (error) { document.querySelector('[data-feedback-error]').textContent = error.message; }
      });
    } else feedbackStatus.textContent = 'Feedback unlocks after completing your internship.';
  });
}

ratingInputs.forEach((input, index) => input.addEventListener('change', () => { ratingInputs.forEach((i, idx) => i.parentElement.style.opacity = idx <= index ? '1' : '0.4'); }));
