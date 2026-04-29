import { useState } from 'react';
import SimulatorTab from './components/SimulatorTab';
import BenchmarkTab from './components/BenchmarkTab';
import FairnessTab from './components/FairnessTab';
import ApplicantTab from './components/ApplicantTab';

const TABS = [
  { id: 'simulator', label: 'Simulator' },
  { id: 'benchmark', label: 'Benchmark' },
  { id: 'fairness', label: 'Fairness Audit' },
  { id: 'applicant', label: 'Applicant Explorer' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '20px 16px 40px' }}>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: '0 0 4px' }}>
          DAC Thesis Demo — Adaptive Health Insurance Underwriting
        </h1>
        <p style={{ fontSize: 13, color: '#6b7280', margin: 0 }}>
          Contextual Bandits (LinUCB, LinTS, Epsilon-Greedy) vs Static XGB Baseline on Cambodia Dataset
        </p>
      </header>

      <nav style={{ display: 'flex', gap: 8, marginBottom: 20, borderBottom: '1px solid #e5e7eb', paddingBottom: 8 }}>
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: '6px 14px',
              borderRadius: 6,
              border: 'none',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              background: activeTab === t.id ? '#2563eb' : 'transparent',
              color: activeTab === t.id ? '#fff' : '#374151',
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {activeTab === 'simulator' && <SimulatorTab />}
      {activeTab === 'benchmark' && <BenchmarkTab />}
      {activeTab === 'fairness' && <FairnessTab />}
      {activeTab === 'applicant' && <ApplicantTab />}
    </div>
  );
}
