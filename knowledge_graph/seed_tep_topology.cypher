// ==============================================================================
// Tennessee Eastman Process (TEP) - Knowledge Graph Seed
// Nodes: Unit, Sensor, FailureMode
// Relationships:
//   - (Unit)-[:FEEDS]->(Unit)
//   - (Sensor)-[:MEASURES]->(Unit)
//   - (Unit)-[:SUSCEPTIBLE_TO]->(FailureMode)
//   - (FailureMode)-[:TYPICALLY_CAUSES]->(FailureMode)
//   - (FailureMode)-[:MANIFESTS_IN]->(Sensor)
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. Physical Processing Units
// ------------------------------------------------------------------------------
MERGE (u_feed:Unit {id: 'UNIT_FEED', name: 'Feed Delivery System', description: 'Raw materials manifold delivering streams A, D, E, and C'});
MERGE (u_reac:Unit {id: 'UNIT_REACTOR', name: 'Chemical Reactor', description: 'Continuous stirred-tank exothermic reactor producing liquid products G and H'});
MERGE (u_cond:Unit {id: 'UNIT_CONDENSER', name: 'Partial Condenser', description: 'Cools reactor effluent stream converting condensable vapors into liquid'});
MERGE (u_sep:Unit {id: 'UNIT_SEPARATOR', name: 'Vapor-Liquid Separator', description: 'Flash vessel separating non-condensed vapor from liquid product mix'});
MERGE (u_comp:Unit {id: 'UNIT_COMPRESSOR', name: 'Recycle Compressor', description: 'Centrifugal compressor returning non-condensed vapor back to reactor'});
MERGE (u_strip:Unit {id: 'UNIT_STRIPPER', name: 'Product Stripper', description: 'Stripping column removing unreacted volatile components from product stream'});
MERGE (u_prod:Unit {id: 'UNIT_PRODUCT', name: 'Product Storage', description: 'Final staging tanks receiving purified streams of components G and H'});

// ------------------------------------------------------------------------------
// 2. Process Sensors & Instrumentation
// ------------------------------------------------------------------------------
MERGE (s1:Sensor {id: 'XMEAS_1', tag: 'A_FEED_FLOW', variable_name: 'Stream 1 (A feed)', unit: 'kscmh', normal_min: 0.20, normal_max: 0.30, normal_mean: 0.25});
MERGE (s2:Sensor {id: 'XMEAS_2', tag: 'D_FEED_FLOW', variable_name: 'Stream 2 (D feed)', unit: 'kg/h', normal_min: 3600.0, normal_max: 3750.0, normal_mean: 3664.0});
MERGE (s3:Sensor {id: 'XMEAS_3', tag: 'E_FEED_FLOW', variable_name: 'Stream 3 (E feed)', unit: 'kg/h', normal_min: 4400.0, normal_max: 4600.0, normal_mean: 4505.0});
MERGE (s4:Sensor {id: 'XMEAS_4', tag: 'A_C_FEED_FLOW', variable_name: 'Stream 4 (A/C feed)', unit: 'kscmh', normal_min: 8.5, normal_max: 9.8, normal_mean: 9.34});

MERGE (s6:Sensor {id: 'XMEAS_6', tag: 'REACTOR_FEED_RATE', variable_name: 'Reactor Feed Rate', unit: 'kscmh', normal_min: 40.0, normal_max: 44.0, normal_mean: 42.3});
MERGE (s7:Sensor {id: 'XMEAS_7', tag: 'REACTOR_PRESSURE', variable_name: 'Reactor Pressure', unit: 'kPa gauge', normal_min: 2650.0, normal_max: 2750.0, normal_mean: 2705.0});
MERGE (s8:Sensor {id: 'XMEAS_8', tag: 'REACTOR_LEVEL', variable_name: 'Reactor Liquid Level', unit: '%', normal_min: 60.0, normal_max: 75.0, normal_mean: 65.2});
MERGE (s9:Sensor {id: 'XMEAS_9', tag: 'REACTOR_TEMP', variable_name: 'Reactor Temperature', unit: 'Deg C', normal_min: 118.0, normal_max: 124.0, normal_mean: 120.4});
MERGE (s21:Sensor {id: 'XMEAS_21', tag: 'REAC_COOL_TEMP', variable_name: 'Reactor Cooling Water Outlet Temp', unit: 'Deg C', normal_min: 92.0, normal_max: 98.0, normal_mean: 94.4});

