import React, { useState } from 'react';
import { Flame, RotateCcw, Play, Sparkles, Radio } from 'lucide-react';

const FAULT_OPTIONS = [
  { code: 'cooling_water_loss', idv: 'IDV(4)', label: 'IDV(4): Reactor Cooling Water Temp Surge', unit: 'UNIT_REACTOR', desc: 'Loss of cooling water causing thermal surge' },
  { code: 'feed_valve_closing', idv: 'IDV(6)', label: 'IDV(6): Reactant A Feed Loss', unit: 'UNIT_FEED', desc: 'Valve closure starving reactor feed Stream 1' },
  { code: 'cooling_valve_sticking', idv: 'IDV(11)', label: 'IDV(11): Reactor Cooling Valve Sticking', unit: 'UNIT_REACTOR', desc: 'Mechanical oscillation in valve XMV_10' },
  { code: 'feed_ratio_step', idv: 'IDV(1)', label: 'IDV(1): A/C Feed Ratio Step Disturbance', unit: 'UNIT_FEED', desc: 'Stoichiometric disturbance in feed Stream 4' },
  { code: 'condenser_cooling_loss', idv: 'COND', label: 'Condenser Cooling Water Failure', unit: 'UNIT_CONDENSER', desc: 'Cooling restriction in product condenser' },
];

export default function FaultControl({
  activeFault = null,
  onInjectFault,
  onClearFault,
  onTriggerRCA,
  onToggleStreaming,
  isStreaming = false,
  isLoading = false
}) {
  const [selectedFault, setSelectedFault] = useState('cooling_water_loss');

  const currentFaultObj = FAULT_OPTIONS.find(
    (f) => f.code === activeFault || f.idv === activeFault
  );

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Flame size={20} color="var(--accent-rose)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Fault Injection & Process Controls</h2>
        </div>

        <div className={`status-pill ${activeFault ? 'fault' : 'normal'}`}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: activeFault ? '#f43f5e' : '#10b981',
              boxShadow: activeFault ? '0 0 8px #f43f5e' : '0 0 8px #10b981',
            }}
          ></span>
          {activeFault ? `DISTURBANCE ACTIVE: ${activeFault}` : 'STEADY-STATE NORMAL'}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <label style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>
          Select Industrial Fault Scenario:
        </label>
        <select
          value={selectedFault}
          onChange={(e) => setSelectedFault(e.target.value)}
          style={{
            background: 'var(--bg-tertiary)',
            color: '#fff',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '0.65rem 0.85rem',
            fontFamily: 'inherit',
            fontSize: '0.88rem',
            outline: 'none',
            cursor: 'pointer',
          }}
        >
          {FAULT_OPTIONS.map((f) => (
            <option key={f.code} value={f.code}>
              {f.label} ({f.unit})
            </option>
          ))}
        </select>
      </div>

      {/* Control Buttons */}
      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <button
          className="btn-danger"
          onClick={() => onInjectFault(selectedFault)}
          disabled={isLoading}
          title="Inject selected disturbance into the plant simulator"
        >
          <Play size={15} /> Inject Fault
        </button>

        <button
          className="btn-outline"
          onClick={onClearFault}
          disabled={isLoading}
          title="Reset plant to steady-state nominal baseline"
        >
          <RotateCcw size={15} /> Reset Plant
        </button>

        {onToggleStreaming && (
          <button
            className="btn-outline"
            onClick={onToggleStreaming}
            style={{ borderColor: isStreaming ? '#10b981' : 'var(--border-subtle)' }}
            title="Toggle 1Hz TimescaleDB background telemetry publisher"
          >
            <Radio size={15} color={isStreaming ? '#10b981' : '#94a3b8'} />
            {isStreaming ? 'Streaming Active' : 'Start 1Hz Stream'}
          </button>
        )}

        <button
          className="btn-primary"
          style={{ marginLeft: 'auto' }}
          onClick={onTriggerRCA}
          disabled={isLoading}
          title="Execute multi-modal causal reasoning and generate explanation"
        >
          <Sparkles size={16} /> Trigger LangGraph RCA
        </button>
      </div>
    </div>
  );
}
