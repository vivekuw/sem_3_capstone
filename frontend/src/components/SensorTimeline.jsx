import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

const SENSOR_META = {
  XMEAS_9: { name: 'Reactor Temperature', unit: '°C', normal: 120.4, parent_unit: 'UNIT_REACTOR', min: 110, max: 140 },
  XMEAS_21: { name: 'Cooling Water Return', unit: '°C', normal: 94.4, parent_unit: 'UNIT_REACTOR', min: 85, max: 120 },
  XMEAS_7: { name: 'Reactor Pressure', unit: 'kPa', normal: 2705.0, parent_unit: 'UNIT_REACTOR', min: 2500, max: 2900 },
  XMEAS_1: { name: 'Reactant A Feed', unit: 'kscmh', normal: 0.25, parent_unit: 'UNIT_FEED', min: 0.0, max: 0.4 },
  XMEAS_22: { name: 'Condenser Cooling Out', unit: '°C', normal: 77.2, parent_unit: 'UNIT_CONDENSER', min: 70, max: 95 },
  XMEAS_11: { name: 'Separator Temp', unit: '°C', normal: 80.1, parent_unit: 'UNIT_SEPARATOR', min: 72, max: 95 },
  XMEAS_13: { name: 'Separator Pressure', unit: 'kPa', normal: 2633.0, parent_unit: 'UNIT_SEPARATOR', min: 2450, max: 2800 },
  XMEAS_20: { name: 'Compressor Work', unit: 'kW', normal: 341.0, parent_unit: 'UNIT_COMPRESSOR', min: 310, max: 390 },
  XMEAS_18: { name: 'Stripper Temp', unit: '°C', normal: 65.7, parent_unit: 'UNIT_STRIPPER', min: 58, max: 78 },
};

export default function SensorTimeline({ sensorData = {}, activeFault = null }) {
  // Store rolling buffer of recent readings for each sensor (up to 20 samples)
  const [history, setHistory] = useState(() => {
    const init = {};
    Object.keys(SENSOR_META).forEach((key) => {
      init[key] = Array(15).fill(SENSOR_META[key].normal);
    });
    return init;
  });

  // Append new sensor sample on each incoming sensorData tick
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

  // Helper to generate SVG sparkline path
  const renderSparkline = (points, minVal, maxVal, isDeviated) => {
    if (!points || points.length < 2) return null;
    const width = 80;
    const height = 24;
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

  const sensorKeys = Object.keys(SENSOR_META);

  return (
    <div className="glass-panel timeline-card">
      <div className="chart-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Activity size={20} color="var(--accent-secondary)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Live Telemetry & Transient Sparklines</h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            TimescaleDB 1 Hz Stream
          </span>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
        </div>
      </div>

      <div className="sensor-grid">
        {sensorKeys.map((key) => {
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
                transition: 'all 0.3s ease',
                borderLeft: isDeviated ? '3px solid #f43f5e' : '3px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>
                  {key} <span style={{ fontSize: '0.68rem', color: '#64748b' }}>({meta.parent_unit})</span>
                </span>
                {isDeviated ? (
                  <span style={{ color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '3px', fontSize: '0.72rem', fontWeight: 700 }}>
                    <AlertTriangle size={12} /> Δ +{percentDev}%
                  </span>
                ) : (
                  <span style={{ color: '#10b981', fontSize: '0.70rem' }}>Normal</span>
                )}
              </div>

              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: '0.1rem' }}>
                {meta.name}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '0.4rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.35rem' }}>
                    <span className="sensor-val" style={{ color: isDeviated ? 'var(--accent-rose)' : '#ffffff', fontSize: '1.25rem' }}>
                      {typeof val === 'number' ? val.toFixed(2) : val}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{meta.unit}</span>
                  </div>
                  <div style={{ fontSize: '0.70rem', color: '#64748b' }}>
                    Setpoint: {meta.normal} {meta.unit}
                  </div>
                </div>

                {/* SVG Sparkline */}
                <div>
                  {renderSparkline(points, meta.min, meta.max, isDeviated)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