MERGE (s22:Sensor {id: 'XMEAS_22', tag: 'COND_COOL_TEMP', variable_name: 'Condenser Cooling Water Outlet Temp', unit: 'Deg C', normal_min: 75.0, normal_max: 82.0, normal_mean: 77.2});

MERGE (s10:Sensor {id: 'XMEAS_10', tag: 'PURGE_RATE', variable_name: 'Purge Gas Rate', unit: 'kscmh', normal_min: 0.30, normal_max: 0.40, normal_mean: 0.337});
MERGE (s11:Sensor {id: 'XMEAS_11', tag: 'SEP_TEMP', variable_name: 'Separator Temperature', unit: 'Deg C', normal_min: 78.0, normal_max: 84.0, normal_mean: 80.1});
MERGE (s12:Sensor {id: 'XMEAS_12', tag: 'SEP_LEVEL', variable_name: 'Separator Liquid Level', unit: '%', normal_min: 45.0, normal_max: 55.0, normal_mean: 50.0});
MERGE (s13:Sensor {id: 'XMEAS_13', tag: 'SEP_PRESSURE', variable_name: 'Separator Pressure', unit: 'kPa gauge', normal_min: 2600.0, normal_max: 2700.0, normal_mean: 2633.0});
MERGE (s14:Sensor {id: 'XMEAS_14', tag: 'SEP_UNDERFLOW', variable_name: 'Separator Underflow Flow', unit: 'm3/h', normal_min: 23.0, normal_max: 28.0, normal_mean: 25.1});

MERGE (s5:Sensor {id: 'XMEAS_5', tag: 'RECYCLE_FLOW', variable_name: 'Recycle Flow Rate', unit: 'kscmh', normal_min: 25.0, normal_max: 29.0, normal_mean: 26.9});
MERGE (s20:Sensor {id: 'XMEAS_20', tag: 'COMP_WORK', variable_name: 'Compressor Power Work', unit: 'kW', normal_min: 320.0, normal_max: 360.0, normal_mean: 341.0});

MERGE (s15:Sensor {id: 'XMEAS_15', tag: 'STRIP_LEVEL', variable_name: 'Stripper Liquid Level', unit: '%', normal_min: 45.0, normal_max: 55.0, normal_mean: 50.0});
MERGE (s16:Sensor {id: 'XMEAS_16', tag: 'STRIP_PRESSURE', variable_name: 'Stripper Pressure', unit: 'kPa gauge', normal_min: 2950.0, normal_max: 3100.0, normal_mean: 3010.0});
MERGE (s17:Sensor {id: 'XMEAS_17', tag: 'STRIP_UNDERFLOW', variable_name: 'Stripper Underflow Flow', unit: 'm3/h', normal_min: 20.0, normal_max: 25.0, normal_mean: 22.9});
MERGE (s18:Sensor {id: 'XMEAS_18', tag: 'STRIP_TEMP', variable_name: 'Stripper Temperature', unit: 'Deg C', normal_min: 63.0, normal_max: 68.0, normal_mean: 65.7});
MERGE (s19:Sensor {id: 'XMEAS_19', tag: 'STRIP_STEAM', variable_name: 'Stripper Steam Flow', unit: 'kg/h', normal_min: 1000.0, normal_max: 1200.0, normal_mean: 1085.0});

MERGE (s23:Sensor {id: 'XMEAS_23', tag: 'PROD_COMP_G', variable_name: 'Stream 11 Component G', unit: 'mol %', normal_min: 45.0, normal_max: 55.0, normal_mean: 53.8});
MERGE (s24:Sensor {id: 'XMEAS_24', tag: 'PROD_COMP_H', variable_name: 'Stream 11 Component H', unit: 'mol %', normal_min: 30.0, normal_max: 40.0, normal_mean: 38.2});

