import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Layers,
  Search,
  CheckCircle2,
  Cpu,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';

// Complete dictionary of all 41 TEP process measurement sensors + primary actuator valves
const SENSOR_META = {
  // ==========================================
  // UNIT_FEED (Reactant Feed Header System)
  // ==========================================
  XMEAS_1: { name: 'A Feed Flow', unit: 'kscmh', normal: 0.25, parent_unit: 'UNIT_FEED', min: 0.0, max: 0.5, desc: 'Stream A volumetric flow' },
  XMEAS_2: { name: 'D Feed Flow', unit: 'kg/h', normal: 3664.0, parent_unit: 'UNIT_FEED', min: 3200, max: 4200, desc: 'Stream D mass flow' },
  XMEAS_3: { name: 'E Feed Flow', unit: 'kg/h', normal: 4505.0, parent_unit: 'UNIT_FEED', min: 4000, max: 5000, desc: 'Stream E mass flow' },
  XMEAS_4: { name: 'A+C Mixed Feed Flow', unit: 'kscmh', normal: 9.34, parent_unit: 'UNIT_FEED', min: 7.5, max: 11.5, desc: 'A and C mixed stream flow' },

  // ==========================================
  // UNIT_REACTOR (Chemical Reactor CSTR)
  // ==========================================
  XMEAS_6: { name: 'Reactor Combined Feed', unit: 'kscmh', normal: 42.3, parent_unit: 'UNIT_REACTOR', min: 35.0, max: 50.0, desc: 'Total reactor feed gas flow' },
  XMEAS_7: { name: 'Reactor Pressure', unit: 'kPa', normal: 2705.0, parent_unit: 'UNIT_REACTOR', min: 2500, max: 2950, desc: 'CSTR operating pressure' },
  XMEAS_8: { name: 'Reactor Level', unit: '%', normal: 65.2, parent_unit: 'UNIT_REACTOR', min: 50.0, max: 80.0, desc: 'Liquid & catalyst inventory level' },
  XMEAS_9: { name: 'Reactor Temperature', unit: '°C', normal: 120.4, parent_unit: 'UNIT_REACTOR', min: 110, max: 140, desc: 'Core reaction temperature' },
  XMEAS_21: { name: 'Reactor Coolant Return', unit: '°C', normal: 94.4, parent_unit: 'UNIT_REACTOR', min: 82, max: 115, desc: 'Cooling jacket effluent temperature' },
  XMV_10: { name: 'Cooling Valve Position', unit: '%', normal: 41.1, parent_unit: 'UNIT_REACTOR', min: 20, max: 100, desc: 'Reactor cooling control valve' },
  // Stream 6: Reactor Feed Stream Compositions (mol%)
  XMEAS_23: { name: 'Feed Comp A', unit: 'mol%', normal: 32.25, parent_unit: 'UNIT_REACTOR', min: 25.0, max: 40.0, desc: 'Component A in reactor feed' },
  XMEAS_24: { name: 'Feed Comp B', unit: 'mol%', normal: 8.95, parent_unit: 'UNIT_REACTOR', min: 5.0, max: 13.0, desc: 'Component B in reactor feed' },
  XMEAS_25: { name: 'Feed Comp C', unit: 'mol%', normal: 26.35, parent_unit: 'UNIT_REACTOR', min: 20.0, max: 32.0, desc: 'Component C in reactor feed' },
  XMEAS_26: { name: 'Feed Comp D', unit: 'mol%', normal: 6.85, parent_unit: 'UNIT_REACTOR', min: 4.0, max: 10.0, desc: 'Component D in reactor feed' },
  XMEAS_27: { name: 'Feed Comp E', unit: 'mol%', normal: 18.75, parent_unit: 'UNIT_REACTOR', min: 14.0, max: 24.0, desc: 'Component E in reactor feed' },
  XMEAS_28: { name: 'Feed Comp F', unit: 'mol%', normal: 1.65, parent_unit: 'UNIT_REACTOR', min: 0.8, max: 3.0, desc: 'Inert component F in feed' },

  // ==========================================
  // UNIT_CONDENSER (Product Heat Exchanger)
  // ==========================================
  XMEAS_22: { name: 'Condenser Coolant Return', unit: '°C', normal: 77.2, parent_unit: 'UNIT_CONDENSER', min: 65, max: 95, desc: 'Condenser coolant return temp' },
  XMV_11: { name: 'Condenser Valve Position', unit: '%', normal: 18.1, parent_unit: 'UNIT_CONDENSER', min: 5, max: 50, desc: 'Condenser cooling water valve' },

  // ==========================================
  // UNIT_SEPARATOR (Flash Separator Vessel)
  // ==========================================
  XMEAS_10: { name: 'Purge Gas Rate', unit: 'kscmh', normal: 0.337, parent_unit: 'UNIT_SEPARATOR', min: 0.2, max: 0.5, desc: 'Purge vent gas to flare' },
  XMEAS_11: { name: 'Separator Temperature', unit: '°C', normal: 80.1, parent_unit: 'UNIT_SEPARATOR', min: 70, max: 95, desc: 'Flash vessel operating temp' },
  XMEAS_12: { name: 'Separator Level', unit: '%', normal: 50.0, parent_unit: 'UNIT_SEPARATOR', min: 35, max: 65, desc: 'Liquid condensate level' },
  XMEAS_13: { name: 'Separator Pressure', unit: 'kPa', normal: 2633.0, parent_unit: 'UNIT_SEPARATOR', min: 2450, max: 2850, desc: 'Headspace vapor pressure' },
  XMEAS_14: { name: 'Separator Underflow Rate', unit: 'm3/h', normal: 25.1, parent_unit: 'UNIT_SEPARATOR', min: 18.0, max: 32.0, desc: 'Condensed liquid to stripper' },
  // Stream 9: Purge Gas Compositions (mol%)
  XMEAS_29: { name: 'Purge Comp A', unit: 'mol%', normal: 32.95, parent_unit: 'UNIT_SEPARATOR', min: 26.0, max: 40.0, desc: 'Component A in purge gas' },
  XMEAS_30: { name: 'Purge Comp B', unit: 'mol%', normal: 13.80, parent_unit: 'UNIT_SEPARATOR', min: 9.0, max: 18.0, desc: 'Component B in purge gas' },
  XMEAS_31: { name: 'Purge Comp C', unit: 'mol%', normal: 23.95, parent_unit: 'UNIT_SEPARATOR', min: 18.0, max: 30.0, desc: 'Component C in purge gas' },
  XMEAS_32: { name: 'Purge Comp D', unit: 'mol%', normal: 1.25, parent_unit: 'UNIT_SEPARATOR', min: 0.5, max: 2.5, desc: 'Component D in purge gas' },
  XMEAS_33: { name: 'Purge Comp E', unit: 'mol%', normal: 18.55, parent_unit: 'UNIT_SEPARATOR', min: 13.0, max: 24.0, desc: 'Component E in purge gas' },
  XMEAS_34: { name: 'Purge Comp F', unit: 'mol%', normal: 2.25, parent_unit: 'UNIT_SEPARATOR', min: 1.0, max: 4.0, desc: 'Inert component F in purge' },
  XMEAS_35: { name: 'Purge Comp G', unit: 'mol%', normal: 4.80, parent_unit: 'UNIT_SEPARATOR', min: 2.0, max: 8.0, desc: 'Product G in purge vapor' },
  XMEAS_36: { name: 'Purge Comp H', unit: 'mol%', normal: 2.45, parent_unit: 'UNIT_SEPARATOR', min: 1.0, max: 5.0, desc: 'Product H in purge vapor' },

  // ==========================================
  // UNIT_COMPRESSOR (Recycle Gas Compressor)
  // ==========================================
  XMEAS_5: { name: 'Recycle Flow Rate', unit: 'kscmh', normal: 26.9, parent_unit: 'UNIT_COMPRESSOR', min: 20.0, max: 35.0, desc: 'Recycled vapor to reactor feed' },
  XMEAS_20: { name: 'Compressor Shaft Power', unit: 'kW', normal: 341.0, parent_unit: 'UNIT_COMPRESSOR', min: 290, max: 400, desc: 'Centrifugal compressor motor work' },

  // ==========================================
  // UNIT_STRIPPER (Stripper Column & Product)
  // ==========================================
  XMEAS_15: { name: 'Stripper Sump Level', unit: '%', normal: 50.0, parent_unit: 'UNIT_STRIPPER', min: 35, max: 65, desc: 'Stripper column bottoms level' },
  XMEAS_16: { name: 'Stripper Pressure', unit: 'kPa', normal: 3010.0, parent_unit: 'UNIT_STRIPPER', min: 2800, max: 3200, desc: 'Column overhead pressure' },
  XMEAS_17: { name: 'Product Flow Rate', unit: 'm3/h', normal: 22.9, parent_unit: 'UNIT_STRIPPER', min: 16.0, max: 30.0, desc: 'Purified product discharge flow' },
  XMEAS_18: { name: 'Stripper Bottom Temp', unit: '°C', normal: 65.7, parent_unit: 'UNIT_STRIPPER', min: 55, max: 80, desc: 'Reboiler bottoms temperature' },
  XMEAS_19: { name: 'Stripper Steam Flow', unit: 'kg/h', normal: 1085.0, parent_unit: 'UNIT_STRIPPER', min: 800, max: 1400, desc: 'Stripping column steam mass flow' },
  // Stream 11: Final Product Stream Compositions (mol%)
  XMEAS_37: { name: 'Product Comp D', unit: 'mol%', normal: 0.15, parent_unit: 'UNIT_STRIPPER', min: 0.05, max: 0.4, desc: 'Unreacted D in product stream' },
  XMEAS_38: { name: 'Product Comp E', unit: 'mol%', normal: 0.85, parent_unit: 'UNIT_STRIPPER', min: 0.3, max: 1.5, desc: 'Unreacted E in product stream' },
  XMEAS_39: { name: 'Product Comp F', unit: 'mol%', normal: 0.05, parent_unit: 'UNIT_STRIPPER', min: 0.01, max: 0.2, desc: 'Inert F in product stream' },
  XMEAS_40: { name: 'Product Comp G', unit: 'mol%', normal: 53.75, parent_unit: 'UNIT_STRIPPER', min: 45.0, max: 60.0, desc: 'Target primary product G' },
  XMEAS_41: { name: 'Product Comp H', unit: 'mol%', normal: 43.85, parent_unit: 'UNIT_STRIPPER', min: 38.0, max: 52.0, desc: 'Target co-product H' },
};

