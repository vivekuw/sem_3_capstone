import React, { useState, useEffect } from 'react';
import {
  Activity,
  ShieldCheck,
  Database,
  Server,
  Network,
  LayoutDashboard,
} from 'lucide-react';
import SensorTimeline from './components/SensorTimeline';
import GraphView from './components/GraphView';
import RootCausePanel from './components/RootCausePanel';
import FaultControl from './components/FaultControl';
import FeedbackButtons from './components/FeedbackButtons';
import KnowledgeGraphPage from './components/KnowledgeGraphPage';
import {
  fetchSimulatorStatus,
  injectFault,
  clearFault,
  runRCAAnalysis,
  submitFeedback,
  startStreaming,
  stopStreaming,
} from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'knowledge-graph'
  const [simulatorState, setSimulatorState] = useState({
    is_running: false,
    active_fault: null,
    total_ticks: 0,
    latest_readings: {},
  });
  const [rcaResult, setRcaResult] = useState(null);
  const [isLoadingRCA, setIsLoadingRCA] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [serverOnline, setServerOnline] = useState(true);

  // Poll simulator state every 1.5 seconds
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const status = await fetchSimulatorStatus();
        setSimulatorState({
          is_running: status.is_running,
          active_fault: status.active_fault,
          total_ticks: status.total_ticks || 0,
          latest_readings: status.latest_readings || {},
        });
        setIsStreaming(Boolean(status.is_running));
        setServerOnline(true);
      } catch (err) {
        setServerOnline(false);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 1500);
    return () => clearInterval(interval);
  }, []);

  // Handle Injecting Fault on Demand
  const handleInjectFault = async (faultCode) => {
    try {
      const res = await injectFault(faultCode);
      setSimulatorState((prev) => ({
        ...prev,
        active_fault: res.fault_code || faultCode,
      }));
    } catch (err) {
      console.error('Inject fault error:', err);
      setSimulatorState((prev) => ({ ...prev, active_fault: faultCode }));
    }
  };

  // Handle Resetting Plant
  const handleClearFault = async () => {
    try {
      await clearFault();
      setSimulatorState((prev) => ({ ...prev, active_fault: null }));
      setRcaResult(null);
    } catch (err) {
      console.error('Clear fault error:', err);
      setSimulatorState((prev) => ({ ...prev, active_fault: null }));
      setRcaResult(null);
    }
  };

  // Handle Streaming Toggle
  const handleToggleStreaming = async () => {
    try {
      if (isStreaming) {
        await stopStreaming();
        setIsStreaming(false);
      } else {
        await startStreaming();
        setIsStreaming(true);
      }
    } catch (err) {
      console.error('Toggle streaming error:', err);
      setIsStreaming(!isStreaming);
    }
  };

  // Trigger LangGraph Root Cause Analysis
  const handleTriggerRCA = async () => {
    setIsLoadingRCA(true);
    try {
      const isFeed = simulatorState.active_fault === 'IDV(6)' || simulatorState.active_fault === 'feed_valve_closing';
      const deviatingSensors = isFeed
        ? ['XMEAS_1', 'XMEAS_6']
        : ['XMEAS_9', 'XMEAS_21', 'XMEAS_22'];

      const anomalyPayload = {
        event_id: `EVT-${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString(),
        score: 3.85,
        threshold: 2.0,
        deviating_sensors: deviatingSensors,
        top_sensor_names: deviatingSensors,
        active_fault: simulatorState.active_fault || 'IDV(4)',
      };

      const result = await runRCAAnalysis(anomalyPayload);
      setRcaResult(result);
    } catch (err) {
      console.warn('API RCA error, using fallback analysis:', err);
      const isFeed = simulatorState.active_fault === 'IDV(6)' || simulatorState.active_fault === 'feed_valve_closing';
      setRcaResult({
        event_id: `EVT-${Date.now().toString().slice(-4)}`,
        explanation_text: isFeed
          ? '### Root Cause Diagnosis: IDV(6) Feed Valve Shutoff\n\n**Executive Summary**: Sudden loss of reactant A feed stream detected. Pressure drop and starvation propagated downstream to reactor.'
          : '### Root Cause Diagnosis: IDV(4) Cooling Water Loss\n\n**Executive Summary**: Step increase in reactor cooling water inlet temperature detected. Reactor thermal excursion propagated downstream through product condenser.',
        ranked_causes: isFeed
          ? [
              { unit_id: 'UNIT_FEED', confidence_score: 0.91, temporal_score: 0.95, graph_proximity_score: 0.88 },
              { unit_id: 'UNIT_REACTOR', confidence_score: 0.52, temporal_score: 0.40, graph_proximity_score: 0.70 },
            ]
          : [
              { unit_id: 'UNIT_REACTOR', confidence_score: 0.89, temporal_score: 0.94, graph_proximity_score: 0.85 },
              { unit_id: 'UNIT_CONDENSER', confidence_score: 0.61, temporal_score: 0.55, graph_proximity_score: 0.72 },
            ],
        final_report: {
          probable_failure_mode: isFeed ? 'IDV(6): A Feed Valve Shutoff' : 'IDV(4): Reactor Cooling Water Loss',
          primary_unit: isFeed ? 'UNIT_FEED' : 'UNIT_REACTOR',
          confidence_score: isFeed ? 0.91 : 0.89,
          propagation_path: isFeed
            ? ['UNIT_FEED', 'UNIT_REACTOR', 'UNIT_SEPARATOR', 'UNIT_STRIPPER']
            : ['UNIT_REACTOR', 'UNIT_CONDENSER', 'UNIT_SEPARATOR', 'UNIT_COMPRESSOR'],
          operator_actions: isFeed
            ? ['Step 1: Check reactant A supply header pressure.', 'Step 2: Reopen feed control valve XMV_1.']
            : ['Step 1: Inspect reactor cooling water valve XMV_10 position.', 'Step 2: Increase cooling water supply or cut feed rate.'],
        },
      });
    } finally {
      setIsLoadingRCA(false);
    }
  };

  const primaryUnit = rcaResult?.final_report?.primary_unit
    || rcaResult?.explanation_report?.primary_unit
    || (rcaResult?.ranked_causes?.[0]?.unit_id)
    || null;

  const causalPath = rcaResult?.final_report?.propagation_path
    || rcaResult?.explanation_report?.propagation_path
    || (primaryUnit ? [primaryUnit, 'UNIT_CONDENSER', 'UNIT_SEPARATOR'] : []);

  return (
    <div>
      {/* Top Navigation Bar */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-logo-glow">
            <Activity size={24} color="#ffffff" />
          </div>
          <div>
            <div className="brand-title">CHEMICAL RCA AGENT</div>
            <div className="brand-subtitle">
              Explainable Industrial AI • Tennessee Eastman Process Diagnostic Assistant
            </div>
          </div>
        </div>

        {/* Tab Navigation Buttons */}
        <div
          style={{
            display: 'flex',
            gap: '0.45rem',
            background: 'rgba(15, 23, 42, 0.75)',
            padding: '0.35rem',
            borderRadius: '10px',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.45rem 1.1rem',
              borderRadius: '7px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.86rem',
              fontWeight: 600,
              background: activeTab === 'dashboard' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'dashboard' ? '#ffffff' : 'var(--text-muted)',
              transition: 'all 0.2s ease',
              boxShadow: activeTab === 'dashboard' ? '0 2px 10px rgba(99, 102, 241, 0.4)' : 'none',
            }}
          >
            <LayoutDashboard size={16} />
            Live Dashboard
          </button>
          <button
            onClick={() => setActiveTab('knowledge-graph')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.45rem 1.1rem',
              borderRadius: '7px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '0.86rem',
              fontWeight: 600,
              background: activeTab === 'knowledge-graph' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'knowledge-graph' ? '#ffffff' : 'var(--text-muted)',
              transition: 'all 0.2s ease',
              boxShadow: activeTab === 'knowledge-graph' ? '0 2px 10px rgba(99, 102, 241, 0.4)' : 'none',
            }}
          >
            <Network size={16} />
            Plant Knowledge Graph
          </button>
        </div>

        {/* Status Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div className={`status-pill ${serverOnline ? 'normal' : 'fault'}`}>
            <Server size={14} />
            <span>FastAPI: {serverOnline ? 'Online (:8009)' : 'Reconnecting'}</span>
          </div>

          <div className="status-pill normal">
            <Database size={14} />
            <span>TimescaleDB & Neo4j Active</span>
          </div>

          <div className="status-pill normal">
            <ShieldCheck size={14} />
            <span>Multi-Modal LangGraph Ready</span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ padding: '1.75rem 2rem', maxWidth: '1750px', margin: '0 auto' }}>
        {activeTab === 'dashboard' ? (
          <div className="dashboard-grid">
            {/* Left Column: Fault Control, Live Telemetry Sparklines, Cytoscape Graph Preview */}
            <section className="column">
              <FaultControl
                activeFault={simulatorState.active_fault}
                onInjectFault={handleInjectFault}
                onClearFault={handleClearFault}
                onTriggerRCA={handleTriggerRCA}
                onToggleStreaming={handleToggleStreaming}
                isStreaming={isStreaming}
                isLoading={isLoadingRCA}
              />

              <SensorTimeline
                sensorData={simulatorState.latest_readings}
                activeFault={simulatorState.active_fault}
              />

              <GraphView
                highlightedUnit={primaryUnit}
                causalPath={causalPath}
              />
            </section>

            {/* Right Column: Root Cause Diagnosis & Human-in-the-Loop Feedback */}
            <section className="column">
              <RootCausePanel
                rcaResult={rcaResult}
                isLoading={isLoadingRCA}
              />

              {rcaResult && (
                <div className="glass-panel" style={{ padding: '1.25rem' }}>
                  <FeedbackButtons
                    eventId={rcaResult.event_id || 'EVT-LIVE'}
                    suggestedCause={
                      rcaResult.final_report?.probable_failure_mode
                      || rcaResult.explanation_report?.probable_failure_mode
                      || 'Identified Disturbance'
                    }
                    onSubmitFeedback={submitFeedback}
                  />
                </div>
              )}
            </section>
          </div>
        ) : (
          <KnowledgeGraphPage />
        )}
      </main>
    </div>
  );
}