// ------------------------------------------------------------------------------
// 3. Labeled Process Disturbance Modes (:FailureMode)
// All 21 standard Tennessee Eastman Process Benchmark Faults (IDV 1 - 21)
// ------------------------------------------------------------------------------
MERGE (f1:FailureMode {id: 'IDV_1', code: 'IDV(1)', name: 'A/C Feed Ratio Step Change', category: 'Feed Disturbance', severity: 'Medium', description: 'Step change in Stream 4 A/C feed ratio shifts reactor stoichiometry.'});
MERGE (f2:FailureMode {id: 'IDV_2', code: 'IDV(2)', name: 'B Composition Step Change', category: 'Feed Disturbance', severity: 'Medium', description: 'Step change in Stream 4 B composition altering product distribution.'});
MERGE (f3:FailureMode {id: 'IDV_3', code: 'IDV(3)', name: 'D Feed Temperature Step Change', category: 'Feed Thermal Disturbance', severity: 'Low', description: 'Step increase in Stream 2 reactant D temperature.'});
MERGE (f4:FailureMode {id: 'IDV_4', code: 'IDV(4)', name: 'Reactor Cooling Water Inlet Temp Step Increase', category: 'Cooling Disturbance', severity: 'High', description: 'Cooling water enters warmer than design, reducing reactor cooling capacity.'});
MERGE (f5:FailureMode {id: 'IDV_5', code: 'IDV(5)', name: 'Condenser Cooling Water Inlet Temp Step Increase', category: 'Cooling Disturbance', severity: 'Medium', description: 'Warm cooling water supply to condenser impairs vapor condensation rate.'});
MERGE (f6:FailureMode {id: 'IDV_6', code: 'IDV(6)', name: 'A Feed Loss', category: 'Feed Loss', severity: 'Critical', description: 'Complete cut of reactant A supply line (Stream 1).'});
MERGE (f7:FailureMode {id: 'IDV_7', code: 'IDV(7)', name: 'C Header Pressure Loss', category: 'Feed Pressure Loss', severity: 'High', description: 'Upstream supply header pressure reduction on reactant C.'});
MERGE (f8:FailureMode {id: 'IDV_8', code: 'IDV(8)', name: 'A/B/C Feed Composition Random Variation', category: 'Composition Noise', severity: 'Low', description: 'Uncorrelated compositional stochastic noise in stream 4 feeds.'});
MERGE (f9:FailureMode {id: 'IDV_9', code: 'IDV(9)', name: 'D Feed Temp Random Variation', category: 'Thermal Noise', severity: 'Low', description: 'Fluctuating reactant D inlet temperature.'});
MERGE (f10:FailureMode {id: 'IDV_10', code: 'IDV(10)', name: 'C Feed Temp Random Variation', category: 'Thermal Noise', severity: 'Low', description: 'Fluctuating reactant C inlet temperature.'});
MERGE (f11:FailureMode {id: 'IDV_11', code: 'IDV(11)', name: 'Reactor Cooling Water Valve Sticking', category: 'Actuator Mechanical Failure', severity: 'High', description: 'Cooling water control valve sticks intermittently, causing temperature oscillations.'});
MERGE (f12:FailureMode {id: 'IDV_12', code: 'IDV(12)', name: 'Condenser Cooling Water Valve Sticking', category: 'Actuator Mechanical Failure', severity: 'Medium', description: 'Condenser coolant control valve sticks causing pressure/level cycling.'});
MERGE (f13:FailureMode {id: 'IDV_13', code: 'IDV(13)', name: 'Reaction Kinetics Drift', category: 'Catalyst/Kinetic Drift', severity: 'Medium', description: 'Gradual catalyst degradation or activation energy drift altering yield.'});
MERGE (f14:FailureMode {id: 'IDV_14', code: 'IDV(14)', name: 'Reactor Cooling Water Valve Stuck Open', category: 'Actuator Failure', severity: 'High', description: 'Cooling valve stuck in open position chilling the reactor bed.'});
MERGE (f15:FailureMode {id: 'IDV_15', code: 'IDV(15)', name: 'Condenser Cooling Water Valve Stuck Open', category: 'Actuator Failure', severity: 'Medium', description: 'Condenser cooling valve stuck open overcooling separator effluent.'});
MERGE (f16:FailureMode {id: 'IDV_16', code: 'IDV(16)', name: 'Stripper Steam Valve Drift', category: 'Thermal Disturbance', severity: 'Medium', description: 'Unknown disturbance IDV(16) manifesting in stripper steam flow and column reboiler.'});
MERGE (f17:FailureMode {id: 'IDV_17', code: 'IDV(17)', name: 'Recycle Loop Pressure Fluctuation', category: 'Compressor Aerodynamic', severity: 'Medium', description: 'Unknown disturbance IDV(17) manifesting in compressor work and recycle loop rate.'});
MERGE (f18:FailureMode {id: 'IDV_18', code: 'IDV(18)', name: 'Internal Stoichiometry Variation', category: 'Process Disturbance', severity: 'Medium', description: 'Unknown disturbance IDV(18) affecting reactor temperature and purge composition.'});
MERGE (f19:FailureMode {id: 'IDV_19', code: 'IDV(19)', name: 'Stripper Column Heat Loss', category: 'Thermal Disturbance', severity: 'Low', description: 'Unknown disturbance IDV(19) affecting stripper bottoms temperature.'});
MERGE (f20:FailureMode {id: 'IDV_20', code: 'IDV(20)', name: 'Compressor Inlet Guide Vane Stiction', category: 'Mechanical Disturbance', severity: 'Medium', description: 'Unknown disturbance IDV(20) affecting compressor throughput and recycle flow.'});
MERGE (f21:FailureMode {id: 'IDV_21', code: 'IDV(21)', name: 'Stream 4 Feed Valve Position Sticking', category: 'Actuator Mechanical Failure', severity: 'High', description: 'Manipulated feed valve XMV(4) sticks periodically.'});