// Machine categorization for dedicated section grouping
const MACHINE_SECTIONS = [
  { id: 'UNIT_FEED', name: 'Feed Delivery System', title: 'Reactant Feed Header (A, D, E, A+C)', count: 4, icon: '🚰' },
  { id: 'UNIT_REACTOR', name: 'Chemical Reactor', title: 'Exothermic CSTR & Reactor Feed Compositions', count: 12, icon: '⚡' },
  { id: 'UNIT_CONDENSER', name: 'Product Condenser', title: 'Shell-and-Tube Heat Exchanger Coolant', count: 2, icon: '❄️' },
  { id: 'UNIT_SEPARATOR', name: 'Vapor-Liquid Separator', title: 'High-Pressure Flash Drum & Purge Gas Analysis', count: 13, icon: '🌪️' },
  { id: 'UNIT_COMPRESSOR', name: 'Recycle Compressor', title: 'Centrifugal Gas Compressor & Recycle Loop', count: 2, icon: '🔄' },
  { id: 'UNIT_STRIPPER', name: 'Stripping Column & Product', title: 'Distillation Stripper & Final Product Analysis', count: 10, icon: '🧪' },
];

export default function SensorTimeline({ sensorData = {}, activeFault = null }) {
  const [selectedMachine, setSelectedMachine] = useState('ALL'); // 'ALL' or machine id
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedSections, setCollapsedSections] = useState({});

  // Rolling buffer of recent readings for all 43 sensors
  const [history, setHistory] = useState(() => {
    const init = {};
    Object.keys(SENSOR_META).forEach((key) => {
      init[key] = Array(15).fill(SENSOR_META[key].normal);
    });
    return init;
  });

  // Append incoming telemetry tick
  useEffect(() => {
    if (!sensorData || Object.keys(sensorData).length === 0) return;

    setHistory((prev) => {
      const updated = { ...prev };
      Object.keys(SENSOR_META).forEach((key) => {
        const val = sensorData[key] !== undefined ? sensorData[key] : SENSOR_META[key].normal;
        const currentArr = prev[key] || [];
        updated[key] = [...currentArr.slice(-19), val];
      });
      return updated;
    });
  }, [sensorData]);

  // Toggle collapse for a machine section
  const toggleCollapse = (machineId) => {
    setCollapsedSections((prev) => ({
      ...prev,
      [machineId]: !prev[machineId],
    }));
  };

  // Helper to generate SVG sparkline
  const renderSparkline = (points, minVal, maxVal, isDeviated) => {
    if (!points || points.length < 2) return null;
    const width = 80;
    const height = 22;
    const range = maxVal - minVal || 1.0;

    const coords = points.map((p, idx) => {
      const x = (idx / (points.length - 1)) * width;
      const normalizedY = Math.max(0, Math.min(1, (p - minVal) / range));
      const y = height - normalizedY * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    const pathD = `M ${coords.join(' L ')}`;
    const strokeColor = isDeviated ? '#f43f5e' : '#38bdf8';

    return (
      <svg width={width} height={height} style={{ overflow: 'visible' }}>
        <path
          d={pathD}
          fill="none"
          stroke={strokeColor}
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  };

  // Check if any sensor in a machine is deviated
  const getMachineStatus = (machineId) => {
    const machineSensors = Object.keys(SENSOR_META).filter((k) => SENSOR_META[k].parent_unit === machineId);
    let deviatedCount = 0;
    machineSensors.forEach((key) => {
      const val = sensorData[key] !== undefined ? sensorData[key] : SENSOR_META[key].normal;
      const meta = SENSOR_META[key];
      const diff = Math.abs(val - meta.normal);
      const pct = (diff / (meta.normal > 1 ? meta.normal : 1.0)) * 100;
      if (pct >= 5.0) deviatedCount++;
    });
    return {
      deviatedCount,
      hasDeviation: deviatedCount > 0,
      total: machineSensors.length,
    };
  };

  // Filter machines to display
  const displayedMachines = selectedMachine === 'ALL'
    ? MACHINE_SECTIONS
    : MACHINE_SECTIONS.filter((m) => m.id === selectedMachine);

  // Total counts
  const totalSensorsCount = Object.keys(SENSOR_META).length;
  let overallDeviated = 0;
  Object.keys(SENSOR_META).forEach((key) => {
    const val = sensorData[key] !== undefined ? sensorData[key] : SENSOR_META[key].normal;
    const meta = SENSOR_META[key];
    const diff = Math.abs(val - meta.normal);
    if ((diff / (meta.normal > 1 ? meta.normal : 1.0)) * 100 >= 5.0) {
      overallDeviated++;
    }
  });

  return (
    <div className="glass-panel timeline-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header with Title and Global Streaming Status */}
      <div className="chart-header" style={{ marginBottom: 0 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Activity size={22} color="var(--accent-secondary)" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
              Plant Telemetry & Transient Sparklines (41 Sensors)
            </h2>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Continuous 1 Hz sensor telemetry organized into dedicated machine sections across all 6 chemical process units.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          {overallDeviated > 0 ? (
            <div className="status-pill fault" style={{ background: 'rgba(244, 63, 94, 0.15)', borderColor: '#f43f5e', color: '#fda4af' }}>
              <AlertTriangle size={13} /> {overallDeviated} Alarms Active
            </div>
          ) : (
            <div className="status-pill normal">
              <CheckCircle2 size={13} /> All 41 Sensors Nominal
            </div>
          )}
          <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
            TimescaleDB 1 Hz
          </span>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
        </div>
      </div>

      {/* Machine Filter Tabs & Quick Search */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          paddingBottom: '0.85rem',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        {/* Machine Tabs */}
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginRight: '0.2rem' }}>
            <Layers size={14} /> Machine:
          </span>
          <button
            onClick={() => setSelectedMachine('ALL')}
            className={selectedMachine === 'ALL' ? 'btn-primary' : 'btn-outline'}
            style={{ padding: '0.3rem 0.75rem', fontSize: '0.78rem' }}
          >
            All Machines ({totalSensorsCount})
          </button>

          {MACHINE_SECTIONS.map((m) => {
            const status = getMachineStatus(m.id);
            const isSelected = selectedMachine === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setSelectedMachine(m.id)}
                className={isSelected ? 'btn-primary' : 'btn-outline'}
                style={{
                  padding: '0.3rem 0.7rem',
                  fontSize: '0.78rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  borderColor: status.hasDeviation ? '#f43f5e' : undefined,
                  background: isSelected ? undefined : status.hasDeviation ? 'rgba(244, 63, 94, 0.12)' : undefined,
                }}
              >
                <span>{m.icon}</span>
                <span>{m.name.split(' ')[0]}</span>
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '0.1rem 0.35rem',
                    borderRadius: '999px',
                    background: status.hasDeviation ? '#f43f5e' : 'rgba(255,255,255,0.1)',
                    color: '#fff',
                  }}
                >
                  {status.total}
                </span>
              </button>
            );
          })}
        </div>

        {/* Quick Search */}
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Search sensor (e.g. Temp, XMEAS_9)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '0.3rem 1.8rem 0.3rem 0.65rem',
              color: '#fff',
              fontSize: '0.78rem',
              outline: 'none',
              width: '210px',
            }}
          />
          <Search size={13} style={{ position: 'absolute', right: '6px', color: 'var(--text-muted)' }} />
        </div>
      </div>

      {/* Dedicated Machine Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {displayedMachines.map((machine) => {
          const status = getMachineStatus(machine.id);
          const isCollapsed = collapsedSections[machine.id];

          // Filter sensors for this machine
          let machineSensorKeys = Object.keys(SENSOR_META).filter(
            (k) => SENSOR_META[k].parent_unit === machine.id
          );

          if (searchQuery.trim()) {
            const q = searchQuery.toUpperCase();
            machineSensorKeys = machineSensorKeys.filter((k) => {
              const meta = SENSOR_META[k];
              return (
                k.toUpperCase().includes(q) ||
                meta.name.toUpperCase().includes(q) ||
                meta.unit.toUpperCase().includes(q) ||
                meta.desc.toUpperCase().includes(q)
              );
            });
          }

          if (machineSensorKeys.length === 0) return null;

          return (
            <div
              key={machine.id}
              style={{
                background: 'rgba(15, 23, 42, 0.55)',
                border: `1px solid ${status.hasDeviation ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)'}`,
                borderRadius: '10px',
                padding: '0.85rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
                transition: 'border-color 0.2s ease',
              }}
            >
              {/* Machine Section Header Bar */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
                onClick={() => toggleCollapse(machine.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>{machine.icon}</span>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <h3 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#fff' }}>
                        {machine.name}
                      </h3>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          padding: '0.15rem 0.45rem',
                          borderRadius: '4px',
                          background: 'rgba(99, 102, 241, 0.2)',
                          color: '#a5b4fc',
                          fontWeight: 600,
                        }}
                      >
                        {machine.id}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
                      {machine.title} • {machineSensorKeys.length} Sensors
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  {status.hasDeviation ? (
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        padding: '0.2rem 0.5rem',
                        borderRadius: '999px',
                        background: 'rgba(244, 63, 94, 0.2)',
                        color: '#fda4af',
                        border: '1px solid #f43f5e',
                      }}
                    >
                      ⚠️ {status.deviatedCount} DEVIATING
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        padding: '0.2rem 0.5rem',
                        borderRadius: '999px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        color: '#34d399',
                      }}
                    >
                      ✓ NORMAL
                    </span>
                  )}
                  {isCollapsed ? <ChevronRight size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                </div>
              </div>

              {/* Sensor Grid for this specific Machine */}
              {!isCollapsed && (
                <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(185px, 1fr))', gap: '0.75rem' }}>
                  {machineSensorKeys.map((key) => {
                    const val = sensorData[key] !== undefined ? sensorData[key] : SENSOR_META[key].normal;
                    const meta = SENSOR_META[key];
                    const deviation = Math.abs(val - meta.normal);
                    const percentDev = ((deviation / (meta.normal > 1 ? meta.normal : 1.0)) * 100).toFixed(1);
                    const isDeviated = parseFloat(percentDev) >= 5.0;
                    const isUp = val > meta.normal;
                    const points = history[key] || [];

                    return (
                      <div
                        key={key}
                        className={`sensor-card ${isDeviated ? 'deviated' : ''}`}
                        style={{
                          padding: '0.75rem 0.85rem',
                          background: isDeviated ? 'rgba(244, 63, 94, 0.08)' : 'rgba(23, 33, 50, 0.65)',
                          border: `1px solid ${isDeviated ? 'rgba(244, 63, 94, 0.45)' : 'var(--border-subtle)'}`,
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                            {key}
                          </span>
                          {isDeviated ? (
                            <span
                              style={{
                                fontSize: '0.68rem',
                                color: '#f43f5e',
                                fontWeight: 700,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.15rem',
                              }}
                            >
                              {isUp ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                              {percentDev}%
                            </span>
                          ) : (
                            <span style={{ fontSize: '0.68rem', color: '#64748b' }}>
                              Nominal
                            </span>
                          )}
                        </div>

                        <div
                          style={{
                            fontSize: '0.76rem',
                            fontWeight: 600,
                            color: '#e2e8f0',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                          title={meta.name}
                        >
                          {meta.name}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: '0.2rem' }}>
                          <div className="sensor-val" style={{ fontSize: '1.15rem' }}>
                            {typeof val === 'number' ? val.toFixed(meta.unit === 'mol%' || meta.normal < 1 ? 2 : 1) : val}
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: '0.25rem', fontWeight: 500 }}>
                              {meta.unit}
                            </span>
                          </div>
                          <div>
                            {renderSparkline(points, meta.min, meta.max, isDeviated)}
                          </div>
                        </div>

                        <div style={{ fontSize: '0.68rem', color: '#64748b', display: 'flex', justifyContent: 'space-between', marginTop: '0.1rem' }}>
                          <span>Norm: {meta.normal} {meta.unit}</span>
                          <span title={meta.desc} style={{ cursor: 'help' }}>ℹ️</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
