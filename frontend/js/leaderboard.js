const leaderboardApi = 'http://127.0.0.1:8000';
const leaderboardToken = localStorage.getItem('internxcel_token');
const leaderboardRows = document.querySelector('[data-leaderboard-rows]');
const leaderboardStatus = document.querySelector('[data-leaderboard-status]');

if (!leaderboardToken) window.location.href = 'login.html';
else {
  fetch(`${leaderboardApi}/api/leaderboard`, {headers: {Authorization: `Bearer ${leaderboardToken}`}}).then((response) => response.json()).then((data) => {
    if (!data.length) {
      leaderboardStatus.textContent = 'Leaderboard will populate once students earn rewards.';
      return;
    }
    leaderboardStatus.hidden = true;
    leaderboardRows.innerHTML = data.map((entry, index) => `<tr><td class="rank-cell"><strong>#${index + 1}</strong></td><td>${entry.student}</td><td><strong>${entry.points}</strong></td><td>${entry.completed_modules}</td></tr>`).join('');
  }).catch((error) => { leaderboardStatus.textContent = `Error loading leaderboard: ${error.message}`; });
}