// ------------------------------------------------------------------------------
// 4. Material & Energy Flows (:FEEDS)
// ------------------------------------------------------------------------------
UNWIND [
  {from: 'UNIT_FEED', to: 'UNIT_REACTOR', stream: 'Stream 1-4', phase: 'Gas/Liquid', desc: 'Fresh feeds A, D, E, C'},
  {from: 'UNIT_REACTOR', to: 'UNIT_CONDENSER', stream: 'Stream 7', phase: 'Mixed Vapor-Liquid', desc: 'Exothermic reactor effluent'},
  {from: 'UNIT_CONDENSER', to: 'UNIT_SEPARATOR', stream: 'Stream 7B', phase: 'Partially Condensed', desc: 'Cooled mixed process effluent'},
  {from: 'UNIT_SEPARATOR', to: 'UNIT_COMPRESSOR', stream: 'Stream 8 (Recycle Vapor)', phase: 'Vapor', desc: 'Recycle overhead vapor'},
  {from: 'UNIT_COMPRESSOR', to: 'UNIT_REACTOR', stream: 'Stream 8R', phase: 'High-Pressure Vapor', desc: 'Compressed recycle gas loop'},
  {from: 'UNIT_SEPARATOR', to: 'UNIT_STRIPPER', stream: 'Stream 10 (Liquid Underflow)', phase: 'Liquid', desc: 'Condensed liquid phase feed to stripper'},
  {from: 'UNIT_STRIPPER', to: 'UNIT_PRODUCT', stream: 'Stream 11 (Final Product)', phase: 'Liquid', desc: 'Stripped liquid product (G + H)'},
  {from: 'UNIT_STRIPPER', to: 'UNIT_CONDENSER', stream: 'Stream 5 (Recycle Vapor)', phase: 'Vapor', desc: 'Stripper overhead vapor returned to condenser'}
] AS row
MATCH (source:Unit {id: row.from}), (target:Unit {id: row.to})
MERGE (source)-[:FEEDS {stream: row.stream, phase: row.phase, description: row.desc}]->(target);

