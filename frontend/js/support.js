const supportApi = 'http://127.0.0.1:8000';
const supportToken = localStorage.getItem('internxcel_token');
const supportForm = document.querySelector('[data-support-form]');
const supportStatus = document.querySelector('[data-support-status]');
const supportTickets = document.querySelector('[data-support-tickets]');
const supportError = document.querySelector('[data-support-error]');

if (!supportToken) window.location.href = '../login.html';
else {
  function loadTickets() {
    fetch(`${supportApi}/api/support/me`, {headers: {Authorization: `Bearer ${supportToken}`}}).then((response) => response.json()).then((tickets) => {
      supportStatus.textContent = tickets.length ? `${tickets.length} ticket${tickets.length === 1 ? '' : 's'}` : 'No tickets yet.';
      supportTickets.innerHTML = tickets.length ? tickets.map((ticket) => `<article class="support-ticket"><div><span class="ticket-status ${ticket.status}">${ticket.status.replace('_', ' ').toUpperCase()}</span><h3>${ticket.subject}</h3><p>${ticket.message}</p><small>${new Date(ticket.created_at).toLocaleDateString()}</small></div><div>${ticket.admin_reply ? `<p class="admin-reply"><strong>Support team:</strong> ${ticket.admin_reply}</p>` : '<p class="empty-state">Awaiting response</p>'}</div></article>`).join('') : '<p class="empty-state">Create a ticket to get in touch with our support team.</p>';
    }).catch(() => { supportStatus.textContent = 'Unable to load tickets.'; });
  }

  loadTickets();
  supportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {subject: supportForm.subject.value, category: supportForm.category.value, message: supportForm.message.value};
    try {
      const result = await fetch(`${supportApi}/api/support`, {method: 'POST', headers: {Authorization: `Bearer ${supportToken}`, 'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
      if (!result.ok) throw new Error('Unable to create ticket.');
      supportForm.reset();
      supportError.textContent = 'Ticket created. Our team will respond soon.';
      setTimeout(loadTickets, 500);
    } catch (error) { supportError.textContent = error.message; }
  });
}
