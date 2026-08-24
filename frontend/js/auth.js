const API_BASE = window.API_BASE_URL;

function setAuthMessage(message, success = false) {
	const element = document.querySelector('[data-auth-message]');
	if (!element) return;
	element.textContent = message;
	element.classList.toggle('success', success);
}

document.querySelector('[data-auth-form]')?.addEventListener('submit', async (event) => {
	event.preventDefault();
	const form = event.currentTarget;
	const button = form.querySelector('button[type="submit"]');
	const mode = form.dataset.authMode;
	const values = Object.fromEntries(new FormData(form).entries());

	if (mode === 'register' && values.password !== values.confirm_password) {
		setAuthMessage('Passwords do not match.');
		return;
	}

	delete values.confirm_password;
	values.year = Number(values.year);
	if (values.domain_id) values.domain_id = Number(values.domain_id);
	button.disabled = true;
	button.textContent = mode === 'login' ? 'Signing in...' : 'Creating account...';
	setAuthMessage('');

	try {
		const response = await fetch(`${API_BASE}/api/auth/${mode}`, {
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			body: JSON.stringify(values),
		});
		const data = await response.json();
		if (!response.ok) throw new Error(data.detail || 'Something went wrong. Please try again.');
		window.clearInternXcelSession?.();
		localStorage.setItem('internxcel_token', data.access_token);
		setAuthMessage('Success. Opening your dashboard...', true);
		button.textContent = 'Ready ✓';
		window.setTimeout(() => { window.location.href = 'dashboard/index.html'; }, 450);
	} catch (error) {
		setAuthMessage(error.message);
		button.disabled = false;
		button.textContent = mode === 'login' ? 'Log in →' : 'Create account →';
	}
});

function logout() {
	window.clearInternXcelSession?.();
	window.location.href = '../index.html';
}

window.internXcelLogout = logout;