// ------------------------------------------------------------------------------
// 5. Sensor Associations (:MEASURES and :MONITORS)
// ------------------------------------------------------------------------------
UNWIND [
  {sensor: 'XMEAS_1', unit: 'UNIT_FEED'},
  {sensor: 'XMEAS_2', unit: 'UNIT_FEED'},
  {sensor: 'XMEAS_3', unit: 'UNIT_FEED'},
  {sensor: 'XMEAS_4', unit: 'UNIT_FEED'},
  {sensor: 'XMEAS_6', unit: 'UNIT_REACTOR'},
  {sensor: 'XMEAS_7', unit: 'UNIT_REACTOR'},
  {sensor: 'XMEAS_8', unit: 'UNIT_REACTOR'},
  {sensor: 'XMEAS_9', unit: 'UNIT_REACTOR'},
  {sensor: 'XMEAS_21', unit: 'UNIT_REACTOR'},
  {sensor: 'XMEAS_22', unit: 'UNIT_CONDENSER'},
  {sensor: 'XMEAS_10', unit: 'UNIT_SEPARATOR'},
  {sensor: 'XMEAS_11', unit: 'UNIT_SEPARATOR'},
  {sensor: 'XMEAS_12', unit: 'UNIT_SEPARATOR'},
  {sensor: 'XMEAS_13', unit: 'UNIT_SEPARATOR'},
  {sensor: 'XMEAS_14', unit: 'UNIT_SEPARATOR'},
  {sensor: 'XMEAS_5', unit: 'UNIT_COMPRESSOR'},
  {sensor: 'XMEAS_20', unit: 'UNIT_COMPRESSOR'},
  {sensor: 'XMEAS_15', unit: 'UNIT_STRIPPER'},
  {sensor: 'XMEAS_16', unit: 'UNIT_STRIPPER'},
  {sensor: 'XMEAS_17', unit: 'UNIT_STRIPPER'},
  {sensor: 'XMEAS_18', unit: 'UNIT_STRIPPER'},
  {sensor: 'XMEAS_19', unit: 'UNIT_STRIPPER'},
  {sensor: 'XMEAS_23', unit: 'UNIT_PRODUCT'},
  {sensor: 'XMEAS_24', unit: 'UNIT_PRODUCT'}
] AS row
MATCH (s:Sensor {id: row.sensor}), (u:Unit {id: row.unit})
MERGE (s)-[:MEASURES]->(u)
MERGE (s)-[:MONITORS]->(u);

// ------------------------------------------------------------------------------
// 6. Unit Susceptibility (:SUSCEPTIBLE_TO and :HAS_FAILURE_MODE)
// ------------------------------------------------------------------------------
UNWIND [
  {unit: 'UNIT_FEED', fault: 'IDV_1'},
  {unit: 'UNIT_FEED', fault: 'IDV_2'},
  {unit: 'UNIT_FEED', fault: 'IDV_3'},
  {unit: 'UNIT_FEED', fault: 'IDV_6'},
  {unit: 'UNIT_FEED', fault: 'IDV_7'},
  {unit: 'UNIT_FEED', fault: 'IDV_8'},
  {unit: 'UNIT_FEED', fault: 'IDV_9'},
  {unit: 'UNIT_FEED', fault: 'IDV_10'},
  {unit: 'UNIT_FEED', fault: 'IDV_21'},
  {unit: 'UNIT_REACTOR', fault: 'IDV_4'},
  {unit: 'UNIT_REACTOR', fault: 'IDV_11'},
  {unit: 'UNIT_REACTOR', fault: 'IDV_13'},
  {unit: 'UNIT_REACTOR', fault: 'IDV_14'},
  {unit: 'UNIT_REACTOR', fault: 'IDV_18'},
  {unit: 'UNIT_CONDENSER', fault: 'IDV_5'},
  {unit: 'UNIT_CONDENSER', fault: 'IDV_12'},
  {unit: 'UNIT_CONDENSER', fault: 'IDV_15'},
  {unit: 'UNIT_COMPRESSOR', fault: 'IDV_17'},
  {unit: 'UNIT_COMPRESSOR', fault: 'IDV_20'},
  {unit: 'UNIT_STRIPPER', fault: 'IDV_16'},
  {unit: 'UNIT_STRIPPER', fault: 'IDV_19'}
] AS row
MATCH (u:Unit {id: row.unit}), (f:FailureMode {id: row.fault})
MERGE (u)-[:SUSCEPTIBLE_TO]->(f)
MERGE (u)-[:HAS_FAILURE_MODE]->(f);

