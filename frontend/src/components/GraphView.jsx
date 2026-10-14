import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { Network, ZoomIn, ZoomOut, Maximize2, Info, Layers } from 'lucide-react';
import { fetchGraphTopology } from '../api/client';

// Standard flowsheet preset layout coordinates for TEP units
const PRESET_POSITIONS = {
  // Main Process Units
  UNIT_FEED: { x: 100, y: 240 },
  UNIT_REACTOR: { x: 300, y: 240 },
  UNIT_CONDENSER: { x: 500, y: 240 },
  UNIT_SEPARATOR: { x: 700, y: 240 },
  UNIT_COMPRESSOR: { x: 500, y: 80 },
  UNIT_STRIPPER: { x: 900, y: 240 },

  // UNIT_FEED Sensors (around x=100)
  XMEAS_1: { x: 50, y: 160 },
  XMEAS_2: { x: 110, y: 150 },
  XMEAS_3: { x: 50, y: 320 },
  XMEAS_4: { x: 110, y: 330 },

  // UNIT_REACTOR Sensors (around x=300)
  XMEAS_6: { x: 240, y: 150 },
  XMEAS_7: { x: 300, y: 150 },
  XMEAS_8: { x: 360, y: 150 },
  XMEAS_9: { x: 240, y: 330 },
  XMEAS_21: { x: 300, y: 330 },
  XMV_10: { x: 360, y: 330 },

  // UNIT_CONDENSER Sensors (around x=500)
  XMEAS_22: { x: 470, y: 330 },
  XMV_11: { x: 530, y: 330 },

  // UNIT_SEPARATOR Sensors (around x=700)
  XMEAS_10: { x: 650, y: 150 },
  XMEAS_11: { x: 710, y: 150 },
  XMEAS_12: { x: 650, y: 330 },
  XMEAS_13: { x: 710, y: 330 },
  XMEAS_14: { x: 760, y: 330 },

  // UNIT_COMPRESSOR Sensors (around x=500, y=80)
  XMEAS_5: { x: 430, y: 40 },
  XMEAS_20: { x: 570, y: 40 },

  // UNIT_STRIPPER Sensors (around x=900)
  XMEAS_15: { x: 860, y: 150 },
  XMEAS_16: { x: 920, y: 150 },
  XMEAS_17: { x: 860, y: 330 },
  XMEAS_18: { x: 920, y: 330 },
  XMEAS_19: { x: 970, y: 330 },

  // Failure Modes
  IDV_4: { x: 300, y: 410 },
  IDV_6: { x: 100, y: 410 },
  IDV_11: { x: 380, y: 410 },
};

