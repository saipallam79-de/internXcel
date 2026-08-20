document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-demo-action]').forEach((button) => {
    button.addEventListener('click', () => {
      button.classList.add('is-complete');
      button.setAttribute('aria-live', 'polite');
      button.textContent = 'Saved ✓';
    });
  });
});
