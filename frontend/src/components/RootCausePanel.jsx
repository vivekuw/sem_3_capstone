import React from 'react';
import { Target, ShieldAlert, Cpu, Wrench, CheckCircle2, GitCommit, Layers } from 'lucide-react';

export default function RootCausePanel({ rcaResult = null, isLoading = false }) {
  if (isLoading) {
    return (
      <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
        <Cpu size={36} color="var(--accent-primary)" style={{ animation: 'spin 2s linear infinite' }} />
        <h3 style={{ marginTop: '1rem', fontSize: '1.1rem', fontWeight: 600 }}>
          LangGraph Agent Investigating Root Cause...
        </h3>
        <p style={{ marginTop: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Traversing Neo4j flowsheet topology, estimating Temporal precedence, and evaluating Granger causality.
        </p>
      </div>
    );
  }

  if (!rcaResult) {
    return (
      <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
        <Target size={36} color="var(--text-dim)" />
        <h3 style={{ marginTop: '0.85rem', fontSize: '1.1rem', fontWeight: 600 }}>
          System Operational & Nominal
        </h3>
        <p style={{ marginTop: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          No active disturbance detected. Select an industrial fault scenario on the left and click <strong>Trigger LangGraph RCA</strong>.
        </p>
      </div>
    );
  }

  const report = rcaResult.final_report || rcaResult.explanation_report || {};
  const rankedUnits = rcaResult.ranked_causes || [];
  const confidenceScores = rcaResult.confidence_scores || {};
  const evidenceList = rcaResult.evidence_list || report.evidence_citations || [];
  const explanationText = rcaResult.explanation_text || report.root_cause_summary || '';

  // Determine top confidence percentage
  const primaryUnit = report.primary_unit || (rankedUnits.length > 0 ? rankedUnits[0].unit_id : 'UNIT_REACTOR');
  const topConfidence = confidenceScores[primaryUnit] !== undefined
    ? Math.round(confidenceScores[primaryUnit] * 100)
    : Math.round((report.confidence_score || 0.88) * 100);

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Header & Overall Diagnosis Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <span style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', fontWeight: 800, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            ROOT CAUSE DIAGNOSIS & REASONING
          </span>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, marginTop: '0.2rem', color: '#ffffff' }}>
            {report.probable_failure_mode || 'Process Excursion Detected'}
          </h2>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Root Cause Origin: <strong style={{ color: '#f43f5e', background: 'rgba(244, 63, 94, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>{primaryUnit}</strong>
          </div>
        </div>

        {/* Confidence Percentage Badge */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>OVERALL CONFIDENCE</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
            {topConfidence}%
          </div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div style={{ width: '100%', background: 'rgba(255,255,255,0.08)', borderRadius: '6px', height: '8px', overflow: 'hidden' }}>
        <div
          style={{
            width: `${topConfidence}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #6366f1, #06b6d4, #10b981)',
            borderRadius: '6px',
            transition: 'width 0.8s ease-in-out',
          }}
        />
      </div>

      {/* Executive Summary */}
      {report.root_cause_summary && (
        <div style={{ background: 'rgba(99, 102, 241, 0.1)', borderLeft: '3px solid var(--accent-primary)', padding: '0.85rem 1rem', borderRadius: '4px' }}>
          <p style={{ fontSize: '0.90rem', color: '#e0e7ff', lineHeight: 1.5 }}>
            {report.root_cause_summary}
          </p>
        </div>
      )}

      {/* 2. Multi-Modal Ranked Causes with Confidence Bars */}
      <div>
        <h3 style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Layers size={15} color="var(--accent-primary)" />
          RANKED CANDIDATE CAUSES (TEMPORAL + GRAPH + GRANGER)
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {rankedUnits.map((cause, idx) => {
            const unitName = cause.unit_id || cause.sensor_id || `Candidate ${idx + 1}`;
            const conf = Math.round((cause.confidence_score !== undefined ? cause.confidence_score : cause.composite_score || 0.5) * 100);
            const tempScore = Math.round((cause.temporal_score || 0) * 100);
            const graphScore = Math.round((cause.graph_proximity_score || cause.graph_score || 0) * 100);
            const grangerScore = Math.round((cause.granger_score || 0) * 100);

            return (
              <div key={idx} className="cause-item" style={{ background: 'rgba(15, 23, 42, 0.75)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '0.85rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 700 }}>#{idx + 1}</span>
                    <strong style={{ fontSize: '0.95rem', color: idx === 0 ? '#f43f5e' : '#f8fafc' }}>{unitName}</strong>
                  </div>
                  <span className="score-badge" style={{ fontWeight: 700 }}>{conf}% Confidence</span>
                </div>

                {/* Composite Confidence Bar */}
                <div style={{ width: '100%', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', height: '6px', overflow: 'hidden', marginBottom: '0.5rem' }}>
                  <div
                    style={{
                      width: `${conf}%`,
                      height: '100%',
                      background: idx === 0 ? 'linear-gradient(90deg, #f43f5e, #ec4899)' : '#6366f1',
                      borderRadius: '4px',
                    }}
                  />
                </div>

                {/* Sub-Score Breakdown Bars */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', fontSize: '0.72rem', color: '#94a3b8' }}>
                  <div>
                    Temporal: <strong style={{ color: '#fff' }}>{tempScore}%</strong>
                  </div>
                  <div>
                    Graph Proximity: <strong style={{ color: '#fff' }}>{graphScore}%</strong>
                  </div>
                  <div>
                    Granger Causality: <strong style={{ color: '#fff' }}>{grangerScore}%</strong>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Physical Propagation Trajectory */}
      {report.propagation_path && report.propagation_path.length > 0 && (
        <div>
          <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <GitCommit size={15} color="var(--accent-secondary)" /> PHYSICAL PROPAGATION TRAJECTORY
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', background: 'rgba(8, 11, 18, 0.6)', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.82rem' }}>
            {report.propagation_path.map((step, i) => (
              <React.Fragment key={i}>
                <span style={{ fontWeight: 600, color: i === 0 ? '#f43f5e' : '#cbd5e1' }}>
                  {step}
                </span>
                {i < report.propagation_path.length - 1 && (
                  <span style={{ color: '#64748b' }}>➔</span>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* 4. Grounded Evidence Citations */}
      {evidenceList.length > 0 && (
        <div>
          <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShieldAlert size={15} color="var(--accent-amber)" /> GROUNDED EVIDENCE LIST
          </h3>
          <ul style={{ paddingLeft: '1.25rem', fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.6 }}>
            {evidenceList.map((cite, i) => (
              <li key={i}>{cite}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 5. Recommended Operator Actions */}
      {report.operator_actions && report.operator_actions.length > 0 && (
        <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '8px', padding: '1rem' }}>
          <h3 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#34d399', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Wrench size={16} /> RECOMMENDED OPERATOR MITIGATION
          </h3>
          <ul style={{ paddingLeft: '1.25rem', fontSize: '0.84rem', color: '#d1fae5', lineHeight: 1.6 }}>
            {report.operator_actions.map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