// ------------------------------------------------------------------------------
// 7. Cascading Fault Propagation (:TYPICALLY_CAUSES)
// ------------------------------------------------------------------------------
UNWIND [
  {root: 'IDV_4', downstream: 'IDV_11', mechanism: 'Thermal jacket exhaustion', delay: 45},
  {root: 'IDV_6', downstream: 'IDV_1', mechanism: 'Reactant starvation in reaction zone', delay: 15},
  {root: 'IDV_7', downstream: 'IDV_6', mechanism: 'Feed header pressure drop', delay: 20},
  {root: 'IDV_13', downstream: 'IDV_4', mechanism: 'Accumulation of unreacted heat-generating intermediates', delay: 180},
  {root: 'IDV_5', downstream: 'IDV_17', mechanism: 'Incomplete condensation increases recycle vapor density', delay: 60}
] AS row
MATCH (r:FailureMode {id: row.root}), (d:FailureMode {id: row.downstream})
MERGE (r)-[:TYPICALLY_CAUSES {mechanism: row.mechanism, delay_sec: row.delay}]->(d);

// ------------------------------------------------------------------------------
// 8. Sensor Manifestation Patterns (:MANIFESTS_IN)
// ------------------------------------------------------------------------------
UNWIND [
  {fault: 'IDV_1', sensor: 'XMEAS_4', dev: 'HIGH', metric: 'Flow Rate'},
  {fault: 'IDV_1', sensor: 'XMEAS_7', dev: 'SHIFT', metric: 'Pressure'},
  {fault: 'IDV_4', sensor: 'XMEAS_9', dev: 'HIGH', metric: 'Temperature'},
  {fault: 'IDV_4', sensor: 'XMEAS_21', dev: 'HIGH', metric: 'Cooling Water Outlet Temp'},
  {fault: 'IDV_4', sensor: 'XMEAS_7', dev: 'HIGH', metric: 'Reactor Pressure'},
  {fault: 'IDV_5', sensor: 'XMEAS_22', dev: 'HIGH', metric: 'Cooling Water Temp'},
  {fault: 'IDV_5', sensor: 'XMEAS_13', dev: 'HIGH', metric: 'Separator Pressure'},
  {fault: 'IDV_6', sensor: 'XMEAS_1', dev: 'LOW', metric: 'Flow Rate Drop'},
  {fault: 'IDV_6', sensor: 'XMEAS_7', dev: 'LOW', metric: 'Depressurization'},
  {fault: 'IDV_7', sensor: 'XMEAS_4', dev: 'LOW', metric: 'Header Pressure'},
  {fault: 'IDV_7', sensor: 'XMEAS_6', dev: 'LOW', metric: 'Reactor Feed'},
  {fault: 'IDV_11', sensor: 'XMEAS_9', dev: 'OSCILLATING', metric: 'Cyclic Temperature'},
  {fault: 'IDV_11', sensor: 'XMEAS_21', dev: 'OSCILLATING', metric: 'Cyclic Coolant Return'},
  {fault: 'IDV_13', sensor: 'XMEAS_9', dev: 'DRIFT', metric: 'Slow Temperature Creep'},
  {fault: 'IDV_13', sensor: 'XMEAS_5', dev: 'DRIFT', metric: 'Recycle Accumulation'},
  {fault: 'IDV_16', sensor: 'XMEAS_19', dev: 'HIGH', metric: 'Reboiler Steam Surges'},
  {fault: 'IDV_16', sensor: 'XMEAS_18', dev: 'SHIFT', metric: 'Stripper Temp'},
  {fault: 'IDV_20', sensor: 'XMEAS_20', dev: 'SHIFT', metric: 'Compressor kW'},
  {fault: 'IDV_20', sensor: 'XMEAS_5', dev: 'SHIFT', metric: 'Recycle Rate'}
] AS row
MATCH (f:FailureMode {id: row.fault}), (s:Sensor {id: row.sensor})
MERGE (f)-[:MANIFESTS_IN {expected_deviation: row.dev, metric: row.metric}]->(s);
