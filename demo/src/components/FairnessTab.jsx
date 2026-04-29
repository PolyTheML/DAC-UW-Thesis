import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { fairness } from '../api';

const ALGORITHMS = [
  { id: 'LinUCB', label: 'LinUCB' },
  { id: 'LinTS', label: 'LinTS' },
  { id: 'EpsilonGreedy', label: 'Epsilon-Greedy' },
  { id: 'StaticXGB', label: 'Static XGB' },
];

export default function FairnessTab() {
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
      const res = await fairness(algo, Number(rounds), Number(seed));
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const regionData = result?.region_approval_rates.map(r => ({
    name: r.region,
    rate: r.rate * 100,
    parity: r.parity_ok,
  })) || [];

  const occData = result?.occupation_approval_rates.map(r => ({
    name: r.occupation,
    rate: r.rate * 100,
    parity: r.parity_ok,
  })) || [];

  const maxRegionRate = result ? Math.max(...result.region_approval_rates.map(r => r.rate)) * 100 : 0;
  const maxOccRate = result ? Math.max(...result.occupation_approval_rates.map(r => r.rate)) * 100 : 0;

  return (
    <div>
      <div style={styles.card}>
        <h3 style={styles.heading}>Fairness Audit</h3>
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
            {loading ? 'Running…' : '▶ Run Audit'}
          </button>
        </div>
        {error && <p style={{ color: '#ef4444', marginTop: 12, fontSize: 13 }}>{error}</p>}
      </div>

      {result && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 20 }}>
            <MetricCard label="Region PSI" value={result.region_psi.toFixed(4)} status={result.region_psi_status} />
            <MetricCard label="Occupation PSI" value={result.occupation_psi.toFixed(4)} status={result.occupation_psi_status} />
            <MetricCard label="Parity Check" value={result.parity_check_passed ? 'PASSED' : 'FAILED'} status={result.parity_check_passed ? 'GREEN' : 'RED'} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 16 }}>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Approval Rate by Region</h4>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={regionData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={100} />
                  <Tooltip formatter={(v) => [`${v.toFixed(1)}%`, 'Approval Rate']} />
                  <ReferenceLine x={maxRegionRate * 0.5} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: '50% parity', fontSize: 10, fill: '#f59e0b' }} />
                  <Bar dataKey="rate" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Approval Rate by Occupation</h4>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={occData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={120} />
                  <Tooltip formatter={(v) => [`${v.toFixed(1)}%`, 'Approval Rate']} />
                  <ReferenceLine x={maxOccRate * 0.5} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: '50% parity', fontSize: 10, fill: '#f59e0b' }} />
                  <Bar dataKey="rate" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value, status }) {
  const color = status === 'GREEN' ? '#22c55e' : status === 'AMBER' ? '#f59e0b' : '#ef4444';
  return (
    <div style={styles.card}>
      <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color }}>{value}</div>
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
