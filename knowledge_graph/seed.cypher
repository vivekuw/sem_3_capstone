// ==============================================================================
// Plant Topology and Sensor Instrumentation Seed Data
// Process Flow: P-100 (Pump) -> V-101 (Valve) -> HX-102 (HeatExchanger) -> R-103 (Reactor)
// All statements use MERGE to ensure idempotency when executed multiple times.
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Equipment Nodes
// ------------------------------------------------------------------------------
MERGE (e1:Equipment {id: 'P-100'})
ON CREATE SET e1.name = 'Feed Pump', e1.type = 'Pump';

MERGE (e2:Equipment {id: 'V-101'})
ON CREATE SET e2.name = 'Control Valve', e2.type = 'Valve';

MERGE (e3:Equipment {id: 'HX-102'})
ON CREATE SET e3.name = 'Preheater Heat Exchanger', e3.type = 'HeatExchanger';

MERGE (e4:Equipment {id: 'R-103'})
ON CREATE SET e4.name = 'Chemical Reactor', e4.type = 'Reactor';

// ------------------------------------------------------------------------------
// 2. Flow Relationships (Equipment)-[:FEEDS]->(Equipment)
// ------------------------------------------------------------------------------
MATCH (p:Equipment {id: 'P-100'}), (v:Equipment {id: 'V-101'})
MERGE (p)-[:FEEDS]->(v);

MATCH (v:Equipment {id: 'V-101'}), (hx:Equipment {id: 'HX-102'})
MERGE (v)-[:FEEDS]->(hx);

MATCH (hx:Equipment {id: 'HX-102'}), (r:Equipment {id: 'R-103'})
MERGE (hx)-[:FEEDS]->(r);

// ------------------------------------------------------------------------------
// 3. Sensor Nodes and (Sensor)-[:MEASURES]->(Equipment)
// ------------------------------------------------------------------------------

// P-100 Sensors
MERGE (s:Sensor {name: 'P100_flow', equipment_id: 'P-100'})
ON CREATE SET s.unit = 'm3/h', s.description = 'Discharge Flow Rate'
WITH s
MATCH (e:Equipment {id: 'P-100'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'P100_pressure', equipment_id: 'P-100'})
ON CREATE SET s.unit = 'bar', s.description = 'Discharge Pressure'
WITH s
MATCH (e:Equipment {id: 'P-100'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'P100_power', equipment_id: 'P-100'})
ON CREATE SET s.unit = 'kW', s.description = 'Motor Power'
WITH s
MATCH (e:Equipment {id: 'P-100'})
MERGE (s)-[:MEASURES]->(e);

// V-101 Sensors
MERGE (s:Sensor {name: 'V101_pos', equipment_id: 'V-101'})
ON CREATE SET s.unit = '%', s.description = 'Valve Stem Position'
WITH s
MATCH (e:Equipment {id: 'V-101'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'V101_flow', equipment_id: 'V-101'})
ON CREATE SET s.unit = 'm3/h', s.description = 'Throughput Flow Rate'
WITH s
MATCH (e:Equipment {id: 'V-101'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'V101_dp', equipment_id: 'V-101'})
ON CREATE SET s.unit = 'bar', s.description = 'Differential Pressure'
WITH s
MATCH (e:Equipment {id: 'V-101'})
MERGE (s)-[:MEASURES]->(e);

// HX-102 Sensors
MERGE (s:Sensor {name: 'HX102_temp_in', equipment_id: 'HX-102'})
ON CREATE SET s.unit = '°C', s.description = 'Inlet Temperature'
WITH s
MATCH (e:Equipment {id: 'HX-102'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'HX102_temp_out', equipment_id: 'HX-102'})
ON CREATE SET s.unit = '°C', s.description = 'Outlet Temperature'
WITH s
MATCH (e:Equipment {id: 'HX-102'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'HX102_coolant_flow', equipment_id: 'HX-102'})
ON CREATE SET s.unit = 'kg/h', s.description = 'Coolant Flow Rate'
WITH s
MATCH (e:Equipment {id: 'HX-102'})
MERGE (s)-[:MEASURES]->(e);

// R-103 Sensors
MERGE (s:Sensor {name: 'R103_temp', equipment_id: 'R-103'})
ON CREATE SET s.unit = '°C', s.description = 'Reactor Internal Temperature'
WITH s
MATCH (e:Equipment {id: 'R-103'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'R103_pressure', equipment_id: 'R-103'})
ON CREATE SET s.unit = 'kPa', s.description = 'Reactor Vessel Pressure'
WITH s
MATCH (e:Equipment {id: 'R-103'})
MERGE (s)-[:MEASURES]->(e);

MERGE (s:Sensor {name: 'R103_level', equipment_id: 'R-103'})
ON CREATE SET s.unit = '%', s.description = 'Liquid Holdup Level'
WITH s
MATCH (e:Equipment {id: 'R-103'})
MERGE (s)-[:MEASURES]->(e);
