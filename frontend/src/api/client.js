/**
 * API client to interact with the FastAPI Chemical RCA Agent backend (Phase 8 & 9).
 */

const API_BASE = '/api';

export async function fetchSimulatorStatus() {
  const res = await fetch(`${API_BASE}/simulator/status`);
  if (!res.ok) throw new Error('Failed to fetch simulator status');
  return res.json();
}

export async function injectFault(faultCode) {
  const res = await fetch(`${API_BASE}/simulator/inject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fault_code: faultCode }),
  });
  if (!res.ok) throw new Error('Failed to inject fault');
  return res.json();
}

export async function clearFault() {
  const res = await fetch(`${API_BASE}/simulator/clear`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to clear fault');
  return res.json();
}

export async function stepSimulation() {
  const res = await fetch(`${API_BASE}/simulator/step`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to step simulator');
  return res.json();
}

export async function startStreaming() {
  const res = await fetch(`${API_BASE}/simulator/start_streaming`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to start streaming');
  return res.json();
}

export async function stopStreaming() {
  const res = await fetch(`${API_BASE}/simulator/stop_streaming`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to stop streaming');
  return res.json();
}

export async function fetchGraphTopology() {
  const res = await fetch(`${API_BASE}/graph/subgraph`);
  if (!res.ok) throw new Error('Failed to fetch KG topology');
  return res.json();
}

export async function fetchAnomalies() {
  const res = await fetch(`${API_BASE}/anomalies`);
  if (!res.ok) throw new Error('Failed to fetch anomalies');
  return res.json();
}

export async function runRCAAnalysis(deviatingSensors = null, eventId = null) {
  const res = await fetch(`${API_BASE}/anomalies/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_id: eventId,
      deviating_sensors: deviatingSensors,
      lookback_minutes: 5,
    }),
  });
  if (!res.ok) throw new Error('Failed to run RCA analysis');
  return res.json();
}

export async function submitFeedback(payload) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to submit operator feedback');
  return res.json();
}
