import { useState, useEffect } from 'react';
import { getApplicants, decide } from '../api';

const ALGORITHMS = [
  { id: 'LinUCB', label: 'LinUCB' },
  { id: 'LinTS', label: 'LinTS' },
  { id: 'EpsilonGreedy', label: 'Epsilon-Greedy' },
  { id: 'StaticXGB', label: 'Static XGB' },
];

const ACTION_COLORS = {
  STANDARD: '#22c55e',
  RATED: '#3b82f6',
  DECLINE: '#ef4444',
  REFER: '#f59e0b',
};

export default function ApplicantTab() {
  const [applicants, setApplicants] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [algo, setAlgo] = useState('LinUCB');
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getApplicants(page, 50).then(res => {
      setApplicants(res.applicants);
      setTotal(res.total);
      if (res.applicants.length > 0) {
        setSelectedIndex(0);
        setDecision(null);
      }
    }).catch(e => setError(e.message));
  }, [page]);

  async function handleDecide() {
    setLoading(true);
    setError(null);
    try {
      const idx = (page - 1) * 50 + selectedIndex;
      const res = await decide({ applicant_index: idx, algorithm: algo, seed: 42 });
      setDecision(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const applicant = applicants[selectedIndex];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 16 }}>
      <div style={styles.sidebar}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: '#6b7280' }}>Applicants ({total})</span>
          <div style={{ display: 'flex', gap: 4 }}>
            <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} style={styles.pageBtn}>←</button>
            <span style={{ fontSize: 12, padding: '2px 6px' }}>{page}</span>
            <button disabled={page * 50 >= total} onClick={() => setPage(p => p + 1)} style={styles.pageBtn}>→</button>
          </div>
        </div>
        <div style={{ maxHeight: 520, overflowY: 'auto' }}>
          {applicants.map((a, i) => (
            <div
              key={i}
              onClick={() => { setSelectedIndex(i); setDecision(null); }}
              style={{
                padding: '8px 10px',
                borderRadius: 6,
                marginBottom: 4,
                cursor: 'pointer',
                background: selectedIndex === i ? '#eff6ff' : '#fff',
                border: selectedIndex === i ? '1px solid #bfdbfe' : '1px solid transparent',
                fontSize: 12,
              }}
            >
              <div style={{ fontWeight: 600 }}>{a.region} · {a.occupation}</div>
              <div style={{ color: '#6b7280' }}>Age {a.age}, BMI {a.bmi?.toFixed(1) ?? '?'}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        {applicant && (
          <>
            <div style={styles.card}>
              <h3 style={styles.heading}>Applicant Profile</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8 }}>
                <Field label="Region" value={applicant.region} />
                <Field label="Occupation" value={applicant.occupation} />
                <Field label="Age" value={applicant.age} />
                <Field label="BMI" value={applicant.bmi?.toFixed(1) ?? '-'} />
                <Field label="Smoking" value={applicant.is_smoking ? 'Yes' : 'No'} />
                <Field label="Exercise" value={applicant.is_exercise ? 'Yes' : 'No'} />
                <Field label="Family History" value={applicant.has_family_history ? 'Yes' : 'No'} />
                <Field label="Income (USD/mo)" value={`$${applicant.monthly_income_usd}`} />
                <Field label="Mortality Multiplier" value={applicant.mortality_multiplier?.toFixed(2) ?? '-'} />
                <Field label="Conditions" value={applicant.pre_existing_conditions || 'None'} />
              </div>
            </div>

            <div style={styles.card}>
              <h3 style={styles.heading}>Bandit Decision</h3>
              <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', marginBottom: 16 }}>
                <div>
                  <label style={styles.label}>Algorithm</label>
                  <select value={algo} onChange={e => setAlgo(e.target.value)} style={styles.select}>
                    {ALGORITHMS.map(a => <option key={a.id} value={a.id}>{a.label}</option>)}
                  </select>
                </div>
                <button onClick={handleDecide} disabled={loading} style={styles.primaryBtn}>
                  {loading ? 'Deciding…' : '▶ Get Decision'}
                </button>
              </div>
              {error && <p style={{ color: '#ef4444', fontSize: 13 }}>{error}</p>}

              {decision && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12, marginTop: 12 }}>
                  <div style={{ ...styles.metric, borderLeft: `4px solid ${ACTION_COLORS[decision.action_name]}` }}>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Chosen Action</div>
                    <div style={{ fontSize: 22, fontWeight: 700, color: ACTION_COLORS[decision.action_name] }}>
                      {decision.action_name}
                    </div>
                  </div>
                  <div style={styles.metric}>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Expected Reward (Standard)</div>
                    <div style={{ fontSize: 18, fontWeight: 700 }}>${decision.expected_rewards[0].toFixed(0)}</div>
                  </div>
                  <div style={styles.metric}>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Expected Reward (Rated)</div>
                    <div style={{ fontSize: 18, fontWeight: 700 }}>${decision.expected_rewards[1].toFixed(0)}</div>
                  </div>
                  <div style={styles.metric}>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Expected Reward (Decline)</div>
                    <div style={{ fontSize: 18, fontWeight: 700 }}>${decision.expected_rewards[2].toFixed(0)}</div>
                  </div>
                  <div style={styles.metric}>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>Expected Reward (Refer)</div>
                    <div style={{ fontSize: 18, fontWeight: 700 }}>${decision.expected_rewards[3].toFixed(0)}</div>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: 10, color: '#9ca3af', textTransform: 'uppercase', fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 500, color: '#111827' }}>{value}</div>
    </div>
  );
}

const styles = {
  sidebar: {
    background: '#f9fafb',
    borderRadius: 8,
    padding: 12,
    border: '1px solid #e5e7eb',
  },
  card: {
    background: '#fff',
    borderRadius: 8,
    padding: 16,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
    marginBottom: 16,
  },
  heading: { fontSize: 16, fontWeight: 700, margin: '0 0 12px' },
  label: { display: 'block', fontSize: 11, fontWeight: 600, color: '#374151', marginBottom: 4, textTransform: 'uppercase' },
  select: { padding: '6px 10px', fontSize: 14, borderRadius: 6, border: '1px solid #d1d5db', minWidth: 140 },
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
  pageBtn: {
    padding: '2px 8px',
    fontSize: 12,
    background: '#fff',
    border: '1px solid #d1d5db',
    borderRadius: 4,
    cursor: 'pointer',
  },
  metric: {
    background: '#f9fafb',
    borderRadius: 6,
    padding: 12,
    border: '1px solid #e5e7eb',
  },
};
