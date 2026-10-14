import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import {
  Network,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Info,
  Search,
  Layers,
  Filter,
  Activity,
  AlertTriangle,
  Cpu,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';
import { fetchGraphTopology } from '../api/client';

// Wide-spaced flowsheet coordinates for TEP units and sensors (520px machine separation)
const PRESET_POSITIONS = {
  // Main Process Units (Generously spaced across flowsheet)
  UNIT_FEED: { x: 180, y: 360 },
  UNIT_REACTOR: { x: 700, y: 360 },
  UNIT_CONDENSER: { x: 1220, y: 360 },
  UNIT_SEPARATOR: { x: 1740, y: 360 },
  UNIT_COMPRESSOR: { x: 1220, y: 110 },
  UNIT_STRIPPER: { x: 2260, y: 360 },

  // UNIT_FEED Sensors (around x=180)
  XMEAS_1: { x: 60, y: 220 },
  XMEAS_2: { x: 180, y: 190 },
  XMEAS_3: { x: 300, y: 220 },
  XMEAS_4: { x: 180, y: 500 },
  IDV_6: { x: 180, y: 620 },

  // UNIT_REACTOR Sensors (around x=700)
  XMEAS_6: { x: 570, y: 210 },
  XMEAS_7: { x: 700, y: 180 },
  XMEAS_8: { x: 830, y: 210 },
  XMEAS_9: { x: 570, y: 510 },
  XMEAS_21: { x: 700, y: 540 },
  XMV_10: { x: 830, y: 510 },
  IDV_4: { x: 630, y: 640 },
  IDV_11: { x: 770, y: 640 },

  // UNIT_CONDENSER Sensors (around x=1220)
  XMEAS_22: { x: 1150, y: 510 },
  XMV_11: { x: 1290, y: 510 },
  IDV_5: { x: 1220, y: 630 },

  // UNIT_SEPARATOR Sensors (around x=1740)
  XMEAS_10: { x: 1610, y: 210 },
  XMEAS_11: { x: 1740, y: 180 },
  XMEAS_13: { x: 1870, y: 210 },
  XMEAS_12: { x: 1670, y: 510 },
  XMEAS_14: { x: 1810, y: 510 },

  // UNIT_COMPRESSOR Sensors (around x=1220, y=110)
  XMEAS_5: { x: 1090, y: 40 },
  XMEAS_20: { x: 1350, y: 40 },

  // UNIT_STRIPPER Sensors (around x=2260)
  XMEAS_15: { x: 2130, y: 210 },
  XMEAS_16: { x: 2260, y: 180 },
  XMEAS_17: { x: 2390, y: 210 },
  XMEAS_18: { x: 2190, y: 510 },
  XMEAS_19: { x: 2330, y: 510 },
  IDV_18: { x: 2260, y: 630 },

  // Feed segment piping equipment (from Neo4j topology)
  'P-100': { x: -340, y: 360 },
  'V-101': { x: -180, y: 360 },
  'HX-102': { x: -20, y: 360 },
  'R-103': { x: 180, y: 100 },
  P100_flow: { x: -340, y: 230 },
  P100_pressure: { x: -340, y: 490 },
  V101_pos: { x: -180, y: 230 },
  V101_flow: { x: -180, y: 490 },
  HX102_temp_in: { x: -20, y: 230 },
  HX102_temp_out: { x: -20, y: 490 },
};

// Detailed metadata dictionary for process equipment and instrumentation
const UNIT_DETAILS = {
  UNIT_FEED: {
    title: 'Reactant Feed Header System',
    description: 'High-pressure manifold delivering gaseous reactants A, D, E, and combined A+C mix into the reactor vessel.',
    upstream: ['Plant Raw Material Battery Limits'],
    downstream: ['UNIT_REACTOR'],
    sensors: ['XMEAS_1 (A Flow)', 'XMEAS_2 (D Flow)', 'XMEAS_3 (E Flow)', 'XMEAS_4 (A+C Flow)'],
    failureModes: ['IDV(1) Feed Ratio Step', 'IDV(2) B Composition Step', 'IDV(6) A Feed Loss', 'IDV(7) C Header Pressure Loss'],
  },
  UNIT_REACTOR: {
    title: 'Exothermic CSTR Chemical Reactor',
    description: 'Continuous Stirred-Tank Reactor operating at 120.4 °C and 2705 kPa where reactants A, C, D, E react exothermically to form products G and H.',
    upstream: ['UNIT_FEED', 'UNIT_COMPRESSOR (Recycle Gas)'],
    downstream: ['UNIT_CONDENSER'],
    sensors: ['XMEAS_6 (Feed Rate)', 'XMEAS_7 (Pressure)', 'XMEAS_8 (Level)', 'XMEAS_9 (Temperature)', 'XMEAS_21 (Cooling Water Out)', 'XMV_10 (Cooling Valve)'],
    failureModes: ['IDV(4) Cooling Water Temp Step', 'IDV(11) Cooling Valve Sticking', 'IDV(13) Reaction Kinetics Drift', 'IDV(14) Cyclic Valve Hunting'],
  },
  UNIT_CONDENSER: {
    title: 'Product Heat Exchanger / Condenser',
    description: 'Shell-and-tube heat exchanger cooling reactor effluent vapor (Stream 7) to condense liquid product before the separator.',
    upstream: ['UNIT_REACTOR', 'UNIT_STRIPPER (Recycle Vapor)'],
    downstream: ['UNIT_SEPARATOR'],
    sensors: ['XMEAS_22 (Cooling Water Temp)', 'XMV_11 (Cooling Water Valve)'],
    failureModes: ['IDV(5) Condenser Cooling Water Loss', 'IDV(12) Condenser Valve Sticking'],
  },
  UNIT_SEPARATOR: {
    title: 'High-Pressure Vapor-Liquid Flash Separator',
    description: 'Vertical flash drum that separates condensed liquid underflow (Stream 10) from unreacted overhead vapor (Stream 8).',
    upstream: ['UNIT_CONDENSER'],
    downstream: ['UNIT_COMPRESSOR (Vapor)', 'UNIT_STRIPPER (Liquid)'],
    sensors: ['XMEAS_10 (Purge Gas Flow)', 'XMEAS_11 (Temperature)', 'XMEAS_12 (Level)', 'XMEAS_13 (Pressure)', 'XMEAS_14 (Underflow Rate)'],
    failureModes: ['IDV(9) D Feed Temp Step', 'IDV(10) C Feed Temp Step'],
  },
  UNIT_COMPRESSOR: {
    title: 'Recycle Gas Centrifugal Compressor',
    description: 'Single-stage centrifugal gas compressor that recompresses unreacted vapor overhead from the separator and returns it to the reactor.',
    upstream: ['UNIT_SEPARATOR'],
    downstream: ['UNIT_REACTOR (Recycle Loop)'],
    sensors: ['XMEAS_5 (Recycle Gas Flow)', 'XMEAS_20 (Compressor Work / Motor Power)'],
    failureModes: ['Compressor recycle surge / head loss'],
  },
  UNIT_STRIPPER: {
    title: 'Product Stripping Distillation Column',
    description: 'Stripping column using injected low-pressure steam to remove light dissolved byproducts from liquid product (Stream 11).',
    upstream: ['UNIT_SEPARATOR'],
    downstream: ['UNIT_CONDENSER (Overhead Recycle)', 'Product Storage (Bottoms)'],
    sensors: ['XMEAS_15 (Level)', 'XMEAS_16 (Pressure)', 'XMEAS_17 (Product Flow Rate)', 'XMEAS_18 (Temperature)', 'XMEAS_19 (Steam Flow)'],
    failureModes: ['IDV(18) Stripper Steam Valve Sticking'],
  },
};

const SENSOR_DETAILS = {
  XMEAS_1: { name: 'A Feed Flow', unit: 'kscmh', nominal: '0.25', machine: 'UNIT_FEED', desc: 'Reactant A volumetric flow transmitter' },
  XMEAS_2: { name: 'D Feed Flow', unit: 'kg/h', nominal: '3664', machine: 'UNIT_FEED', desc: 'Reactant D mass flow rate' },
  XMEAS_3: { name: 'E Feed Flow', unit: 'kg/h', nominal: '4795', machine: 'UNIT_FEED', desc: 'Reactant E mass flow rate' },
  XMEAS_4: { name: 'A+C Feed Flow', unit: 'kscmh', nominal: '9.25', machine: 'UNIT_FEED', desc: 'Combined A and C feed stream flow' },
  XMEAS_5: { name: 'Recycle Flow', unit: 'kscmh', nominal: '26.9', machine: 'UNIT_COMPRESSOR', desc: 'Recycle gas flow to reactor' },
  XMEAS_6: { name: 'Reactor Feed Rate', unit: 'kscmh', nominal: '36.5', machine: 'UNIT_REACTOR', desc: 'Total mixed gas feed rate entering reactor' },
  XMEAS_7: { name: 'Reactor Pressure', unit: 'kPa', nominal: '2705', machine: 'UNIT_REACTOR', desc: 'CSTR vessel operating pressure' },
  XMEAS_8: { name: 'Reactor Level', unit: '%', nominal: '65.0', machine: 'UNIT_REACTOR', desc: 'Catalyst & liquid inventory level' },
  XMEAS_9: { name: 'Reactor Temperature', unit: '°C', nominal: '120.4', machine: 'UNIT_REACTOR', desc: 'Primary core reaction temperature' },
  XMEAS_10: { name: 'Purge Gas Rate', unit: 'kscmh', nominal: '0.33', machine: 'UNIT_SEPARATOR', desc: 'Inert gas purge to flare system' },
  XMEAS_11: { name: 'Separator Temperature', unit: '°C', nominal: '80.1', machine: 'UNIT_SEPARATOR', desc: 'Flash drum operating temperature' },
  XMEAS_12: { name: 'Separator Level', unit: '%', nominal: '50.0', machine: 'UNIT_SEPARATOR', desc: 'Liquid condensate level' },
  XMEAS_13: { name: 'Separator Pressure', unit: 'kPa', nominal: '2633', machine: 'UNIT_SEPARATOR', desc: 'Vapor headspace pressure' },
  XMEAS_14: { name: 'Separator Underflow', unit: 'm3/h', nominal: '25.1', machine: 'UNIT_SEPARATOR', desc: 'Condensed liquid flow to stripper column' },
  XMEAS_15: { name: 'Stripper Level', unit: '%', nominal: '50.0', machine: 'UNIT_STRIPPER', desc: 'Bottom sump liquid inventory level' },
  XMEAS_16: { name: 'Stripper Pressure', unit: 'kPa', nominal: '2680', machine: 'UNIT_STRIPPER', desc: 'Stripping column overhead pressure' },
  XMEAS_17: { name: 'Product Flow Rate', unit: 'm3/h', nominal: '22.9', machine: 'UNIT_STRIPPER', desc: 'Final purified product discharge rate' },
  XMEAS_18: { name: 'Stripper Temperature', unit: '°C', nominal: '65.8', machine: 'UNIT_STRIPPER', desc: 'Stripper bottom reboiler temperature' },
  XMEAS_19: { name: 'Stripper Steam Flow', unit: 'kg/h', nominal: '1060', machine: 'UNIT_STRIPPER', desc: 'Heating steam mass flow rate' },
  XMEAS_20: { name: 'Compressor Work', unit: 'kW', nominal: '341', machine: 'UNIT_COMPRESSOR', desc: 'Recycle compressor shaft power consumption' },
  XMEAS_21: { name: 'Reactor Coolant Temp', unit: '°C', nominal: '94.6', machine: 'UNIT_REACTOR', desc: 'Reactor cooling jacket effluent temperature' },
  XMEAS_22: { name: 'Condenser Coolant Temp', unit: '°C', nominal: '77.3', machine: 'UNIT_CONDENSER', desc: 'Condenser cooling water return temperature' },
  XMV_10: { name: 'Reactor Cooling Valve', unit: '%', nominal: '41.1', machine: 'UNIT_REACTOR', desc: 'Reactor cooling water control valve opening' },
  XMV_11: { name: 'Condenser Cooling Valve', unit: '%', nominal: '14.7', machine: 'UNIT_CONDENSER', desc: 'Condenser cooling water control valve opening' },
};

const DEFAULT_BACKUP_NODES = [
  // 6 Equipment Units
  { id: 'UNIT_FEED', name: 'Feed Delivery System', label: 'Unit' },
  { id: 'UNIT_REACTOR', name: 'Chemical Reactor', label: 'Unit' },
  { id: 'UNIT_CONDENSER', name: 'Product Condenser', label: 'Unit' },
  { id: 'UNIT_SEPARATOR', name: 'Vapor-Liquid Separator', label: 'Unit' },
  { id: 'UNIT_COMPRESSOR', name: 'Recycle Compressor', label: 'Unit' },
  { id: 'UNIT_STRIPPER', name: 'Stripper Column', label: 'Unit' },

  // UNIT_FEED sensors
  { id: 'XMEAS_1', name: 'A Feed Flow', label: 'Sensor', tag: 'A_FLOW' },
  { id: 'XMEAS_2', name: 'D Feed Flow', label: 'Sensor', tag: 'D_FLOW' },
  { id: 'XMEAS_3', name: 'E Feed Flow', label: 'Sensor', tag: 'E_FLOW' },
  { id: 'XMEAS_4', name: 'A+C Feed Flow', label: 'Sensor', tag: 'AC_FLOW' },

  // UNIT_REACTOR sensors
  { id: 'XMEAS_6', name: 'Reactor Feed Rate', label: 'Sensor', tag: 'RX_FEED' },
  { id: 'XMEAS_7', name: 'Reactor Pressure', label: 'Sensor', tag: 'RX_PRESS' },
  { id: 'XMEAS_8', name: 'Reactor Level', label: 'Sensor', tag: 'RX_LVL' },
  { id: 'XMEAS_9', name: 'Reactor Temperature', label: 'Sensor', tag: 'RX_TEMP' },
  { id: 'XMEAS_21', name: 'Reactor Coolant Temp', label: 'Sensor', tag: 'RX_CW_OUT' },
  { id: 'XMV_10', name: 'Cooling Valve Pos', label: 'Sensor', tag: 'CW_VALVE' },

  // UNIT_CONDENSER sensors
  { id: 'XMEAS_22', name: 'Condenser Coolant Temp', label: 'Sensor', tag: 'COND_CW' },
  { id: 'XMV_11', name: 'Condenser Valve Pos', label: 'Sensor', tag: 'COND_VALVE' },

  // UNIT_SEPARATOR sensors
  { id: 'XMEAS_10', name: 'Purge Gas Rate', label: 'Sensor', tag: 'PURGE_FLOW' },
  { id: 'XMEAS_11', name: 'Separator Temperature', label: 'Sensor', tag: 'SEP_TEMP' },
  { id: 'XMEAS_12', name: 'Separator Level', label: 'Sensor', tag: 'SEP_LVL' },
  { id: 'XMEAS_13', name: 'Separator Pressure', label: 'Sensor', tag: 'SEP_PRESS' },
  { id: 'XMEAS_14', name: 'Separator Underflow', label: 'Sensor', tag: 'SEP_FLOW' },

  // UNIT_COMPRESSOR sensors
  { id: 'XMEAS_5', name: 'Recycle Flow', label: 'Sensor', tag: 'RECYCLE_FLOW' },
  { id: 'XMEAS_20', name: 'Compressor Work', label: 'Sensor', tag: 'COMP_PWR' },

  // UNIT_STRIPPER sensors
  { id: 'XMEAS_15', name: 'Stripper Level', label: 'Sensor', tag: 'STRIP_LVL' },
  { id: 'XMEAS_16', name: 'Stripper Pressure', label: 'Sensor', tag: 'STRIP_PRESS' },
  { id: 'XMEAS_17', name: 'Product Flow Rate', label: 'Sensor', tag: 'PROD_FLOW' },
  { id: 'XMEAS_18', name: 'Stripper Temperature', label: 'Sensor', tag: 'STRIP_TEMP' },
  { id: 'XMEAS_19', name: 'Stripper Steam Flow', label: 'Sensor', tag: 'STEAM_FLOW' },

  // Failure Modes
  { id: 'IDV_4', name: 'Cooling Water Loss', label: 'FailureMode', code: 'IDV(4)' },
  { id: 'IDV_6', name: 'A Feed Loss', label: 'FailureMode', code: 'IDV(6)' },
  { id: 'IDV_11', name: 'Reactor Valve Sticking', label: 'FailureMode', code: 'IDV(11)' },
];

const DEFAULT_BACKUP_EDGES = [
  // FEEDS
  { id: 'e_feed_rx', source: 'UNIT_FEED', target: 'UNIT_REACTOR', type: 'FEEDS' },
  { id: 'e_rx_cond', source: 'UNIT_REACTOR', target: 'UNIT_CONDENSER', type: 'FEEDS' },
  { id: 'e_cond_sep', source: 'UNIT_CONDENSER', target: 'UNIT_SEPARATOR', type: 'FEEDS' },
  { id: 'e_sep_comp', source: 'UNIT_SEPARATOR', target: 'UNIT_COMPRESSOR', type: 'FEEDS' },
  { id: 'e_comp_rx', source: 'UNIT_COMPRESSOR', target: 'UNIT_REACTOR', type: 'FEEDS' },
  { id: 'e_sep_strip', source: 'UNIT_SEPARATOR', target: 'UNIT_STRIPPER', type: 'FEEDS' },

  // MEASURES
  { id: 'e_s1', source: 'XMEAS_1', target: 'UNIT_FEED', type: 'MEASURES' },
  { id: 'e_s2', source: 'XMEAS_2', target: 'UNIT_FEED', type: 'MEASURES' },
  { id: 'e_s3', source: 'XMEAS_3', target: 'UNIT_FEED', type: 'MEASURES' },
  { id: 'e_s4', source: 'XMEAS_4', target: 'UNIT_FEED', type: 'MEASURES' },

  { id: 'e_s6', source: 'XMEAS_6', target: 'UNIT_REACTOR', type: 'MEASURES' },
  { id: 'e_s7', source: 'XMEAS_7', target: 'UNIT_REACTOR', type: 'MEASURES' },
  { id: 'e_s8', source: 'XMEAS_8', target: 'UNIT_REACTOR', type: 'MEASURES' },
  { id: 'e_s9', source: 'XMEAS_9', target: 'UNIT_REACTOR', type: 'MEASURES' },
  { id: 'e_s21', source: 'XMEAS_21', target: 'UNIT_REACTOR', type: 'MEASURES' },
  { id: 'e_mv10', source: 'XMV_10', target: 'UNIT_REACTOR', type: 'MEASURES' },

  { id: 'e_s22', source: 'XMEAS_22', target: 'UNIT_CONDENSER', type: 'MEASURES' },
  { id: 'e_mv11', source: 'XMV_11', target: 'UNIT_CONDENSER', type: 'MEASURES' },

  { id: 'e_s10', source: 'XMEAS_10', target: 'UNIT_SEPARATOR', type: 'MEASURES' },
  { id: 'e_s11', source: 'XMEAS_11', target: 'UNIT_SEPARATOR', type: 'MEASURES' },
  { id: 'e_s12', source: 'XMEAS_12', target: 'UNIT_SEPARATOR', type: 'MEASURES' },
  { id: 'e_s13', source: 'XMEAS_13', target: 'UNIT_SEPARATOR', type: 'MEASURES' },
  { id: 'e_s14', source: 'XMEAS_14', target: 'UNIT_SEPARATOR', type: 'MEASURES' },

  { id: 'e_s5', source: 'XMEAS_5', target: 'UNIT_COMPRESSOR', type: 'MEASURES' },
  { id: 'e_s20', source: 'XMEAS_20', target: 'UNIT_COMPRESSOR', type: 'MEASURES' },

  { id: 'e_s15', source: 'XMEAS_15', target: 'UNIT_STRIPPER', type: 'MEASURES' },
  { id: 'e_s16', source: 'XMEAS_16', target: 'UNIT_STRIPPER', type: 'MEASURES' },
  { id: 'e_s17', source: 'XMEAS_17', target: 'UNIT_STRIPPER', type: 'MEASURES' },
  { id: 'e_s18', source: 'XMEAS_18', target: 'UNIT_STRIPPER', type: 'MEASURES' },
  { id: 'e_s19', source: 'XMEAS_19', target: 'UNIT_STRIPPER', type: 'MEASURES' },

  // SUSCEPTIBLE_TO
  { id: 'e_f4', source: 'UNIT_REACTOR', target: 'IDV_4', type: 'SUSCEPTIBLE_TO' },
  { id: 'e_f6', source: 'UNIT_FEED', target: 'IDV_6', type: 'SUSCEPTIBLE_TO' },
  { id: 'e_f11', source: 'UNIT_REACTOR', target: 'IDV_11', type: 'SUSCEPTIBLE_TO' },
];

export default function KnowledgeGraphPage() {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'units', 'sensors', 'failures'

  useEffect(() => {
    if (!containerRef.current) return;
    let isMounted = true;

    async function loadGraph() {
      let elements = [];
      try {
        const data = await fetchGraphTopology();
        const rawNodes = (data && data.nodes && data.nodes.length > 0) ? data.nodes : DEFAULT_BACKUP_NODES;
        const rawEdges = (data && data.edges && data.edges.length > 0) ? data.edges : DEFAULT_BACKUP_EDGES;

        const nodes = rawNodes.map((n) => {
          const pos = PRESET_POSITIONS[n.id] || {
            x: 150 + Math.random() * 800,
            y: 150 + Math.random() * 300,
          };
          return {
            group: 'nodes',
            data: {
              id: n.id,
              label: n.name || n.id,
              type: n.label || 'Unit',
              code: n.code || '',
              tag: n.tag || '',
              description: n.description || '',
            },
            position: pos,
          };
        });

        const nodeIds = new Set(nodes.map((n) => n.data.id));

        const validEdges = rawEdges
          .filter((e) => e && e.source && e.target && nodeIds.has(e.source) && nodeIds.has(e.target))
          .map((e, idx) => ({
            group: 'edges',
            data: {
              id: e.id || `edge_${idx}`,
              source: e.source,
              target: e.target,
              type: e.type || 'FEEDS',
              label: e.type || 'FEEDS',
            },
          }));

        elements = [...nodes, ...validEdges];
      } catch (err) {
        console.warn('Using default Cytoscape dataset:', err);
        const nodes = DEFAULT_BACKUP_NODES.map((n) => ({
          group: 'nodes',
          data: {
            id: n.id,
            label: n.name || n.id,
            type: n.label,
            code: n.code || '',
            tag: n.tag || '',
          },
          position: PRESET_POSITIONS[n.id] || { x: 200, y: 200 },
        }));
        const nodeIds = new Set(nodes.map((n) => n.data.id));
        const validEdges = DEFAULT_BACKUP_EDGES
          .filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target))
          .map((e) => ({
            group: 'edges',
            data: e,
          }));
        elements = [...nodes, ...validEdges];
      }

      if (!isMounted || !containerRef.current) return;

      const cy = cytoscape({
        container: containerRef.current,
        elements: elements,
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
              'text-max-width': '90px',
              'width': '85px',
              'height': '44px',
              'shape': 'roundrectangle',
              'border-width': 1.5,
              'border-color': '#475569',
              'transition-property': 'background-color, border-color, border-width, width, height, shadow-blur',
              'transition-duration': '0.25s',
            },
          },
          // Unit Nodes (Process Machines)
          {
            selector: 'node[type = "Unit"]',
            style: {
              'background-color': '#0f172a',
              'border-color': '#6366f1',
              'border-width': 2.5,
              'width': '105px',
              'height': '48px',
              'font-size': '12px',
              'font-weight': 700,
              'color': '#ffffff',
            },
          },
          // Sensor Nodes
          {
            selector: 'node[type = "Sensor"]',
            style: {
              'background-color': '#082f49',
              'border-color': '#0284c7',
              'border-width': 1.5,
              'shape': 'ellipse',
              'width': '48px',
              'height': '48px',
              'font-size': '9px',
              'color': '#e0f2fe',
            },
          },
          // Failure Mode Nodes
          {
            selector: 'node[type = "FailureMode"]',
            style: {
              'background-color': '#450a0a',
              'border-color': '#dc2626',
              'border-width': 2,
              'shape': 'diamond',
              'width': '52px',
              'height': '52px',
              'font-size': '9px',
              'color': '#fecaca',
            },
          },
          // Selected / Active Node
          {
            selector: 'node:selected',
            style: {
              'border-color': '#22d3ee',
              'border-width': 3.5,
              'shadow-blur': 25,
              'shadow-color': '#22d3ee',
              'shadow-opacity': 0.9,
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
          // FEEDS Process Piping Edges
          {
            selector: 'edge[type = "FEEDS"]',
            style: {
              'width': 3,
              'line-color': '#6366f1',
              'target-arrow-color': '#6366f1',
              'arrow-scale': 1.3,
            },
          },
          // Recycle Loop Edges
          {
            selector: 'edge[source = "UNIT_COMPRESSOR"][target = "UNIT_REACTOR"]',
            style: {
              'line-color': '#06b6d4',
              'target-arrow-color': '#06b6d4',
              'width': 3.5,
              'line-style': 'dashed',
            },
          },
          // MEASURES Sensor Edges
          {
            selector: 'edge[type = "MEASURES"]',
            style: {
              'width': 1.5,
              'line-color': '#0284c7',
              'target-arrow-color': '#0284c7',
              'line-style': 'dotted',
              'opacity': 0.75,
            },
          },
          // SUSCEPTIBLE_TO Failure Edges
          {
            selector: 'edge[type = "SUSCEPTIBLE_TO"]',
            style: {
              'width': 1.5,
              'line-color': '#dc2626',
              'target-arrow-color': '#dc2626',
              'line-style': 'dashed',
              'opacity': 0.7,
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

      cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        setSelectedNode(node.data());
      });

      cy.on('tap', (evt) => {
        if (evt.target === cy) {
          setSelectedNode(null);
        }
      });

      cyRef.current = cy;
      cy.fit(undefined, 35);
      setTimeout(() => {
        if (cy && !cy.destroyed()) {
          cy.fit(undefined, 35);
        }
      }, 80);
    }

    loadGraph();

    return () => {
      isMounted = false;
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, []);

  // Filter Nodes by Type
  const handleFilterChange = (type) => {
    setFilterType(type);
    const cy = cyRef.current;
    if (!cy) return;

    cy.nodes().style('display', 'element');
    cy.edges().style('display', 'element');

    if (type === 'units') {
      cy.$('node[type != "Unit"]').style('display', 'none');
      cy.$('edge[type != "FEEDS"]').style('display', 'none');
    } else if (type === 'sensors') {
      cy.$('node[type = "FailureMode"]').style('display', 'none');
      cy.$('edge[type = "SUSCEPTIBLE_TO"]').style('display', 'none');
    } else if (type === 'failures') {
      cy.$('node[type = "Sensor"]').style('display', 'none');
      cy.$('edge[type = "MEASURES"]').style('display', 'none');
    }

    cy.fit(undefined, 35);
  };

  // Search Node and Zoom
  const handleSearch = (e) => {
    e.preventDefault();
    const query = searchQuery.trim().toUpperCase();
    if (!query || !cyRef.current) return;

    const cy = cyRef.current;
    const targetNode = cy.nodes().filter((n) => {
      const id = n.data('id').toUpperCase();
      const label = (n.data('label') || '').toUpperCase();
      const tag = (n.data('tag') || '').toUpperCase();
      return id.includes(query) || label.includes(query) || tag.includes(query);
    });

    if (targetNode.length > 0) {
      cy.nodes().unselect();
      targetNode.first().select();
      setSelectedNode(targetNode.first().data());
      cy.animate({
        center: { eles: targetNode.first() },
        zoom: 1.4,
        duration: 500,
      });
    }
  };

  const handleResetView = () => {
    const cy = cyRef.current;
    if (cy) {
      cy.nodes().unselect();
      setSelectedNode(null);
      setSearchQuery('');
      setFilterType('all');
      cy.nodes().style('display', 'element');
      cy.edges().style('display', 'element');
      cy.fit(undefined, 35);
    }
  };

  // Dynamically scale spacing between all machines and entities outward or inward
  const handleScaleSpacing = (factor) => {
    const cy = cyRef.current;
    if (!cy) return;
    const nodes = cy.nodes();
    const bb = nodes.boundingBox();
    const cx = (bb.x1 + bb.x2) / 2;
    const cy_center = (bb.y1 + bb.y2) / 2;

    nodes.forEach((node) => {
      const pos = node.position();
      const nx = cx + (pos.x - cx) * factor;
      const ny = cy_center + (pos.y - cy_center) * factor;
      node.animate({
        position: { x: nx, y: ny },
        duration: 350,
      });
    });

    setTimeout(() => {
      if (cy && !cy.destroyed()) {
        cy.fit(undefined, 40);
      }
    }, 400);
  };

  // Run dynamic physics layout that automatically pushes all nodes into non-overlapping zones
  const handleRunCoSE = () => {
    const cy = cyRef.current;
    if (!cy) return;
    const layout = cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 750,
      nodeRepulsion: 22000000,
      idealEdgeLength: 170,
      edgeElasticity: 70,
      gravity: 0.08,
      numIter: 1000,
      componentSpacing: 300,
      nodeOverlap: 40,
      padding: 60,
    });
    layout.run();
  };

  // Reset to wide spaced flowsheet layout
  const handleResetFlowsheet = () => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().forEach((node) => {
      const id = node.data('id');
      const targetPos = PRESET_POSITIONS[id];
      if (targetPos) {
        node.animate({
          position: targetPos,
          duration: 400,
        });
      }
    });
    setTimeout(() => {
      if (cy && !cy.destroyed()) {
        cy.fit(undefined, 40);
      }
    }, 450);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
      {/* Top Banner and Knowledge Graph Stats */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Network size={26} color="var(--accent-primary)" />
              <h1 style={{ fontSize: '1.45rem', fontWeight: 700, color: '#fff' }}>
                Plant Knowledge Graph Explorer
              </h1>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Complete topological ontology of the Tennessee Eastman Process (TEP): Physical Units, Instrumentation Sensors, and Failure Modes.
            </p>
          </div>

          {/* Quick Metrics Badges */}
          <div style={{ display: 'flex', gap: '0.85rem', flexWrap: 'wrap' }}>
            <div className="status-pill normal" style={{ background: 'rgba(99, 102, 241, 0.15)', borderColor: '#6366f1', color: '#a5b4fc' }}>
              <Cpu size={14} /> 6 Chemical Units
            </div>
            <div className="status-pill normal" style={{ background: 'rgba(2, 132, 199, 0.15)', borderColor: '#0284c7', color: '#38bdf8' }}>
              <Activity size={14} /> 22 Primary Sensors
            </div>
            <div className="status-pill normal" style={{ background: 'rgba(225, 29, 72, 0.15)', borderColor: '#e11d48', color: '#fb7185' }}>
              <AlertTriangle size={14} /> 18 TEP Fault Modes
            </div>
          </div>
        </div>

        {/* Toolbar: Filters, Spacing Controls, Search Bar, Zoom */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '1.25rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-subtle)',
            flexWrap: 'wrap',
            gap: '0.85rem',
          }}
        >
          {/* Filters */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Filter size={13} /> View:
            </span>
            <button
              className={filterType === 'all' ? 'btn-primary' : 'btn-outline'}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={() => handleFilterChange('all')}
            >
              All Entities
            </button>
            <button
              className={filterType === 'units' ? 'btn-primary' : 'btn-outline'}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={() => handleFilterChange('units')}
            >
              Machines Only
            </button>
            <button
              className={filterType === 'sensors' ? 'btn-primary' : 'btn-outline'}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={() => handleFilterChange('sensors')}
            >
              Sensors + Units
            </button>
            <button
              className={filterType === 'failures' ? 'btn-primary' : 'btn-outline'}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
              onClick={() => handleFilterChange('failures')}
            >
              Failure Modes
            </button>
          </div>

          {/* Node Spacing & Layout Buttons */}
          <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Layers size={13} /> Spacing:
            </span>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
              onClick={() => handleScaleSpacing(1.25)}
              title="Increase space between all machines and entities"
            >
              + Spread Out
            </button>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
              onClick={() => handleScaleSpacing(0.8)}
              title="Decrease space between all entities"
            >
              - Compact
            </button>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem', color: 'var(--accent-cyan)' }}
              onClick={handleRunCoSE}
              title="Organic physics layout separating all entities"
            >
              Auto Physics
            </button>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
              onClick={handleResetFlowsheet}
              title="Reset to wide-spaced chemical flowsheet layout"
            >
              Wide Flowsheet
            </button>
          </div>

          {/* Search Box & Controls */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
              <input
                type="text"
                placeholder="Search sensor (e.g. XMEAS_9)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '0.35rem 2rem 0.35rem 0.75rem',
                  color: '#fff',
                  fontSize: '0.82rem',
                  outline: 'none',
                  width: '210px',
                }}
              />
              <button
                type="submit"
                style={{
                  position: 'absolute',
                  right: '6px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                }}
              >
                <Search size={14} />
              </button>
            </form>

            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.6rem' }}
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
              title="Zoom In"
            >
              <ZoomIn size={14} />
            </button>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.6rem' }}
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
              title="Zoom Out"
            >
              <ZoomOut size={14} />
            </button>
            <button
              className="btn-outline"
              style={{ padding: '0.35rem 0.6rem' }}
              onClick={handleResetView}
              title="Reset View"
            >
              <Maximize2 size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Graph Canvas and Inspector Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedNode ? '1fr 340px' : '1fr', gap: '1.25rem' }}>
        {/* Graph Canvas */}
        <div
          className="glass-panel"
          style={{
            position: 'relative',
            height: '700px',
            overflow: 'hidden',
            padding: '0.5rem',
            background: 'rgba(8, 11, 18, 0.85)',
          }}
        >
          <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

          {/* Canvas Floating Legend */}
          <div
            style={{
              position: 'absolute',
              bottom: '16px',
              left: '16px',
              background: 'rgba(15, 23, 42, 0.92)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '0.55rem 0.9rem',
              backdropFilter: 'blur(8px)',
              display: 'flex',
              gap: '1.2rem',
              fontSize: '0.76rem',
              color: '#cbd5e1',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#0f172a', border: '2px solid #6366f1' }}></span>
              Equipment Unit
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '11px', height: '11px', borderRadius: '50%', background: '#082f49', border: '1.5px solid #0284c7' }}></span>
              Process Sensor
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '11px', height: '11px', transform: 'rotate(45deg)', background: '#450a0a', border: '1.5px solid #dc2626' }}></span>
              Failure Mode
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '16px', height: '2px', background: '#06b6d4' }}></span>
              Recycle Loop
            </span>
          </div>
        </div>

        {/* Selected Entity Inspector Sidebar */}
        {selectedNode && (
          <div className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '620px', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
              <div>
                <span
                  style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    fontWeight: 700,
                    letterSpacing: '0.05em',
                    color: selectedNode.type === 'Unit' ? '#a5b4fc' : selectedNode.type === 'Sensor' ? '#38bdf8' : '#f87171',
                  }}
                >
                  {selectedNode.type} Entity
                </span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginTop: '0.2rem' }}>
                  {selectedNode.label || selectedNode.id}
                </h3>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  ID: <code style={{ color: 'var(--accent-cyan)' }}>{selectedNode.id}</code>
                </div>
              </div>
              <button
                className="btn-outline"
                style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                onClick={() => setSelectedNode(null)}
              >
                ✕
              </button>
            </div>

            {/* Entity Specific Information */}
            {selectedNode.type === 'Unit' && UNIT_DETAILS[selectedNode.id] && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem', fontSize: '0.82rem' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Official Unit Title</div>
                  <div style={{ color: '#cbd5e1', marginTop: '0.15rem' }}>{UNIT_DETAILS[selectedNode.id].title}</div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Process Function</div>
                  <div style={{ color: '#94a3b8', lineHeight: 1.4, marginTop: '0.2rem' }}>
                    {UNIT_DETAILS[selectedNode.id].description}
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Physical Piping Connections</div>
                  <div style={{ marginTop: '0.3rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                    <div style={{ color: '#94a3b8' }}>
                      <strong style={{ color: '#38bdf8' }}>Upstream:</strong> {UNIT_DETAILS[selectedNode.id].upstream.join(', ')}
                    </div>
                    <div style={{ color: '#94a3b8' }}>
                      <strong style={{ color: '#a5b4fc' }}>Downstream:</strong> {UNIT_DETAILS[selectedNode.id].downstream.join(', ')}
                    </div>
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Associated Sensors ({UNIT_DETAILS[selectedNode.id].sensors.length})</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.3rem' }}>
                    {UNIT_DETAILS[selectedNode.id].sensors.map((s, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'rgba(15, 23, 42, 0.7)',
                          padding: '0.35rem 0.6rem',
                          borderRadius: '5px',
                          border: '1px solid rgba(2, 132, 199, 0.3)',
                          color: '#e0f2fe',
                          fontSize: '0.78rem',
                        }}
                      >
                        {s}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Known Process Faults</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.3rem' }}>
                    {UNIT_DETAILS[selectedNode.id].failureModes.map((f, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: 'rgba(69, 10, 10, 0.4)',
                          padding: '0.35rem 0.6rem',
                          borderRadius: '5px',
                          border: '1px solid rgba(225, 29, 72, 0.3)',
                          color: '#fecaca',
                          fontSize: '0.78rem',
                        }}
                      >
                        {f}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {selectedNode.type === 'Sensor' && SENSOR_DETAILS[selectedNode.id] && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem', fontSize: '0.82rem' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Sensor Instrument Name</div>
                  <div style={{ color: '#38bdf8', marginTop: '0.15rem', fontWeight: 600 }}>
                    {SENSOR_DETAILS[selectedNode.id].name}
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Parent Equipment Unit</div>
                  <div style={{ color: '#a5b4fc', marginTop: '0.15rem' }}>
                    {SENSOR_DETAILS[selectedNode.id].machine}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.5rem', borderRadius: '6px' }}>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Engineering Unit</div>
                    <div style={{ color: '#fff', fontWeight: 700, marginTop: '0.1rem' }}>
                      {SENSOR_DETAILS[selectedNode.id].unit}
                    </div>
                  </div>
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.5rem', borderRadius: '6px' }}>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Baseline Nominal</div>
                    <div style={{ color: '#34d399', fontWeight: 700, marginTop: '0.1rem' }}>
                      {SENSOR_DETAILS[selectedNode.id].nominal} {SENSOR_DETAILS[selectedNode.id].unit}
                    </div>
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Telemetry Role</div>
                  <div style={{ color: '#cbd5e1', lineHeight: 1.4, marginTop: '0.2rem' }}>
                    {SENSOR_DETAILS[selectedNode.id].desc}
                  </div>
                </div>
              </div>
            )}

            {selectedNode.type === 'FailureMode' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem', fontSize: '0.82rem' }}>
                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Disturbance Code</div>
                  <div style={{ color: '#f87171', fontWeight: 700, fontSize: '0.95rem' }}>
                    {selectedNode.code || selectedNode.id}
                  </div>
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: '#fff' }}>Disturbance Description</div>
                  <div style={{ color: '#cbd5e1', lineHeight: 1.4, marginTop: '0.2rem' }}>
                    {selectedNode.description || selectedNode.label}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
