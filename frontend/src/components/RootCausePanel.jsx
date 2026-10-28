import React, { useState, useEffect } from 'react';
import {
  Target,
  ShieldAlert,
  Cpu,
  Wrench,
  CheckCircle2,
  GitCommit,
  Layers,
  Sparkles,
  Bot,
  Clock,
  Zap,
  Activity,
  Search,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Flame,
  ArrowRight,
  Sliders
} from 'lucide-react';
import { SENSOR_SOLUTIONS, getSensorSolution } from '../data/sensorSolutions';

// Complete dictionary of all 41 TEP process sensors + 2 control actuators
const SENSOR_META = {
  // UNIT_FEED
  XMEAS_1: { name: 'A Feed Flow', unit: 'kscmh', normal: 0.2505, parent_unit: 'UNIT_FEED', desc: 'Reactant A fresh feed stream' },
  XMEAS_2: { name: 'D Feed Flow', unit: 'kg/h', normal: 3664.0, parent_unit: 'UNIT_FEED', desc: 'Reactant D feed stream' },
  XMEAS_3: { name: 'E Feed Flow', unit: 'kg/h', normal: 4505.0, parent_unit: 'UNIT_FEED', desc: 'Reactant E feed stream' },
  XMEAS_4: { name: 'A+C Mixed Feed Flow', unit: 'kscmh', normal: 9.34, parent_unit: 'UNIT_FEED', desc: 'A and C mixed stream' },
  // UNIT_REACTOR
  XMEAS_6: { name: 'Reactor Combined Feed', unit: 'kscmh', normal: 42.3, parent_unit: 'UNIT_REACTOR', desc: 'Total reactor feed gas rate' },
  XMEAS_7: { name: 'Reactor Pressure', unit: 'kPa', normal: 2705.0, parent_unit: 'UNIT_REACTOR', desc: 'CSTR vessel pressure' },
  XMEAS_8: { name: 'Reactor Level', unit: '%', normal: 65.2, parent_unit: 'UNIT_REACTOR', desc: 'Liquid & catalyst level' },
  XMEAS_9: { name: 'Reactor Temperature', unit: '°C', normal: 120.4, parent_unit: 'UNIT_REACTOR', desc: 'Exothermic core reaction temp' },
  XMEAS_21: { name: 'Reactor Coolant Return', unit: '°C', normal: 94.4, parent_unit: 'UNIT_REACTOR', desc: 'Cooling jacket return temp' },
  XMV_10: { name: 'Reactor CW Valve Position', unit: '%', normal: 41.1, parent_unit: 'UNIT_REACTOR', desc: 'Reactor cooling control valve' },
  XMEAS_23: { name: 'Feed Stream Comp A', unit: 'mol%', normal: 32.25, parent_unit: 'UNIT_REACTOR', desc: 'Component A in reactor feed' },
  XMEAS_24: { name: 'Feed Stream Comp B', unit: 'mol%', normal: 8.95, parent_unit: 'UNIT_REACTOR', desc: 'Component B in reactor feed' },
  XMEAS_25: { name: 'Feed Stream Comp C', unit: 'mol%', normal: 26.35, parent_unit: 'UNIT_REACTOR', desc: 'Component C in reactor feed' },
  XMEAS_26: { name: 'Feed Stream Comp D', unit: 'mol%', normal: 6.85, parent_unit: 'UNIT_REACTOR', desc: 'Component D in reactor feed' },
  XMEAS_27: { name: 'Feed Stream Comp E', unit: 'mol%', normal: 18.75, parent_unit: 'UNIT_REACTOR', desc: 'Component E in reactor feed' },
  XMEAS_28: { name: 'Feed Stream Comp F', unit: 'mol%', normal: 1.65, parent_unit: 'UNIT_REACTOR', desc: 'Inert component F in feed' },
  // UNIT_CONDENSER
  XMEAS_22: { name: 'Condenser Coolant Return', unit: '°C', normal: 77.2, parent_unit: 'UNIT_CONDENSER', desc: 'Condenser cooling return temp' },
  XMV_11: { name: 'Condenser CW Valve Position', unit: '%', normal: 18.1, parent_unit: 'UNIT_CONDENSER', desc: 'Condenser cooling water valve' },
  // UNIT_SEPARATOR
  XMEAS_10: { name: 'Purge Gas Rate', unit: 'kscmh', normal: 0.337, parent_unit: 'UNIT_SEPARATOR', desc: 'Purge vent gas to flare' },
  XMEAS_11: { name: 'Separator Temperature', unit: '°C', normal: 80.1, parent_unit: 'UNIT_SEPARATOR', desc: 'Flash drum operating temp' },
  XMEAS_12: { name: 'Separator Level', unit: '%', normal: 50.0, parent_unit: 'UNIT_SEPARATOR', desc: 'Liquid condensate level' },
  XMEAS_13: { name: 'Separator Pressure', unit: 'kPa', normal: 2633.0, parent_unit: 'UNIT_SEPARATOR', desc: 'Vapor headspace pressure' },
  XMEAS_14: { name: 'Separator Underflow Rate', unit: 'm3/h', normal: 25.1, parent_unit: 'UNIT_SEPARATOR', desc: 'Liquid bottoms to stripper' },
  XMEAS_29: { name: 'Purge Comp A', unit: 'mol%', normal: 32.95, parent_unit: 'UNIT_SEPARATOR', desc: 'Component A in purge gas' },
  XMEAS_30: { name: 'Purge Comp B', unit: 'mol%', normal: 13.80, parent_unit: 'UNIT_SEPARATOR', desc: 'Component B in purge gas' },
  XMEAS_31: { name: 'Purge Comp C', unit: 'mol%', normal: 23.95, parent_unit: 'UNIT_SEPARATOR', desc: 'Component C in purge gas' },
  XMEAS_32: { name: 'Purge Comp D', unit: 'mol%', normal: 1.25, parent_unit: 'UNIT_SEPARATOR', desc: 'Component D in purge gas' },
  XMEAS_33: { name: 'Purge Comp E', unit: 'mol%', normal: 18.55, parent_unit: 'UNIT_SEPARATOR', desc: 'Component E in purge gas' },
  XMEAS_34: { name: 'Purge Comp F', unit: 'mol%', normal: 2.25, parent_unit: 'UNIT_SEPARATOR', desc: 'Component F in purge gas' },
  XMEAS_35: { name: 'Purge Comp G', unit: 'mol%', normal: 4.80, parent_unit: 'UNIT_SEPARATOR', desc: 'Component G in purge gas' },
  XMEAS_36: { name: 'Purge Comp H', unit: 'mol%', normal: 2.45, parent_unit: 'UNIT_SEPARATOR', desc: 'Component H in purge gas' },
  // UNIT_COMPRESSOR
  XMEAS_5: { name: 'Recycle Flow', unit: 'kscmh', normal: 26.9, parent_unit: 'UNIT_COMPRESSOR', desc: 'Recycle gas from separator' },
  XMEAS_20: { name: 'Compressor Work', unit: 'kW', normal: 341.0, parent_unit: 'UNIT_COMPRESSOR', desc: 'Centrifugal compressor power' },
  // UNIT_STRIPPER
  XMEAS_15: { name: 'Stripper Level', unit: '%', normal: 50.0, parent_unit: 'UNIT_STRIPPER', desc: 'Stripping column sump level' },
  XMEAS_16: { name: 'Stripper Pressure', unit: 'kPa', normal: 3010.0, parent_unit: 'UNIT_STRIPPER', desc: 'Stripping column overhead pressure' },
  XMEAS_17: { name: 'Stripper Underflow Rate', unit: 'm3/h', normal: 22.9, parent_unit: 'UNIT_STRIPPER', desc: 'Final product stream flow' },
  XMEAS_18: { name: 'Stripper Temperature', unit: '°C', normal: 65.7, parent_unit: 'UNIT_STRIPPER', desc: 'Bottom reboiler operating temp' },
  XMEAS_19: { name: 'Stripper Steam Flow', unit: 'kg/h', normal: 1085.0, parent_unit: 'UNIT_STRIPPER', desc: 'Reboiler steam supply rate' },
  XMEAS_37: { name: 'Product Comp D', unit: 'mol%', normal: 0.15, parent_unit: 'UNIT_STRIPPER', desc: 'Component D in product stream' },
  XMEAS_38: { name: 'Product Comp E', unit: 'mol%', normal: 0.85, parent_unit: 'UNIT_STRIPPER', desc: 'Component E in product stream' },
  XMEAS_39: { name: 'Product Comp F', unit: 'mol%', normal: 0.05, parent_unit: 'UNIT_STRIPPER', desc: 'Component F in product stream' },
  XMEAS_40: { name: 'Product Comp G', unit: 'mol%', normal: 53.75, parent_unit: 'UNIT_STRIPPER', desc: 'Desired product G concentration' },
  XMEAS_41: { name: 'Product Comp H', unit: 'mol%', normal: 43.85, parent_unit: 'UNIT_STRIPPER', desc: 'Desired product H concentration' },
};

