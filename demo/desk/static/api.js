// Thin fetch wrappers for the four desk endpoints.
const API = {
  async fields() { return (await fetch('/api/applicant/fields')).json(); },
  async random() { return (await fetch('/api/applicant/random')).json(); },
  async canonical() { return (await fetch('/api/canonical')).json(); },
  async score(applicant) {
    const res = await fetch('/api/score', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(applicant),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail ? JSON.stringify(detail.detail) : `HTTP ${res.status}`);
    }
    return res.json();
  },
  async learn(payload) {
    const res = await fetch('/api/learn/run', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};