export default function GraphView({
  highlightedUnit = null,
  causalPath = [],
  onSelectNode = null
}) {
  const containerRef = useRef(null);
  const cyInstance = useRef(null);
  const [selectedNodeInfo, setSelectedNodeInfo] = useState(null);
  const [showSensors, setShowSensors] = useState(true);

  // Initialize Cytoscape canvas
  useEffect(() => {
    if (!containerRef.current) return;

    let isMounted = true;

    async function initGraph() {
      let elements = [];
      try {
        const data = await fetchGraphTopology();
        if (data && data.nodes) {
          // Convert to Cytoscape elements with preset positions
          const nodes = data.nodes.map((n) => {
            const pos = PRESET_POSITIONS[n.id] || {
              x: 100 + Math.random() * 600,
              y: 100 + Math.random() * 200,
            };
            return {
              group: 'nodes',
              data: {
                id: n.id,
                label: n.name || n.id,
                type: n.label || 'Unit',
                code: n.code || '',
                description: n.description || '',
              },
              position: pos,
            };
          });

          const nodeIds = new Set(nodes.map((n) => n.data.id));
          const validEdges = data.edges
            .filter((e) => e && e.source && e.target && nodeIds.has(e.source) && nodeIds.has(e.target))
            .map((e, idx) => ({
              group: 'edges',
              data: {
                id: e.id || `edge_${idx}`,
                source: e.source,
                target: e.target,
                type: e.type || 'FEEDS',
              },
            }));

          elements = [...nodes, ...validEdges];
        }
      } catch (err) {
        console.warn('Using fallback Cytoscape elements:', err);
      }

      if (!isMounted || !containerRef.current) return;

      // Initialize Cytoscape
      const cy = cytoscape({
        container: containerRef.current,
        elements: elements.length > 0 ? elements : [
          { group: 'nodes', data: { id: 'UNIT_FEED', label: 'Feed System', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_FEED },
          { group: 'nodes', data: { id: 'UNIT_REACTOR', label: 'Chemical Reactor', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_REACTOR },
          { group: 'nodes', data: { id: 'UNIT_CONDENSER', label: 'Condenser', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_CONDENSER },
          { group: 'nodes', data: { id: 'UNIT_SEPARATOR', label: 'Separator', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_SEPARATOR },
          { group: 'nodes', data: { id: 'UNIT_COMPRESSOR', label: 'Recycle Compressor', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_COMPRESSOR },
          { group: 'nodes', data: { id: 'UNIT_STRIPPER', label: 'Stripper Column', type: 'Unit' }, position: PRESET_POSITIONS.UNIT_STRIPPER },
          { group: 'edges', data: { id: 'e1', source: 'UNIT_FEED', target: 'UNIT_REACTOR', type: 'FEEDS' } },
          { group: 'edges', data: { id: 'e2', source: 'UNIT_REACTOR', target: 'UNIT_CONDENSER', type: 'FEEDS' } },
          { group: 'edges', data: { id: 'e3', source: 'UNIT_CONDENSER', target: 'UNIT_SEPARATOR', type: 'FEEDS' } },
          { group: 'edges', data: { id: 'e4', source: 'UNIT_SEPARATOR', target: 'UNIT_COMPRESSOR', type: 'FEEDS' } },
          { group: 'edges', data: { id: 'e5', source: 'UNIT_COMPRESSOR', target: 'UNIT_REACTOR', type: 'FEEDS' } },
          { group: 'edges', data: { id: 'e6', source: 'UNIT_SEPARATOR', target: 'UNIT_STRIPPER', type: 'FEEDS' } },
        ],
        style: [
          // Base Node Style
          {
            selector: 'node',
            style: {
              'background-color': '#1e293b',
              'label': 'data(label)',
              'color': '#f8fafc',
              'font-size': '11px',
              'font-family': 'Outfit, sans-serif',
              'font-weight': 600,
              'text-valign': 'center',
              'text-halign': 'center',
              'text-wrap': 'wrap',
              'text-max-width': '80px',
              'width': '75px',
              'height': '38px',
              'shape': 'roundrectangle',
              'border-width': 1.5,
              'border-color': '#475569',
              'transition-property': 'background-color, border-color, border-width, width, height',
              'transition-duration': '0.3s',
            },
          },
          // Unit Nodes
          {
            selector: 'node[type = "Unit"]',
            style: {
              'background-color': '#0f172a',
              'border-color': '#6366f1',
              'border-width': 2,
              'width': '84px',
              'height': '42px',
            },
          },
          // Sensor Nodes
          {
            selector: 'node[type = "Sensor"]',
            style: {
              'background-color': '#082f49',
              'border-color': '#0284c7',
              'shape': 'ellipse',
              'width': '40px',
              'height': '40px',
              'font-size': '9px',
            },
          },
          // FailureMode Nodes
          {
            selector: 'node[type = "FailureMode"]',
            style: {
              'background-color': '#450a0a',
              'border-color': '#dc2626',
              'shape': 'diamond',
              'width': '44px',
              'height': '44px',
              'font-size': '9px',
            },
          },
          // Base Edge Style
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#334155',
              'target-arrow-color': '#334155',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'arrow-scale': 1.2,
            },
          },
          // Recycle loop edge
          {
            selector: 'edge[source = "UNIT_COMPRESSOR"]',
            style: {
              'line-style': 'dashed',
              'line-dash-pattern': [6, 3],
              'line-color': '#0ea5e9',
              'target-arrow-color': '#0ea5e9',
            },
          },
          // Highlighted Root Cause Node
          {
            selector: '.root-cause',
            style: {
              'background-color': '#e11d48',
              'border-color': '#fecdd3',
              'border-width': 3.5,
              'color': '#ffffff',
              'width': '95px',
              'height': '48px',
              'font-size': '12px',
              'font-weight': 700,
              'shadow-blur': 25,
              'shadow-color': '#e11d48',
              'shadow-opacity': 0.85,
            },
          },
          // Highlighted Propagation Trajectory Nodes
          {
            selector: '.propagation-node',
            style: {
              'background-color': '#be185d',
              'border-color': '#f472b6',
              'border-width': 2.5,
              'shadow-blur': 15,
              'shadow-color': '#be185d',
              'shadow-opacity': 0.6,
            },
          },
          // Highlighted Propagation Trajectory Edges
          {
            selector: '.propagation-edge',
            style: {
              'line-color': '#f43f5e',
              'target-arrow-color': '#f43f5e',
              'width': 4.5,
              'line-style': 'solid',
              'shadow-blur': 10,
              'shadow-color': '#f43f5e',
              'shadow-opacity': 0.8,
            },
          },
        ],
        layout: {
          name: 'preset',
        },
        userZoomingEnabled: true,
        userPanningEnabled: true,
        boxSelectionEnabled: false,
      });

      // Click node handler
      cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        const d = node.data();
        setSelectedNodeInfo(d);
        if (onSelectNode) onSelectNode(d);
      });

      cy.on('tap', (evt) => {
        if (evt.target === cy) {
          setSelectedNodeInfo(null);
        }
      });

      cy.fit(undefined, 30);
      cyInstance.current = cy;
    }

    initGraph();

    return () => {
      isMounted = false;
      if (cyInstance.current) {
        cyInstance.current.destroy();
        cyInstance.current = null;
      }
    };
  }, []);

  // Update highlighting whenever highlightedUnit or causalPath changes
  useEffect(() => {
    const cy = cyInstance.current;
    if (!cy) return;

    // Reset existing highlights
    cy.elements().removeClass('root-cause');
    cy.elements().removeClass('propagation-node');
    cy.elements().removeClass('propagation-edge');

    if (highlightedUnit) {
      // Highlight root cause unit
      const rootNode = cy.$(`node[id = "${highlightedUnit}"]`);
      if (rootNode.length > 0) {
        rootNode.addClass('root-cause');
      }

      // Highlight propagation path nodes & edges
      if (causalPath && causalPath.length > 0) {
        causalPath.forEach((unitId, idx) => {
          if (unitId !== highlightedUnit) {
            cy.$(`node[id = "${unitId}"]`).addClass('propagation-node');
          }

          if (idx < causalPath.length - 1) {
            const nextUnitId = causalPath[idx + 1];
            // Find edge connecting unitId to nextUnitId
            const edge = cy.$(`edge[source = "${unitId}"][target = "${nextUnitId}"]`);
            if (edge.length > 0) {
              edge.addClass('propagation-edge');
            }
          }
        });
      }
    }
  }, [highlightedUnit, causalPath]);

  // Toggle sensor visibility
  const handleToggleSensors = () => {
    const cy = cyInstance.current;
    if (!cy) return;
    const nextState = !showSensors;
    setShowSensors(nextState);

    if (nextState) {
      cy.$('node[type = "Sensor"]').style('display', 'element');
      cy.$('edge[type = "MEASURES"]').style('display', 'element');
    } else {
      cy.$('node[type = "Sensor"]').style('display', 'none');
      cy.$('edge[type = "MEASURES"]').style('display', 'none');
    }
  };

  const handleZoomIn = () => cyInstance.current?.zoom(cyInstance.current.zoom() * 1.25);
  const handleZoomOut = () => cyInstance.current?.zoom(cyInstance.current.zoom() * 0.8);
  const handleReset = () => cyInstance.current?.fit(undefined, 30);

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* Header with Control Buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Network size={20} color="var(--accent-primary)" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Plant Topology & Cytoscape Knowledge Graph</h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <button
            className="btn-outline"
            style={{ padding: '0.3rem 0.6rem', fontSize: '0.78rem' }}
            onClick={handleToggleSensors}
            title="Toggle Sensor Nodes"
          >
            <Layers size={13} /> {showSensors ? 'Hide Sensors' : 'Show Sensors'}
          </button>
          <button
            className="btn-outline"
            style={{ padding: '0.3rem 0.5rem' }}
            onClick={handleZoomIn}
            title="Zoom In"
          >
            <ZoomIn size={14} />
          </button>
          <button
            className="btn-outline"
            style={{ padding: '0.3rem 0.5rem' }}
            onClick={handleZoomOut}
            title="Zoom Out"
          >
            <ZoomOut size={14} />
          </button>
          <button
            className="btn-outline"
            style={{ padding: '0.3rem 0.5rem' }}
            onClick={handleReset}
            title="Reset View"
          >
            <Maximize2 size={14} />
          </button>
        </div>
      </div>

      {/* Cytoscape Canvas Container */}
      <div
        style={{
          width: '100%',
          height: '380px',
          background: 'rgba(8, 11, 18, 0.75)',
          borderRadius: '10px',
          position: 'relative',
          border: '1px solid var(--border-subtle)',
          overflow: 'hidden',
        }}
      >
        <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

        {/* Selected Node Details Tooltip Card */}
        {selectedNodeInfo && (
          <div
            style={{
              position: 'absolute',
              bottom: '12px',
              left: '12px',
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(99, 102, 241, 0.4)',
              borderRadius: '8px',
              padding: '0.6rem 0.9rem',
              backdropFilter: 'blur(8px)',
              fontSize: '0.82rem',
              maxWidth: '280px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
              zIndex: 10,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
              <Info size={14} /> {selectedNodeInfo.label}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '0.2rem' }}>
              Type: <strong style={{ color: '#fff' }}>{selectedNodeInfo.type}</strong> | ID: <code>{selectedNodeInfo.id}</code>
            </div>
            {selectedNodeInfo.description && (
              <div style={{ color: '#cbd5e1', fontSize: '0.74rem', marginTop: '0.3rem', lineHeight: 1.3 }}>
                {selectedNodeInfo.description}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '1.2rem', fontSize: '0.75rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#0f172a', border: '1.5px solid #6366f1' }}></span>
          Plant Unit
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '9px', height: '9px', borderRadius: '50%', background: '#082f49', border: '1.5px solid #0284c7' }}></span>
          Sensor
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '10px', height: '10px', background: '#e11d48', borderRadius: '2px', boxShadow: '0 0 8px #e11d48' }}></span>
          Root Cause Unit
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '18px', height: '3px', background: '#f43f5e' }}></span>
          Causal Propagation Path
        </span>
      </div>
    </div>
  );
}
