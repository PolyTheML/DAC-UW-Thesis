import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { simulate } from '../api';

const ALGORITHMS = [
  { id: 'LinUCB', label: 'LinUCB' },
  { id: 'LinTS', label: 'LinTS' },
  { id: 'EpsilonGreedy', label: 'Epsilon-Greedy' },
  { id: 'StaticXGB', label: 'Static XGB' },
];

export default function SimulatorTab() {
  const [algo, setAlgo] = useState('LinUCB');
  const [rounds, setRounds] = useState(5000);
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await simulate({ algorithm: algo, n_rounds: Number(rounds), seed: Number(seed) });
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const chartData = result
    ? result.cumulative_rewards.map((_, i) => ({
        round: i + 1,
        reward: result.cumulative_rewards[i],
        regret: result.cumulative_regrets[i],
      }))
    : [];

  return (
    <div>
      <div style={styles.card}>
        <h3 style={styles.heading}>Run Simulation</h3>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label style={styles.label}>Algorithm</label>
            <select value={algo} onChange={e => setAlgo(e.target.value)} style={styles.select}>
              {ALGORITHMS.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
            </select>
          </div>
          <div>
            <label style={styles.label}>Rounds</label>
            <input type="number" value={rounds} onChange={e => setRounds(e.target.value)} min={100} max={20000} style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Seed</label>
            <input type="number" value={seed} onChange={e => setSeed(e.target.value)} style={styles.input} />
          </div>
          <button onClick={handleRun} disabled={loading} style={styles.primaryBtn}>
            {loading ? 'Running…' : '▶ Run Simulation'}
          </button>
        </div>
        {error && <p style={{ color: '#ef4444', marginTop: 12, fontSize: 13 }}>{error}</p>}
      </div>

      {result && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12, marginBottom: 20 }}>
            <MetricCard label="Total Reward" value={`$${result.total_reward.toLocaleString()}`} />
            <MetricCard label="Total Regret" value={`$${result.total_regret.toLocaleString()}`} />
            <MetricCard label="Avg Regret (last 500)" value={`$${result.avg_regret_last_500.toFixed(2)}`} />
            <MetricCard label="Time" value={`${result.elapsed_ms} ms`} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16, marginBottom: 20 }}>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Cumulative Reward</h4>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="round" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [`$${v.toLocaleString()}`, '']} />
                  <Line type="monotone" dataKey="reward" stroke="#22c55e" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Cumulative Regret</h4>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="round" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [`$${v.toLocaleString()}`, '']} />
                  <Line type="monotone" dataKey="regret" stroke="#ef4444" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={styles.card}>
            <h4 style={styles.subheading}>Action Distribution</h4>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {Object.entries(result.action_distribution).map(([name, pct]) => (
                <div key={name} style={{ textAlign: 'center', minWidth: 100 }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: '#2563eb' }}>{(pct * 100).toFixed(1)}%</div>
                  <div style={{ fontSize: 12, color: '#6b7280' }}>{name}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div style={styles.card}>
      <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>{value}</div>
    </div>
  );
}

const styles = {
  card: {
    background: '#fff',
    borderRadius: 8,
    padding: 16,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
    marginBottom: 16,
  },
  heading: { fontSize: 16, fontWeight: 700, margin: '0 0 12px' },
  subheading: { fontSize: 14, fontWeight: 600, margin: '0 0 10px' },
  label: { display: 'block', fontSize: 11, fontWeight: 600, color: '#374151', marginBottom: 4, textTransform: 'uppercase' },
  select: { padding: '6px 10px', fontSize: 14, borderRadius: 6, border: '1px solid #d1d5db', minWidth: 140 },
  input: { padding: '6px 10px', fontSize: 14, borderRadius: 6, border: '1px solid #d1d5db', width: 100 },
  primaryBtn: {
    padding: '8px 16px',
    fontSize: 14,
    fontWeight: 600,
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
  },
};
