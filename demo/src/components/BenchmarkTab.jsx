import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { simulate } from '../api';

const ALGORITHMS = ['LinUCB', 'LinTS', 'EpsilonGreedy', 'StaticXGB'];

export default function BenchmarkTab() {
  const [rounds, setRounds] = useState(5000);
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  async function handleRunAll() {
    setLoading(true);
    setError(null);
    setResults([]);
    try {
      const all = [];
      for (const algo of ALGORITHMS) {
        const res = await simulate({ algorithm: algo, n_rounds: Number(rounds), seed: Number(seed) });
        all.push(res);
      }
      setResults(all);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const summaryData = results.map(r => ({
    algorithm: r.algorithm,
    'Total Reward': Math.round(r.total_reward),
    'Total Regret': Math.round(r.total_regret),
    'Avg Regret (last 500)': parseFloat(r.avg_regret_last_500.toFixed(2)),
  }));

  return (
    <div>
      <div style={styles.card}>
        <h3 style={styles.heading}>Benchmark Comparison</h3>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label style={styles.label}>Rounds</label>
            <input type="number" value={rounds} onChange={e => setRounds(e.target.value)} min={100} max={20000} style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Seed</label>
            <input type="number" value={seed} onChange={e => setSeed(e.target.value)} style={styles.input} />
          </div>
          <button onClick={handleRunAll} disabled={loading} style={styles.primaryBtn}>
            {loading ? 'Running all 4 algorithms…' : '▶ Run All'}
          </button>
        </div>
        {error && <p style={{ color: '#ef4444', marginTop: 12, fontSize: 13 }}>{error}</p>}
      </div>

      {results.length > 0 && (
        <>
          <div style={styles.card}>
            <h4 style={styles.subheading}>Summary Table</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                  <th style={styles.th}>Algorithm</th>
                  <th style={styles.th}>Total Reward</th>
                  <th style={styles.th}>Total Regret</th>
                  <th style={styles.th}>Avg Regret (last 500)</th>
                  <th style={styles.th}>Time (ms)</th>
                </tr>
              </thead>
              <tbody>
                {results.map(r => (
                  <tr key={r.algorithm} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={styles.td}><strong>{r.algorithm}</strong></td>
                    <td style={styles.td}>${r.total_reward.toLocaleString()}</td>
                    <td style={styles.td}>${r.total_regret.toLocaleString()}</td>
                    <td style={styles.td}>${r.avg_regret_last_500.toFixed(2)}</td>
                    <td style={styles.td}>{r.elapsed_ms}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Total Reward</h4>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={summaryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="algorithm" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [`$${v.toLocaleString()}`, 'Total Reward']} />
                  <Bar dataKey="Total Reward" fill="#22c55e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              <h4 style={styles.subheading}>Total Regret</h4>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={summaryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="algorithm" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [`$${v.toLocaleString()}`, 'Total Regret']} />
                  <Bar dataKey="Total Regret" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
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
  th: { textAlign: 'left', padding: '8px 12px', fontSize: 12, color: '#6b7280', textTransform: 'uppercase' },
  td: { padding: '8px 12px', fontSize: 13 },
};
