const profileApi = window.API_BASE_URL;
const profileToken = localStorage.getItem('internxcel_token');
const profileForm = document.querySelector('[data-profile-form]');
const profileStatus = document.querySelector('[data-profile-status]');

function setProfileStatus(message, success = false) {
	if (!profileStatus) return;
	profileStatus.textContent = message;
	profileStatus.classList.toggle('success', success);
}

function fillProfile(user) {
	Object.entries(user).forEach(([key, value]) => {
		const field = profileForm?.elements.namedItem(key);
		if (field) field.value = value ?? '';
	});
	document.querySelector('[data-profile-name]')?.replaceChildren(user.full_name);
	document.querySelector('[data-profile-summary]')?.replaceChildren(`${user.college} · ${user.degree} · ${user.branch}`);
}

if (!profileToken) {
	window.location.href = '../login.html';
} else {
	fetch(`${profileApi}/api/auth/me`, {headers: {Authorization: `Bearer ${profileToken}`}})
		.then(async (response) => {
			const data = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(data.detail || 'Unable to load your profile.');
			return data;
		})
		.then((user) => {
			fillProfile(user);
			return fetch(`${profileApi}/api/internships/me`, {headers: {Authorization: `Bearer ${profileToken}`}})
				.then((response) => response.ok ? response.json() : null)
				.then((internship) => internship ? fetch(`${profileApi}/api/domains/${internship.domain_id}`).then((response) => response.ok ? response.json() : null) : null)
				.then((domain) => { if (domain) document.querySelector('[data-profile-summary]')?.replaceChildren(`${user.college} · ${user.degree} · ${user.branch} · ${domain.name}`); });
		})
		.catch((error) => setProfileStatus(error.message));
}

profileForm?.addEventListener('submit', async (event) => {
	event.preventDefault();
	const button = profileForm.querySelector('button[type="submit"]');
	button.disabled = true;
	setProfileStatus('Saving your details...');
	try {
		const values = Object.fromEntries(new FormData(profileForm).entries());
		values.year = Number(values.year);
		const response = await fetch(`${profileApi}/api/users/me`, {
			method: 'PATCH',
			headers: {'Content-Type': 'application/json', Authorization: `Bearer ${profileToken}`},
			body: JSON.stringify(values),
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(data.detail || 'Unable to save your profile.');
		fillProfile(data);
		setProfileStatus('Profile updated successfully.', true);
	} catch (error) {
		setProfileStatus(error.message);
	} finally {
		button.disabled = false;
	}
});
