const baseUrl = String(window.POKE_LEADERBOARD_API || '').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `Leaderboard request failed (${response.status})`);
  return body;
}

if (!baseUrl) {
  window.sharedLeaderboardError = 'Shared leaderboard setup is pending.';
} else {
  window.sharedLeaderboard = {
    async list(mode) {
      const body = await request(`/leaderboard?mode=${encodeURIComponent(mode)}`);
      return body.scores;
    },
    async submit(mode, name, score) {
      const body = await request('/leaderboard', {
        method: 'POST',
        body: JSON.stringify({ mode, name, score }),
      });
      return body.result;
    },
  };
}
window.dispatchEvent(new Event('sharedLeaderboardReady'));