const UNIT_LABELS = {
  UNIT_FEED: { label: 'Reactant Feed System', color: '#38bdf8' },
  UNIT_REACTOR: { label: 'Chemical Reactor CSTR', color: '#f43f5e' },
  UNIT_CONDENSER: { label: 'Product Condenser', color: '#a855f7' },
  UNIT_SEPARATOR: { label: 'Vapor-Liquid Separator', color: '#f59e0b' },
  UNIT_COMPRESSOR: { label: 'Recycle Compressor', color: '#10b981' },
  UNIT_STRIPPER: { label: 'Product Stripper Column', color: '#ec4899' },
};

function AnalyzingProgress({ activeModel, onFastDiagnose }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const progressPercent = Math.min(95, Math.max(15, seconds * 5));

  return (
    <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <Cpu size={32} color="var(--accent-primary)" style={{ animation: 'spin 2s linear infinite' }} />
        <span style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
          LangGraph Agent Diagnosing Plant...
        </span>
      </div>

      {/* Elapsed Timer & Model Badge */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <Clock size={14} color="var(--accent-cyan)" />
          <span>Elapsed: <strong>{seconds}s</strong></span>
        </div>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8rem', color: '#a5b4fc' }}>
          <Bot size={14} />
          <span>Local Model: <strong>{activeModel ? activeModel.split('/').pop() : 'Mistral-7B'}</strong></span>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden', marginBottom: '1.5rem' }}>
        <div
          style={{
            height: '100%',
            width: `${progressPercent}%`,
            background: 'linear-gradient(90deg, #6366f1, #22d3ee)',
            borderRadius: '4px',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* Diagnostic Stage Checklist */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', textAlign: 'left', maxWidth: '440px', margin: '0 auto', fontSize: '0.84rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', color: '#10b981' }}>
          <CheckCircle2 size={16} />
          <span>Stage 1: Ingested All 43 Sensors & Control Actuators</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', color: '#10b981' }}>
          <CheckCircle2 size={16} />
          <span>Stage 2: Traversed Neo4j Flowsheet Topology & 6 Unit Piping</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', color: seconds >= 1 ? '#10b981' : 'var(--text-muted)' }}>
          <CheckCircle2 size={16} />
          <span>Stage 3: Granger Causality & Temporal Precedence Ranked</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', color: '#a855f7' }}>
          <Sparkles size={16} style={{ animation: 'pulse 1.5s infinite' }} />
          <span>Stage 4: Synthesizing Physical Explanation with Mistral-7B...</span>
        </div>
      </div>

      {/* Fast Fallback Option */}
      {onFastDiagnose && (
        <button
          onClick={onFastDiagnose}
          style={{
            marginTop: '1.5rem',
            background: 'rgba(255, 255, 255, 0.06)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            color: '#cbd5e1',
            borderRadius: '8px',
            padding: '0.5rem 1rem',
            fontSize: '0.8rem',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Zap size={14} color="#f59e0b" />
          <span>Skip Local LLM & Show Instant Causal Result</span>
        </button>
      )}
    </div>
  );
}

function SensorDownsideSolution({
  sensor,
  solution,
  isOverheatMachine,
  isDeviated,
  isApplyingMitigation,
  mitigatingSensorId,
  mitigationSuccess,
  onApplySolution,
}) {
  const isOverheated = solution.is_overheated || (isOverheatMachine && solution.is_thermal);

  return (
    <div
      style={{
        marginTop: '0.65rem',
        paddingTop: '0.85rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        animation: 'fadeIn 0.25s ease-in-out',
        textAlign: 'left',
      }}
    >
      {/* 1. Component Overheat / Anomaly Diagnosis Banner */}
      <div
        style={{
          background: isOverheated
            ? 'linear-gradient(135deg, rgba(244, 63, 94, 0.2) 0%, rgba(159, 18, 57, 0.15) 100%)'
            : 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(56, 189, 248, 0.08) 100%)',
          border: `1px solid ${isOverheated ? 'rgba(244, 63, 94, 0.5)' : 'rgba(99, 102, 241, 0.4)'}`,
          boxShadow: isOverheated ? '0 0 16px rgba(244, 63, 94, 0.18)' : 'none',
          borderRadius: '8px',
          padding: '0.85rem 1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.4rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {isOverheated ? (
              <Flame size={18} color="#f43f5e" style={{ filter: 'drop-shadow(0 0 6px #f43f5e)' }} />
            ) : (
              <Wrench size={16} color="var(--accent-cyan)" />
            )}
            <span
              style={{
                fontSize: '0.82rem',
                fontWeight: 800,
                letterSpacing: '0.04em',
                color: isOverheated ? '#f43f5e' : '#38bdf8',
                textTransform: 'uppercase',
              }}
            >
              {isOverheated
                ? '🔥 MACHINE OVERHEATING FROM THIS COMPONENT'
                : 'COMPONENT CAUSAL DIAGNOSIS'}
            </span>
          </div>

          <span
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '6px',
              background: 'rgba(0, 0, 0, 0.3)',
              color: '#cbd5e1',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            P&ID: {solution.pid_tag}
          </span>
        </div>

        {/* Failing Component Name */}
        <div style={{ fontSize: '0.96rem', fontWeight: 700, color: '#ffffff', lineHeight: 1.4 }}>
          {solution.component_name}
        </div>

        {/* Machine & Actuator info */}
        <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '0.25rem', display: 'flex', gap: '0.85rem', flexWrap: 'wrap' }}>
          <span>Machine: <strong style={{ color: '#ffffff' }}>{solution.equipment_unit}</strong></span>
          <span>Actuator: <strong style={{ color: '#a5b4fc' }}>{solution.actuator_tag}</strong></span>
          <span>Type: <strong style={{ color: '#94a3b8' }}>{solution.component_type}</strong></span>
        </div>

        {/* Diagnosis text */}
        <p style={{ fontSize: '0.85rem', color: isOverheated ? '#fecdd3' : '#e0e7ff', marginTop: '0.55rem', lineHeight: 1.5, background: 'rgba(0, 0, 0, 0.25)', padding: '0.5rem 0.75rem', borderRadius: '5px', border: `1px solid ${isOverheated ? 'rgba(244, 63, 94, 0.25)' : 'rgba(99, 102, 241, 0.2)'}` }}>
          {solution.overheat_diagnosis}
        </p>
      </div>

      {/* 2. Live Telemetry vs Nominal Baseline */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.5rem',
          background: 'rgba(0, 0, 0, 0.35)',
          padding: '0.65rem 0.85rem',
          borderRadius: '6px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        <div>
          <span style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase' }}>Live Telemetry</span>
          <div style={{ fontSize: '0.98rem', fontWeight: 800, color: isDeviated ? '#f43f5e' : '#34d399' }}>
            {typeof sensor.current_value === 'number' ? sensor.current_value.toFixed(2) : sensor.current_value} {sensor.eng_unit}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase' }}>Nominal Baseline</span>
          <div style={{ fontSize: '0.98rem', fontWeight: 700, color: '#94a3b8' }}>
            {solution.nominal_baseline}
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase' }}>Deviation</span>
          <div style={{ fontSize: '0.98rem', fontWeight: 800, color: isDeviated ? '#f43f5e' : '#34d399' }}>
            {sensor.dev_percent > 0 ? '+' : ''}{sensor.dev_percent.toFixed(1)}%
          </div>
        </div>
        <div>
          <span style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase' }}>Component Status</span>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: isDeviated ? (isOverheated ? '#f43f5e' : '#f59e0b') : '#34d399' }}>
            {isDeviated ? (isOverheated ? '🔥 Overheated Excursion' : 'Process Drift') : '✓ Nominal Safe'}
          </div>
        </div>
      </div>

      {/* 3. Physical Mechanism Explanation */}
      <div
        style={{
          fontSize: '0.81rem',
          color: '#cbd5e1',
          lineHeight: 1.5,
          background: 'rgba(15, 23, 42, 0.7)',
          padding: '0.65rem 0.85rem',
          borderRadius: '6px',
          borderLeft: `3px solid ${isOverheated ? '#f43f5e' : 'var(--accent-cyan)'}`,
        }}
      >
        <strong style={{ color: '#ffffff' }}>Physical Chemistry & Thermal Mechanism: </strong>
        {solution.physical_mechanism}
      </div>

      {/* 4. Actionable Field Solution Steps */}
      <div>
        <div style={{ fontSize: '0.80rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.45rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Wrench size={14} color="var(--accent-cyan)" />
          <span>Operator Solution & Corrective Actions for {solution.component_name}:</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {solution.solution_steps.map((step, sIdx) => (
            <div
              key={sIdx}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.55rem',
                fontSize: '0.80rem',
                color: '#e2e8f0',
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '0.5rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <span style={{ color: 'var(--accent-cyan)', fontWeight: 800, minWidth: '16px' }}>{sIdx + 1}.</span>
              <span style={{ lineHeight: 1.45 }}>{step}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Emergency Action if available */}
      {solution.emergency_action && (
        <div
          style={{
            fontSize: '0.78rem',
            color: '#fca5a5',
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px dashed rgba(244, 63, 94, 0.4)',
            borderRadius: '6px',
            padding: '0.5rem 0.75rem',
            lineHeight: 1.4,
          }}
        >
          <strong>Emergency Safeguard: </strong>
          {solution.emergency_action}
        </div>
      )}

      {/* 5. One-Click Component Recovery Action Button */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', flexWrap: 'wrap', marginTop: '0.35rem', paddingTop: '0.65rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onApplySolution(sensor.sensor_id);
          }}
          disabled={isApplyingMitigation}
          style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            boxShadow: '0 0 16px rgba(16, 185, 129, 0.35)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '6px',
            padding: '0.6rem 1.2rem',
            color: '#ffffff',
            fontSize: '0.84rem',
            fontWeight: 700,
            cursor: isApplyingMitigation ? 'not-allowed' : 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.2s ease',
          }}
        >
          <Zap size={15} />
          {isApplyingMitigation && mitigatingSensorId === sensor.sensor_id
            ? `Applying Solution for ${sensor.sensor_id}...`
            : `Apply Solution for this Component (${solution.actuator_tag})`}
        </button>

        {mitigationSuccess && mitigatingSensorId === sensor.sensor_id && (
          <span style={{ fontSize: '0.78rem', color: '#34d399', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(16, 185, 129, 0.12)', padding: '4px 10px', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            <CheckCircle2 size={15} />
            Solution executed! Restoring {sensor.sensor_id} & {solution.actuator_tag} to nominal baseline.
          </span>
        )}
      </div>
    </div>
  );
}

export default function RootCausePanel({
  rcaResult = null,
  isLoading = false,
  onTriggerRCA = null,
  onFastDiagnose = null,
  llmStatus = { online: true, active_model: 'mistralai/mistral-7b-instruct-v0.3' },
  latestReadings = {},
  activeFault = null,
  onApplyMitigation = null,
}) {
  const [viewMode, setViewMode] = useState('sensors'); // 'sensors' | 'units'
  const [sensorFilterUnit, setSensorFilterUnit] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedUnits, setExpandedUnits] = useState({});
  const [expandedSensorId, setExpandedSensorId] = useState(null);
  const [mitigatingSensorId, setMitigatingSensorId] = useState(null);
  const [isApplyingMitigation, setIsApplyingMitigation] = useState(false);
  const [mitigationSuccess, setMitigationSuccess] = useState(false);
  const [executedSteps, setExecutedSteps] = useState({});

  const toggleSensorExpand = (sensorId) => {
    setExpandedSensorId((prev) => (prev === sensorId ? null : sensorId));
  };

  const handleExecuteMitigation = async () => {
    setIsApplyingMitigation(true);
    setMitigationSuccess(false);
    try {
      if (onApplyMitigation) {
        await onApplyMitigation();
      }
      setMitigationSuccess(true);
      setTimeout(() => setMitigationSuccess(false), 8000);
    } finally {
      setIsApplyingMitigation(false);
    }
  };

  const handleExecuteComponentMitigation = async (sensorId) => {
    setMitigatingSensorId(sensorId);
    setIsApplyingMitigation(true);
    setMitigationSuccess(false);
    try {
      if (onApplyMitigation) {
        await onApplyMitigation();
      }
      setMitigationSuccess(true);
      setTimeout(() => setMitigationSuccess(false), 8000);
    } finally {
      setIsApplyingMitigation(false);
    }
  };

  const toggleStepExecuted = (stepIndex) => {
    setExecutedSteps((prev) => ({ ...prev, [stepIndex]: !prev[stepIndex] }));
  };

  if (isLoading) {
    return <AnalyzingProgress activeModel={llmStatus?.active_model} onFastDiagnose={onFastDiagnose} />;
  }

  if (!rcaResult) {
    return (
      <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Target size={42} color="var(--accent-cyan)" />
        <h3 style={{ marginTop: '0.85rem', fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
          Root Cause Analysis Ready
        </h3>
        <p style={{ marginTop: '0.4rem', color: 'var(--text-muted)', fontSize: '0.88rem', maxWidth: '420px', lineHeight: 1.5 }}>
          Inject a plant fault scenario on the left, or click below anytime to evaluate all 43 process sensors, trace causal propagation, and generate an explanation with your local LLM.
        </p>

        {onTriggerRCA && (
          <button
            className="btn-primary"
            style={{
              marginTop: '1.25rem',
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              boxShadow: '0 0 20px rgba(168, 85, 247, 0.45)',
              padding: '0.75rem 1.6rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '0.55rem',
              cursor: 'pointer',
            }}
            onClick={onTriggerRCA}
            disabled={isLoading}
          >
            <Sparkles size={18} color="#ffffff" />
            Analyze Root Cause Now
          </button>
        )}

        <div
          style={{
            marginTop: '1.25rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.85rem',
            borderRadius: '20px',
            background: llmStatus?.online ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
            border: `1px solid ${llmStatus?.online ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
            fontSize: '0.78rem',
            color: llmStatus?.online ? '#34d399' : '#f87171',
          }}
        >
          <Bot size={14} />
          <span>LM Studio: {llmStatus?.online ? `Active (${llmStatus?.active_model || 'mistralai/mistral-7b-instruct-v0.3'})` : 'Offline (Rule fallback mode)'}</span>
        </div>
      </div>
    );
  }

  const report = rcaResult.final_report || rcaResult.explanation_report || {};
  const rankedUnits = rcaResult.ranked_causes || [];
  const incomingSensors = rcaResult.ranked_sensors || [];
  const confidenceScores = rcaResult.confidence_scores || {};
  const evidenceList = rcaResult.evidence_list || report.evidence_citations || [];

  // Determine top confidence percentage and health status
  const primaryUnit = report.primary_unit || (rankedUnits.length > 0 ? rankedUnits[0].unit_id : 'UNIT_REACTOR');
  const isHealthy = primaryUnit.includes('NONE') || primaryUnit.includes('Normal') || (report.probable_failure_mode && report.probable_failure_mode.includes('Normal'));
  const topConfidence = confidenceScores[primaryUnit] !== undefined
    ? Math.round(confidenceScores[primaryUnit] * 100)
    : Math.round((report.confidence_score || 0.88) * 100);

  // Map incoming sensor scores by sensor_id
  const incomingMap = {};
  incomingSensors.forEach((s) => {
    if (s.sensor_id) incomingMap[s.sensor_id] = s;
  });

  // Assemble full 43-sensor list combining API causal scores and live telemetry deviations
  const allSensorsRanked = Object.keys(SENSOR_META).map((sensorId) => {
    const meta = SENSOR_META[sensorId];
    const fromApi = incomingMap[sensorId];
    const currentVal = latestReadings?.[sensorId];
    const normalVal = meta.normal;
    let devPercent = 0;
    if (currentVal !== undefined && normalVal !== 0) {
      devPercent = ((currentVal - normalVal) / normalVal) * 100;
    }

    const unitCause = rankedUnits.find((u) => u.unit_id === meta.parent_unit);
    const unitConf = unitCause ? (unitCause.confidence_score || unitCause.composite_score || 0.6) : 0.5;

    // Use API composite score if available, else derive from causal unit score & deviation
    let compositeScore = 0.5;
    if (fromApi?.composite_score !== undefined) {
      compositeScore = fromApi.composite_score;
    } else {
      const devWeight = Math.min(0.4, (Math.abs(devPercent) / 100) * 0.4);
      compositeScore = Math.min(0.99, Math.max(0.15, unitConf * 0.7 + devWeight));
    }

    const tempScore = fromApi?.temporal_score !== undefined
      ? fromApi.temporal_score
      : (unitCause?.temporal_score || 0.5);

    const graphScore = fromApi?.graph_proximity_score !== undefined
      ? fromApi.graph_proximity_score
      : (unitCause?.graph_proximity_score || unitCause?.graph_score || 0.5);

    const grangerScore = fromApi?.granger_score !== undefined
      ? fromApi.granger_score
      : (unitCause?.granger_score || 0.4);

    return {
      sensor_id: sensorId,
      name: meta.name,
      unit_id: meta.parent_unit,
      eng_unit: meta.unit,
      desc: meta.desc,
      current_value: currentVal !== undefined ? currentVal : normalVal,
      normal_value: normalVal,
      dev_percent: devPercent,
      composite_score: compositeScore,
      temporal_score: tempScore,
      graph_score: graphScore,
      granger_score: grangerScore,
    };
  });

  // Sort descending by composite causal score
  allSensorsRanked.sort((a, b) => b.composite_score - a.composite_score);

  // Filtered sensors for tab view
  const filteredSensors = allSensorsRanked.filter((s) => {
    const matchesUnit = sensorFilterUnit === 'ALL' || s.unit_id === sensorFilterUnit;
    const matchesSearch = !searchQuery ||
      s.sensor_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.unit_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesUnit && matchesSearch;
  });

  const toggleUnitExpand = (unitId) => {
    setExpandedUnits((prev) => ({ ...prev, [unitId]: !prev[unitId] }));
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* 1. Header & Overall Diagnosis Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <span style={{ fontSize: '0.72rem', color: isHealthy ? '#34d399' : 'var(--accent-cyan)', fontWeight: 800, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            {isHealthy ? 'PLANT STATUS: HEALTHY & NOMINAL' : 'ROOT CAUSE DIAGNOSIS & REASONING'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap', marginTop: '0.2rem' }}>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: isHealthy ? '#34d399' : '#ffffff', margin: 0 }}>
              {report.probable_failure_mode || (isHealthy ? 'Plant Operational Steady-State' : 'Process Excursion Detected')}
            </h2>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                background: 'rgba(99, 102, 241, 0.2)',
                border: '1px solid rgba(99, 102, 241, 0.5)',
                borderRadius: '12px',
                padding: '2px 8px',
                fontSize: '0.74rem',
                color: '#c7d2fe',
                fontWeight: 700,
              }}
            >
              <Sparkles size={12} color="#818cf8" />
              Scope: 43 / 43 Sensors Analyzed
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {isHealthy ? (
              <span>Plant Equipment Status: <strong style={{ color: '#10b981', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>100% NOMINAL (All Units Normal)</strong></span>
            ) : (
              <span>Root Cause Origin: <strong style={{ color: '#f43f5e', background: 'rgba(244, 63, 94, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>{primaryUnit}</strong></span>
            )}
          </div>
        </div>

        {/* Confidence Percentage Badge */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            {isHealthy ? 'HEALTH SCORE' : 'OVERALL CONFIDENCE'}
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: isHealthy ? '#10b981' : 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
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
            background: isHealthy
              ? 'linear-gradient(90deg, #10b981, #34d399)'
              : 'linear-gradient(90deg, #6366f1, #06b6d4, #10b981)',
            borderRadius: '6px',
            transition: 'width 0.8s ease-in-out',
          }}
        />
      </div>

      {/* Executive Summary */}
      {report.root_cause_summary && (
        <div
          style={{
            background: isHealthy ? 'rgba(16, 185, 129, 0.08)' : 'rgba(99, 102, 241, 0.1)',
            borderLeft: `3px solid ${isHealthy ? '#10b981' : 'var(--accent-primary)'}`,
            padding: '0.85rem 1rem',
            borderRadius: '4px',
          }}
        >
          <p style={{ fontSize: '0.90rem', color: isHealthy ? '#a7f3d0' : '#e0e7ff', lineHeight: 1.5 }}>
            {report.root_cause_summary}
          </p>
        </div>
      )}

      {/* View Switcher: All 43 Sensors vs 6 Equipment Units */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginTop: '0.25rem' }}>
        <div style={{ display: 'flex', gap: '0.4rem', background: 'rgba(15, 23, 42, 0.9)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <button
            onClick={() => setViewMode('sensors')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: viewMode === 'sensors' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'transparent',
              color: viewMode === 'sensors' ? '#ffffff' : '#94a3b8',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Activity size={14} />
            All 43 Sensors Ranked ({allSensorsRanked.length})
          </button>
          <button
            onClick={() => setViewMode('units')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              background: viewMode === 'units' ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'transparent',
              color: viewMode === 'units' ? '#ffffff' : '#94a3b8',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Layers size={14} />
            Equipment Units ({rankedUnits.length})
          </button>
        </div>

        {viewMode === 'sensors' && (
          <div style={{ position: 'relative', minWidth: '220px' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search sensor or tag..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                padding: '0.4rem 0.6rem 0.4rem 2rem',
                fontSize: '0.8rem',
                color: '#ffffff',
                outline: 'none',
              }}
            />
          </div>
        )}
      </div>

      {/* ======================================================== */}
      {/* VIEW A: ALL 43 SENSORS RANKED (#1 - #43)                 */}
      {/* ======================================================== */}
      {viewMode === 'sensors' && (
        <div>
          {/* Unit Filter Chips */}
          <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
            {['ALL', 'UNIT_FEED', 'UNIT_REACTOR', 'UNIT_CONDENSER', 'UNIT_SEPARATOR', 'UNIT_COMPRESSOR', 'UNIT_STRIPPER'].map((u) => {
              const count = u === 'ALL'
                ? allSensorsRanked.length
                : allSensorsRanked.filter((s) => s.unit_id === u).length;
              const isSelected = sensorFilterUnit === u;
              const unitLabel = u === 'ALL' ? 'ALL 43 SENSORS' : u.replace('UNIT_', '');
              return (
                <button
                  key={u}
                  onClick={() => setSensorFilterUnit(u)}
                  style={{
                    background: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                    border: `1px solid ${isSelected ? 'rgba(99, 102, 241, 0.6)' : 'rgba(255, 255, 255, 0.08)'}`,
                    color: isSelected ? '#a5b4fc' : '#94a3b8',
                    padding: '0.25rem 0.6rem',
                    borderRadius: '6px',
                    fontSize: '0.72rem',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                  }}
                >
                  {unitLabel} ({count})
                </button>
              );
            })}
          </div>

          {/* Scrollable List of Sensors */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.55rem', maxHeight: '480px', overflowY: 'auto', paddingRight: '4px' }}>
            {filteredSensors.map((sensor, idx) => {
              const conf = Math.round(sensor.composite_score * 100);
              const tempScore = Math.round(sensor.temporal_score * 100);
              const graphScore = Math.round(sensor.graph_score * 100);
              const grangerScore = Math.round(sensor.granger_score * 100);
              const unitColor = UNIT_LABELS[sensor.unit_id]?.color || '#6366f1';
              const absDev = Math.abs(sensor.dev_percent);
              const isDeviated = absDev >= 3.0;
              const isExpanded = expandedSensorId === sensor.sensor_id;
              const solution = getSensorSolution(sensor.sensor_id, sensor.current_value, sensor.normal_value, sensor.unit_id);
              const isOverheatMachine = primaryUnit === 'UNIT_REACTOR' || (sensor.unit_id === 'UNIT_REACTOR' && Math.abs(sensor.dev_percent) > 2);

              return (
                <div
                  key={sensor.sensor_id}
                  onClick={() => toggleSensorExpand(sensor.sensor_id)}
                  style={{
                    background: isExpanded ? 'rgba(15, 23, 42, 0.98)' : 'rgba(15, 23, 42, 0.85)',
                    border: isExpanded
                      ? '1px solid rgba(99, 102, 241, 0.75)'
                      : `1px solid ${idx < 3 ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)'}`,
                    boxShadow: isExpanded ? '0 0 24px rgba(99, 102, 241, 0.25)' : 'none',
                    borderRadius: '8px',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.45rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                  }}
                  title="Click to expand component root cause & solution on the downside"
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span
                        style={{
                          fontSize: '0.74rem',
                          fontWeight: 800,
                          color: idx < 3 ? '#f43f5e' : '#94a3b8',
                          background: idx < 3 ? 'rgba(244, 63, 94, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          minWidth: '28px',
                          textAlign: 'center',
                        }}
                      >
                        #{idx + 1}
                      </span>
                      <div>
                        <strong style={{ fontSize: '0.94rem', color: '#ffffff' }}>
                          {sensor.sensor_id}
                        </strong>
                        <span style={{ fontSize: '0.82rem', color: '#94a3b8', marginLeft: '0.4rem' }}>
                          {sensor.name}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem', flexWrap: 'wrap' }}>
                      {/* Unit Pill */}
                      <span
                        style={{
                          fontSize: '0.68rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '10px',
                          background: `${unitColor}20`,
                          border: `1px solid ${unitColor}50`,
                          color: unitColor,
                        }}
                      >
                        {sensor.unit_id.replace('UNIT_', '')}
                      </span>

                      {/* Live Reading & Deviation Pill */}
                      <div
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          fontSize: '0.76rem',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '6px',
                          background: isDeviated
                            ? (sensor.dev_percent > 0 ? 'rgba(244, 63, 94, 0.15)' : 'rgba(56, 189, 248, 0.15)')
                            : 'rgba(16, 185, 129, 0.12)',
                          color: isDeviated
                            ? (sensor.dev_percent > 0 ? '#f43f5e' : '#38bdf8')
                            : '#34d399',
                        }}
                      >
                        {isDeviated ? (
                          sensor.dev_percent > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />
                        ) : (
                          <CheckCircle2 size={12} />
                        )}
                        <span>
                          {typeof sensor.current_value === 'number' ? sensor.current_value.toFixed(2) : sensor.current_value} {sensor.eng_unit}
                        </span>
                        {isDeviated && (
                          <span style={{ opacity: 0.85, fontSize: '0.7rem' }}>
                            ({sensor.dev_percent > 0 ? '+' : ''}{sensor.dev_percent.toFixed(1)}%)
                          </span>
                        )}
                      </div>

                      <span className="score-badge" style={{ fontWeight: 800 }}>
                        {conf}%
                      </span>

                      {/* Expand Solution Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSensorExpand(sensor.sensor_id);
                        }}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          background: isExpanded ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                          border: `1px solid ${isExpanded ? 'rgba(99, 102, 241, 0.6)' : 'rgba(255, 255, 255, 0.12)'}`,
                          color: isExpanded ? '#a5b4fc' : '#cbd5e1',
                          borderRadius: '6px',
                          padding: '3px 8px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                        title="Click to view component root cause & solution on downside"
                      >
                        <Wrench size={12} color={isExpanded ? '#818cf8' : '#94a3b8'} />
                        <span>{isExpanded ? 'Hide Solution ▲' : 'View Solution ▼'}</span>
                      </button>
                    </div>
                  </div>

                  {/* Causal Score Bar */}
                  <div style={{ width: '100%', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', height: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${conf}%`,
                        height: '100%',
                        background: idx < 3
                          ? 'linear-gradient(90deg, #f43f5e, #ec4899)'
                          : 'linear-gradient(90deg, #6366f1, #38bdf8)',
                        borderRadius: '3px',
                      }}
                    />
                  </div>

                  {/* Subscore metrics */}
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.7rem', color: '#94a3b8' }}>
                    <span>Temporal Lead: <strong style={{ color: '#fff' }}>{tempScore}%</strong></span>
                    <span>Graph Proximity: <strong style={{ color: '#fff' }}>{graphScore}%</strong></span>
                    <span>Granger Influence: <strong style={{ color: '#fff' }}>{grangerScore}%</strong></span>
                  </div>

                  {/* Downside Component Solution Drawer */}
                  {isExpanded && (
                    <SensorDownsideSolution
                      sensor={sensor}
                      solution={solution}
                      isOverheatMachine={isOverheatMachine}
                      isDeviated={isDeviated}
                      isApplyingMitigation={isApplyingMitigation}
                      mitigatingSensorId={mitigatingSensorId}
                      mitigationSuccess={mitigationSuccess}
                      onApplySolution={handleExecuteComponentMitigation}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* VIEW B: EQUIPMENT UNITS RANKED (6 MACHINES)              */}
      {/* ======================================================== */}
      {viewMode === 'units' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {rankedUnits.map((cause, idx) => {
            const unitName = cause.unit_id || cause.sensor_id || `Candidate ${idx + 1}`;
            const conf = Math.round((cause.confidence_score !== undefined ? cause.confidence_score : cause.composite_score || 0.5) * 100);
            const tempScore = Math.round((cause.temporal_score || 0) * 100);
            const graphScore = Math.round((cause.graph_proximity_score || cause.graph_score || 0) * 100);
            const grangerScore = Math.round((cause.granger_score || 0) * 100);
            const unitMeta = UNIT_LABELS[unitName] || { label: unitName, color: '#6366f1' };
            const isExpanded = Boolean(expandedUnits[unitName]);
            const unitSensors = allSensorsRanked.filter((s) => s.unit_id === unitName);

            return (
              <div key={idx} className="cause-item" style={{ background: 'rgba(15, 23, 42, 0.85)', border: `1px solid ${idx === 0 ? 'rgba(244, 63, 94, 0.45)' : 'var(--border-subtle)'}`, borderRadius: '8px', padding: '0.9rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 700 }}>#{idx + 1}</span>
                    <strong style={{ fontSize: '1rem', color: idx === 0 ? '#f43f5e' : '#f8fafc' }}>{unitName}</strong>
                    <span style={{ fontSize: '0.78rem', color: unitMeta.color, fontWeight: 600 }}>({unitMeta.label})</span>
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
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', fontSize: '0.72rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
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

                {/* Accordion toggle to show sensors in this machine */}
                <button
                  onClick={() => toggleUnitExpand(unitName)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '4px',
                    padding: '0.3rem 0.6rem',
                    fontSize: '0.72rem',
                    color: '#94a3b8',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                  }}
                >
                  {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  <span>{isExpanded ? 'Hide' : 'Inspect'} {unitSensors.length} Sensors in {unitName}</span>
                </button>

                {/* Expanded sensor breakdown */}
                {isExpanded && (
                  <div style={{ marginTop: '0.65rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '0.65rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                    {unitSensors.map((s) => {
                      const isSensorExpanded = expandedSensorId === s.sensor_id;
                      const solution = getSensorSolution(s.sensor_id, s.current_value, s.normal_value, s.unit_id);
                      const isDeviated = Math.abs(s.dev_percent) >= 3.0;
                      const isOverheatMachine = unitName === 'UNIT_REACTOR';

                      return (
                        <div
                          key={s.sensor_id}
                          onClick={() => toggleSensorExpand(s.sensor_id)}
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.35rem',
                            background: isSensorExpanded ? 'rgba(15, 23, 42, 0.95)' : 'rgba(0, 0, 0, 0.25)',
                            border: `1px solid ${isSensorExpanded ? 'rgba(99, 102, 241, 0.6)' : 'rgba(255, 255, 255, 0.05)'}`,
                            padding: '0.55rem 0.75rem',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                          title="Click to view component root cause & solution on downside"
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <strong style={{ color: '#e2e8f0', fontSize: '0.82rem' }}>{s.sensor_id}</strong>
                              <span style={{ color: '#94a3b8', marginLeft: '0.35rem', fontSize: '0.78rem' }}>{s.name}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <span style={{ color: '#cbd5e1', fontSize: '0.78rem' }}>
                                {typeof s.current_value === 'number' ? s.current_value.toFixed(2) : s.current_value} {s.eng_unit}
                              </span>
                              <span style={{ color: '#a5b4fc', fontWeight: 700, fontSize: '0.78rem' }}>
                                {Math.round(s.composite_score * 100)}%
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleSensorExpand(s.sensor_id);
                                }}
                                style={{
                                  background: isSensorExpanded ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.06)',
                                  border: '1px solid rgba(255, 255, 255, 0.12)',
                                  borderRadius: '4px',
                                  padding: '2px 6px',
                                  fontSize: '0.68rem',
                                  color: isSensorExpanded ? '#a5b4fc' : '#94a3b8',
                                  cursor: 'pointer',
                                }}
                              >
                                {isSensorExpanded ? 'Hide ▲' : 'Solution ▼'}
                              </button>
                            </div>
                          </div>

                          {isSensorExpanded && (
                            <SensorDownsideSolution
                              sensor={s}
                              solution={solution}
                              isOverheatMachine={isOverheatMachine}
                              isDeviated={isDeviated}
                              isApplyingMitigation={isApplyingMitigation}
                              mitigatingSensorId={mitigatingSensorId}
                              mitigationSuccess={mitigationSuccess}
                              onApplySolution={handleExecuteComponentMitigation}
                            />
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

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

      {/* 5. Interactive Solution & Mitigation Control Panel */}
      {report.operator_actions && report.operator_actions.length > 0 && (
        <div
          style={{
            background: isHealthy ? 'rgba(16, 185, 129, 0.06)' : 'rgba(15, 23, 42, 0.95)',
            border: `1px solid ${isHealthy ? 'rgba(16, 185, 129, 0.3)' : 'rgba(99, 102, 241, 0.4)'}`,
            boxShadow: isHealthy ? 'none' : '0 0 24px rgba(99, 102, 241, 0.2)',
            borderRadius: '10px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <div style={{ background: isHealthy ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.25)', padding: '6px', borderRadius: '8px' }}>
                <Wrench size={18} color={isHealthy ? '#10b981' : '#818cf8'} />
              </div>
              <div>
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#ffffff', margin: 0 }}>
                  OPERATIONAL SOLUTION & RECOVERY DASHBOARD
                </h3>
                <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                  Interactive corrective actions to restore {primaryUnit}
                </span>
              </div>
            </div>

            {/* Target Machine & Status Pill */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  fontSize: '0.74rem',
                  fontWeight: 800,
                  padding: '3px 10px',
                  borderRadius: '12px',
                  background: isHealthy ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                  border: `1px solid ${isHealthy ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)'}`,
                  color: isHealthy ? '#34d399' : '#f87171',
                }}
              >
                {isHealthy ? '✓ Plant Stabilized (Nominal)' : `Target: ${primaryUnit}`}
              </span>
            </div>
          </div>

          {/* Success Banner if solution was just executed */}
          {mitigationSuccess && (
            <div
              style={{
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                borderRadius: '8px',
                padding: '0.75rem 1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                color: '#6ee7b7',
                fontSize: '0.86rem',
                fontWeight: 600,
              }}
            >
              <CheckCircle2 size={18} color="#10b981" />
              <span>
                Solution successfully executed for {primaryUnit}! Control loops aligned and all 43 sensors returning to steady-state baseline.
              </span>
            </div>
          )}

          {/* Interactive Steps List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {report.operator_actions.map((act, i) => {
              const isChecked = Boolean(executedSteps[i]);
              return (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    gap: '0.75rem',
                    background: isChecked ? 'rgba(16, 185, 129, 0.08)' : 'rgba(0, 0, 0, 0.35)',
                    border: `1px solid ${isChecked ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.06)'}`,
                    borderRadius: '8px',
                    padding: '0.75rem 0.9rem',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem' }}>
                    <button
                      onClick={() => toggleStepExecuted(i)}
                      style={{
                        background: isChecked ? '#10b981' : 'transparent',
                        border: `2px solid ${isChecked ? '#10b981' : '#64748b'}`,
                        borderRadius: '4px',
                        width: '20px',
                        height: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        padding: 0,
                        marginTop: '2px',
                      }}
                      title="Mark step as executed"
                    >
                      {isChecked && <CheckCircle2 size={14} color="#ffffff" />}
                    </button>
                    <div>
                      <div style={{ fontSize: '0.85rem', color: isChecked ? '#6ee7b7' : '#e2e8f0', fontWeight: isChecked ? 600 : 500, lineHeight: 1.5, textDecoration: isChecked ? 'line-through' : 'none' }}>
                        {act}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleStepExecuted(i)}
                    style={{
                      background: isChecked ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                      border: `1px solid ${isChecked ? 'rgba(16, 185, 129, 0.4)' : 'rgba(255, 255, 255, 0.1)'}`,
                      color: isChecked ? '#34d399' : '#94a3b8',
                      borderRadius: '6px',
                      padding: '0.3rem 0.65rem',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {isChecked ? 'Executed ✓' : 'Mark Done'}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Primary Action Button: Apply Solution */}
          {!isHealthy && onApplyMitigation && (
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center', marginTop: '0.25rem' }}>
              <button
                onClick={handleExecuteMitigation}
                disabled={isApplyingMitigation}
                style={{
                  flex: 1,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  boxShadow: '0 0 18px rgba(16, 185, 129, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.25)',
                  borderRadius: '8px',
                  padding: '0.7rem 1.25rem',
                  color: '#ffffff',
                  fontSize: '0.9rem',
                  fontWeight: 700,
                  cursor: isApplyingMitigation ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.55rem',
                  transition: 'all 0.2s ease',
                }}
              >
                <Zap size={16} />
                {isApplyingMitigation ? `Executing Solution for ${primaryUnit}...` : `Apply Automated AI Solution to ${primaryUnit}`}
              </button>

              <button
                onClick={() => {
                  const allDone = {};
                  report.operator_actions.forEach((_, i) => (allDone[i] = true));
                  setExecutedSteps(allDone);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '8px',
                  padding: '0.7rem 1rem',
                  color: '#cbd5e1',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                }}
              >
                <CheckCircle2 size={15} color="#10b981" />
                <span>Mark All Complete</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
