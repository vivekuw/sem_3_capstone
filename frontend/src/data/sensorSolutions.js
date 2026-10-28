// Domain knowledge and component-level corrective solutions for all 43 TEP sensors & actuators
// Grounded in Tennessee Eastman Plant (TEP) chemical engineering P&ID topology

export const SENSOR_SOLUTIONS = {
  // =========================================================================
  // UNIT_REACTOR (Chemical Reactor CSTR)
  // =========================================================================
  XMEAS_9: {
    sensor_id: 'XMEAS_9',
    name: 'Reactor Temperature',
    component_name: 'Reactor Cooling Jacket Control Valve (XMV_10) & CW Supply Header',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Pneumatic Control Valve & Primary Coolant Heat Exchanger',
    actuator_tag: 'XMV_10 (Reactor CW Valve)',
    pid_tag: 'TC-101 / Heat Duty Balance',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Reactor core temperature has spiked above 120.4 °C because cooling water valve XMV_10 is throttled or suffering actuator stiction, preventing jacket heat removal while exothermic reaction heat (Q_gen > Q_rem) accumulates rapidly.',
    physical_mechanism: 'The CSTR reactions (A + C + D -> G and A + C + E -> H) are strongly exothermic (dH ~ -84 kJ/mol). Heat generation increases exponentially with temperature according to Arrhenius kinetics. If valve XMV_10 restricts cooling water below 41.1%, jacket heat removal capacity collapses, triggering thermal excursion towards safety trip thresholds (135 °C).',
    solution_steps: [
      'Switch Reactor Cooling Water Valve XMV_10 from DCS Auto to Manual override and stroke positioner to 41.1% nominal.',
      'Engage auxiliary cooling water booster pump line to increase jacket circulation velocity above 42.0 m³/h.',
      'Trim Reactant A feed rate (XMEAS_1) by 15% to suppress core exothermic reaction rate until temperature stabilizes.',
      'Monitor Reactor Coolant Return (XMEAS_21) to confirm jacket temperature differential drops below 26.0 °C.'
    ],
    emergency_action: 'Stroke XMV_10 to 100% open, trip Reactant A feed booster pump, and engage nitrogen purge quench if core temp exceeds 132 °C.',
    nominal_baseline: '120.4 °C'
  },

  XMEAS_21: {
    sensor_id: 'XMEAS_21',
    name: 'Reactor Coolant Return Temp',
    component_name: 'Reactor Jacket Return Manifold & Outlet Thermowell',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Heat Transfer Fluid Return Header & Sensor Thermowell',
    actuator_tag: 'XMV_10',
    pid_tag: 'TI-102 / Thermal Return',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Coolant return temperature is elevated beyond 94.4 °C, indicating the reactor jacket is thermally saturated and cannot absorb additional heat from the reactor vessel.',
    physical_mechanism: 'Coolant temperature rise (dT = Q_rem / (m_dot * Cp)) is inversely proportional to cooling water mass flow rate. When valve XMV_10 throttles coolant flow, the lower velocity causes residence time in the jacket to increase, boiling coolant in the return manifold and reducing the logarithmic mean temperature difference (LMTD).',
    solution_steps: [
      'Increase cooling water supply header pressure by activating secondary utility pump P-102B.',
      'Stroke cooling water valve XMV_10 open to clear thermal saturation in the return manifold.',
      'Verify jacket return temperature falls steadily towards nominal 94.4 °C.',
      'Check thermowell TI-102 calibration and purge air pockets from the cooling jacket casing.'
    ],
    emergency_action: 'Open cooling jacket vent line to purge steam pockets and switch to reserve chilled water loop.',
    nominal_baseline: '94.4 °C'
  },

  XMV_10: {
    sensor_id: 'XMV_10',
    name: 'Reactor CW Valve Position',
    component_name: 'Pneumatic Actuator Valve XMV_10 & Smart Positioner',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Fail-Open Pneumatic Globe Valve with Positioner Feedback',
    actuator_tag: 'XMV_10',
    pid_tag: 'FCV-110 / Reactor Coolant',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Valve XMV_10 actuator has deviated from nominal 41.1% opening due to valve stiction or diaphragm air pressure loss, directly choking cooling water flow and causing reactor core overheating.',
    physical_mechanism: 'Pneumatic actuator stiction prevents fine proportional modulation of cooling water flow. As reactor heat generation shifts, the valve fails to adjust position, creating a fatal imbalance between reaction kinetics and heat removal that drives core temperature upward.',
    solution_steps: [
      'Inspect 20 psi instrument air supply tubing to actuator XMV_10 for moisture or pressure drops.',
      'Perform digital valve positioner auto-calibration routine to clear mechanical stem stiction.',
      'Manually position handwheel to lock valve at 41.1% nominal opening until auto-control is restored.',
      'Verify cooling water flow rate stabilizes and core temperature drops below 120.4 °C.'
    ],
    emergency_action: 'Manually crank mechanical bypass valve open to maintain minimum 40% cooling flow regardless of actuator failure.',
    nominal_baseline: '41.1 %'
  },

  XMEAS_7: {
    sensor_id: 'XMEAS_7',
    name: 'Reactor Pressure',
    component_name: 'Reactor Vapor Dome & Off-Gas Header Relief Line',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Vapor Space Containment & Pressure Control Loop',
    actuator_tag: 'XMV_6 / XMV_10',
    pid_tag: 'PIC-101 / Reactor Pressure',
    is_thermal: false,
    overheat_diagnosis: 'OVERPRESSURIZATION DRIVEN BY OVERHEATING: Reactor pressure has surged above 2705.0 kPa because core overheating vaporizes volatile feed components (Reactants A & C), exceeding vapor dome volumetric capacity.',
    physical_mechanism: 'Antoine equation equilibrium dictates that vapor pressure rises exponentially with reactor temperature. Core overheating directly drives volatile components into the vapor phase, generating pressure surges that threaten reactor mechanical pressure boundaries (trip limit: 2895 kPa).',
    solution_steps: [
      'Immediately cool reactor core by increasing cooling water flow through Valve XMV_10 to suppress vapor generation.',
      'Modulate downstream Purge Gas Valve XMV_6 to relieve excess vapor accumulation into the flare header.',
      'Check Condenser CW Valve XMV_11 to maximize vapor condensation rate of Stream 7.',
      'Confirm pressure returns to nominal baseline of 2705.0 kPa.'
    ],
    emergency_action: 'If pressure exceeds 2850 kPa, open emergency flare vent valve PV-101 and initiate reactor quench.',
    nominal_baseline: '2705.0 kPa'
  },

  XMEAS_8: {
    sensor_id: 'XMEAS_8',
    name: 'Reactor Level',
    component_name: 'CSTR Agitator Assembly & Differential Pressure Level Transmitter',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Liquid Sump Containment & Agitation Mixing System',
    actuator_tag: 'XMV_10 / Stream 6 Flow',
    pid_tag: 'LIC-101 / Reactor Inventory',
    is_thermal: false,
    overheat_diagnosis: 'LEVEL DISTURBANCE FROM THERMAL EXPANSION: Reactor liquid holdup deviated from 65.2% due to liquid density changes and rapid vapor boil-off under elevated core temperatures.',
    physical_mechanism: 'Excessive reaction heat causes localized boiling and foaming in the CSTR, altering effective slurry density and causing liquid carryover into vapor outlet Stream 7.',
    solution_steps: [
      'Inspect mechanical agitator motor power and rotational speed (nominal 120 RPM) for foaming suppression.',
      'Balance fresh reactant inflow rates with reactor outlet product draw.',
      'Cool reactor core to eliminate thermal boiling swell and restore stable vapor-liquid interface at 65.2%.'
    ],
    emergency_action: 'Trim Reactant D & E feed rates if high liquid level risks liquid entrainment into condenser header.',
    nominal_baseline: '65.2 %'
  },

  XMEAS_6: {
    sensor_id: 'XMEAS_6',
    name: 'Reactor Combined Feed Flow',
    component_name: 'Stream 6 Combined Gas Manifold & Recycle Influx Header',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Gas Manifold & Mixing Chamber',
    actuator_tag: 'XMV_5 / Feed Valves',
    pid_tag: 'FIC-101 / Combined Reactor Influx',
    is_thermal: false,
    overheat_diagnosis: 'FEED HEADER FLOW INSTABILITY: Feed gas flow deviated from 42.3 kscmh, altering reactant residence time and triggering thermal instability in the reactor core.',
    physical_mechanism: 'Stream 6 combines fresh Reactant feeds (Streams 1, 2, 3, 4) with recycled gas from compressor Stream 5. Flow fluctuations disrupt stoichiometry and heat generation profiles inside the reactor vessel.',
    solution_steps: [
      'Verify compressor recycle discharge flow (XMEAS_5) aligns with fresh feed delivery rates.',
      'Inspect Stream 6 orifice plate flowmeter calibration and differential pressure transmitter.',
      'Re-engage master ratio controller to stabilize combined feed rate at 42.3 kscmh.'
    ],
    emergency_action: 'Throttle fresh feeds if compressor surge threatens Stream 6 manifold pressure integrity.',
    nominal_baseline: '42.3 kscmh'
  },

  XMEAS_23: {
    sensor_id: 'XMEAS_23',
    name: 'Feed Stream Comp A',
    component_name: 'Process Gas Chromatograph GC-1 (Stream 6) & Reactant A Ratio Controller',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Composition Analyzer & Ratio Controller',
    actuator_tag: 'XMV_1 (Reactant A Valve)',
    pid_tag: 'AIC-101 / Comp A',
    is_thermal: false,
    overheat_diagnosis: 'STOICHIOMETRIC EXCESS DRIVING OVERHEAT: High Reactant A concentration accelerates primary exothermic reaction kinetics, causing thermal overshoot in the reactor core.',
    physical_mechanism: 'Reactant A is the primary limiting reagent for exothermic reactions. A surplus of A shifts reaction equilibrium rightward, generating excess heat that overwhelms jacket cooling capacity.',
    solution_steps: [
      'Throttle Reactant A fresh feed control valve XMV_1 to lower Stream 6 concentration back to 32.25 mol%.',
      'Purge accumulated inert Component F to re-establish proper gas mole fractions.',
      'Monitor reactor temperature to confirm heat release rate moderates.'
    ],
    emergency_action: 'Trim Reactant A feed rate by 25% if reactor temperature continues to escalate.',
    nominal_baseline: '32.25 mol%'
  },

  XMEAS_24: {
    sensor_id: 'XMEAS_24',
    name: 'Feed Stream Comp B',
    component_name: 'Gas Chromatograph GC-1 & Fresh Feed B Header',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Composition Analyzer',
    actuator_tag: 'XMV_4',
    pid_tag: 'AIC-102 / Comp B',
    is_thermal: false,
    overheat_diagnosis: 'INERT DILUENT DRIFT: Feed B concentration drifted from 8.95 mol%, altering reaction kinetics and mixture specific heat capacity in the reactor core.',
    physical_mechanism: 'Component B acts as a moderate carrier gas. Alterations in its partial pressure change overall gas heat capacity and flash drum vapor equilibrium.',
    solution_steps: [
      'Calibrate GC-1 sampling stream conditioning probe.',
      'Adjust fresh feed A+C mixed ratio to stabilize Component B at nominal 8.95 mol%.'
    ],
    emergency_action: 'Ensure purge vent valve XMV_6 remains responsive to prevent inert gas buildup.',
    nominal_baseline: '8.95 mol%'
  },

  XMEAS_25: {
    sensor_id: 'XMEAS_25',
    name: 'Feed Stream Comp C',
    component_name: 'Reactant C Flow Header & Stream 6 Analyzer GC-1',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Composition Analyzer & Flow Ratio System',
    actuator_tag: 'XMV_4',
    pid_tag: 'AIC-103 / Comp C',
    is_thermal: false,
    overheat_diagnosis: 'REACTANT RATIO IMBALANCE: Reactant C mole fraction deviated from 26.35 mol%, disrupting the stoichiometric A:C balance required for steady heat release.',
    physical_mechanism: 'Reactant C participates in both product G and product H synthesis reactions. Composition imbalances cause fluctuating reaction rates and unstable heat duty.',
    solution_steps: [
      'Trim Reactant C proportion in mixed feed Stream 4.',
      'Verify compressor recycle loop does not harbor unreacted Reactant C surplus.',
      'Restore Component C concentration to 26.35 mol%.'
    ],
    emergency_action: 'Rebalance master feed controller to prevent stoichiometric runaway.',
    nominal_baseline: '26.35 mol%'
  },

  XMEAS_26: {
    sensor_id: 'XMEAS_26',
    name: 'Feed Stream Comp D',
    component_name: 'Reactant D Feed Stream Valve XMV_2 & GC-1 Analyzer',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Liquid Feed Injection System',
    actuator_tag: 'XMV_2',
    pid_tag: 'AIC-104 / Comp D',
    is_thermal: false,
    overheat_diagnosis: 'PRODUCT G PRECURSOR SURGE: Excess Reactant D accelerates reaction A + C + D -> G, releasing intense exothermic heat that overheats the reactor.',
    physical_mechanism: 'Reactant D directly determines the formation rate of Product G (-84 kJ/mol). Over-feeding D accelerates heat generation beyond jacket cooling limits.',
    solution_steps: [
      'Throttle Reactant D feed valve XMV_2 to bring feed flow back to 3664 kg/h.',
      'Verify Stream 6 Component D fraction returns to 6.85 mol%.',
      'Increase reactor cooling water flow (XMV_10) to absorb residual heat.'
    ],
    emergency_action: 'Temporarily reduce D feed by 20% to quench reaction thermal runaway.',
    nominal_baseline: '6.85 mol%'
  },

  XMEAS_27: {
    sensor_id: 'XMEAS_27',
    name: 'Feed Stream Comp E',
    component_name: 'Reactant E Feed Stream Valve XMV_3 & GC-1 Analyzer',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Liquid Feed Injection System',
    actuator_tag: 'XMV_3',
    pid_tag: 'AIC-105 / Comp E',
    is_thermal: false,
    overheat_diagnosis: 'PRODUCT H PRECURSOR IMBALANCE: Reactant E drifted from 18.75 mol%, destabilizing reaction A + C + E -> H and column product balance.',
    physical_mechanism: 'Reactant E drives Product H synthesis. Imbalances distort reactor heat duty and cause stripper bottoms off-spec issues.',
    solution_steps: [
      'Adjust Reactant E feed valve XMV_3 to maintain 4505 kg/h.',
      'Check GC-1 carrier gas supply and retention time calibration.',
      'Verify feed composition aligns with 18.75 mol% nominal.'
    ],
    emergency_action: 'Align E feed with downstream stripper reboiler capacity.',
    nominal_baseline: '18.75 mol%'
  },

  XMEAS_28: {
    sensor_id: 'XMEAS_28',
    name: 'Feed Stream Comp F',
    component_name: 'Purge Stream Optimization Controller & GC-1 Analyzer',
    equipment_unit: 'Chemical Reactor CSTR (UNIT_REACTOR)',
    component_type: 'Inert Accumulation Monitor',
    actuator_tag: 'XMV_6',
    pid_tag: 'AIC-106 / Comp F',
    is_thermal: false,
    overheat_diagnosis: 'INERT COMPONENT ACCUMULATION: Inert Component F concentration drifted from 1.65 mol%, decreasing reactor reaction rate and causing pressure build-up.',
    physical_mechanism: 'Component F is an inert byproduct. If purge rate is too low, F accumulates, blanket-diluting reactants and reducing reactor efficiency while forcing pressure upward.',
    solution_steps: [
      'Increase Separator Purge Valve XMV_6 opening to purge excess inert F.',
      'Verify Component F stabilizes at 1.65 mol% in feed header Stream 6.'
    ],
    emergency_action: 'Increase purge rate to 0.40 kscmh to vent accumulated inert gas.',
    nominal_baseline: '1.65 mol%'
  },

  // =========================================================================
  // UNIT_CONDENSER (Product Condenser)
  // =========================================================================
  XMEAS_22: {
    sensor_id: 'XMEAS_22',
    name: 'Condenser Coolant Return Temp',
    component_name: 'Shell-and-Tube Product Condenser Tube Bundle & CW Return Manifold',
    equipment_unit: 'Product Condenser (UNIT_CONDENSER)',
    component_type: 'Heat Exchanger Bundle & Cooling Loop',
    actuator_tag: 'XMV_11 (Condenser CW Valve)',
    pid_tag: 'TC-201 / Condenser Duty',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Condenser coolant return temperature has exceeded 77.2 °C, indicating that the condenser cannot condense hot reactor vapors and is allowing superheated gas to surge into the separator drum.',
    physical_mechanism: 'Hot effluent Stream 7 from the overheated reactor enters the condenser. If cooling water valve XMV_11 is throttled or tubes are fouled, coolant boils or saturates, collapsing condensation efficiency and pushing hot vapor into the downstream separator.',
    solution_steps: [
      'Open Condenser Cooling Water Valve XMV_11 from throttled state to nominal 18.1% (or higher during excursion).',
      'Inspect cooling water supply header pressure to ensure adequate flow through tube bundle.',
      'Check condenser shell-and-tube differential pressure for air-locking or scaling.',
      'Confirm coolant return temperature drops back to 77.2 °C.'
    ],
    emergency_action: 'Stroke XMV_11 to 50% open to rapidly quench hot vapor exiting the reactor.',
    nominal_baseline: '77.2 °C'
  },

  XMV_11: {
    sensor_id: 'XMV_11',
    name: 'Condenser CW Valve Position',
    component_name: 'Condenser Cooling Water Control Valve XMV_11 & Actuator',
    equipment_unit: 'Product Condenser (UNIT_CONDENSER)',
    component_type: 'Pneumatic Control Valve',
    actuator_tag: 'XMV_11',
    pid_tag: 'FCV-211 / Condenser CW',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Valve XMV_11 actuator restricted coolant flow below 18.1%, causing thermal saturation in the condenser and downstream overheating.',
    physical_mechanism: 'Throttling XMV_11 reduces cooling water velocity through the tube bundle, raising coolant return temperature and allowing hot uncondensed reactor vapor to enter the separator vessel.',
    solution_steps: [
      'Stroke Valve XMV_11 to nominal 18.1% operating setpoint.',
      'Inspect valve positioner air supply line and I/P converter signal.',
      'Verify cooling water flow rate restores condensation of Stream 7 vapors.'
    ],
    emergency_action: 'Engage manual handwheel bypass to force valve open to 25% until auto loop is restored.',
    nominal_baseline: '18.1 %'
  },

  // =========================================================================
  // UNIT_SEPARATOR (Vapor-Liquid Separator)
  // =========================================================================
  XMEAS_10: {
    sensor_id: 'XMEAS_10',
    name: 'Purge Gas Rate',
    component_name: 'Separator Purge Line Control Valve (XMV_6) & Flare Header',
    equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)',
    component_type: 'Vapor Venting & Pressure Relief System',
    actuator_tag: 'XMV_6 (Purge Valve)',
    pid_tag: 'FIC-301 / Purge Vent',
    is_thermal: false,
    overheat_diagnosis: 'PURGE SURGE FROM OVERHEATING: Purge gas rate surged above 0.337 kscmh as elevated reactor vapor pressure forced excess hot gas into the separator overhead vent.',
    physical_mechanism: 'When the reactor overheats and condenser cooling fails, uncondensed gas flashes into the separator vapor dome, causing high pressure that forces purge valve XMV_6 to vent valuable reactants to flare.',
    solution_steps: [
      'Throttle Purge Valve XMV_6 back to nominal setpoint of 0.337 kscmh.',
      'Resolve upstream reactor overheating (XMEAS_9) and condenser cooling (XMV_11) to stop vapor boiling.',
      'Verify purge vent flow stabilizes, minimizing reactant loss to flare.'
    ],
    emergency_action: 'Close purge valve to minimum safe stop (0.20 kscmh) if valuable product G is escaping to flare.',
    nominal_baseline: '0.337 kscmh'
  },

  XMEAS_11: {
    sensor_id: 'XMEAS_11',
    name: 'Separator Temperature',
    component_name: 'Separator Flash Vessel Drum Body & Demister Pad',
    equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)',
    component_type: 'Flash Vessel & Demister Entrainment Separator',
    actuator_tag: 'XMV_11',
    pid_tag: 'TI-301 / Separator Temp',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Separator flash vessel temperature has climbed above 80.1 °C because hot uncondensed reactor vapor is blowing through the condenser into the separator drum.',
    physical_mechanism: 'Thermal energy carried over from the reactor vapor line heats the separator vessel, preventing condensation of liquid products G & H and increasing vapor carryover into the recycle compressor.',
    solution_steps: [
      'Increase condenser cooling water flow via Valve XMV_11 to subcool condensed liquid below 80.1 °C.',
      'Address reactor core overheating (Valve XMV_10) to reduce vapor enthalpy entering the condenser.',
      'Check separator liquid temperature profile to prevent boiling in underflow Stream 10.'
    ],
    emergency_action: 'Increase condenser cooling to maximum to drop separator temperature back to 80.1 °C.',
    nominal_baseline: '80.1 °C'
  },

  XMEAS_12: {
    sensor_id: 'XMEAS_12',
    name: 'Separator Level',
    component_name: 'Separator Liquid Underflow Level Control Valve (XMV_7) & Sump Chamber',
    equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)',
    component_type: 'Liquid Holdup & Interface Level Control Loop',
    actuator_tag: 'XMV_7',
    pid_tag: 'LIC-301 / Separator Holdup',
    is_thermal: false,
    overheat_diagnosis: 'LIQUID INVENTORY COLLAPSE: Separator level deviated from 50.0% due to liquid vaporization under high process temperature and liquid underflow imbalance.',
    physical_mechanism: 'High temperatures vaporize light liquid components from the separator boot, while underflow pump drawing liquid to the stripper depletes vessel inventory.',
    solution_steps: [
      'Modulate underflow valve XMV_7 to maintain 50.0% liquid level in separator sump.',
      'Restore condenser cooling to increase liquid condensation rate into the separator vessel.',
      'Verify differential pressure level transmitter calibration.'
    ],
    emergency_action: 'Throttle underflow valve XMV_7 if separator level drops below 30% to prevent pump cavitation.',
    nominal_baseline: '50.0 %'
  },

  XMEAS_13: {
    sensor_id: 'XMEAS_13',
    name: 'Separator Pressure',
    component_name: 'Flash Drum Vapor Headspace & Compressor Suction Header',
    equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)',
    component_type: 'Vapor Containment Space',
    actuator_tag: 'XMV_6 / XMV_5',
    pid_tag: 'PIC-301 / Separator Pressure',
    is_thermal: false,
    overheat_diagnosis: 'SEPARATOR OVERPRESSURE: Vapor headspace pressure spiked above 2633.0 kPa due to thermal vapor generation in upstream units.',
    physical_mechanism: 'Elevated reactor core temperature creates excessive gas volume that cannot be fully condensed in the condenser, pressurizing the separator vapor dome.',
    solution_steps: [
      'Modulate purge valve XMV_6 to relieve excess vapor volume.',
      'Ensure recycle compressor anti-surge valve XMV_5 draws suction gas smoothly.',
      'Cool upstream reactor and condenser to lower vapor formation rates.'
    ],
    emergency_action: 'Open separator vent valve if pressure exceeds 2800 kPa.',
    nominal_baseline: '2633.0 kPa'
  },

  XMEAS_14: {
    sensor_id: 'XMEAS_14',
    name: 'Separator Underflow Rate',
    component_name: 'Separator Bottoms Transfer Pump & Valve XMV_7',
    equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)',
    component_type: 'Liquid Transfer Line to Stripper Column',
    actuator_tag: 'XMV_7',
    pid_tag: 'FIC-302 / Stripper Feed Flow',
    is_thermal: false,
    overheat_diagnosis: 'STRIPPER FEED RATE DISTURBANCE: Liquid flow to the stripper column deviated from 25.1 m³/h, destabilizing column liquid holdup.',
    physical_mechanism: 'Fluctuations in separator level and underflow valve XMV_7 positioning cause surging or starvation of feed to the product stripper column.',
    solution_steps: [
      'Calibrate underflow flow controller FIC-302 to maintain 25.1 m³/h.',
      'Check transfer pump suction strainer for debris or vapor cavitation.',
      'Ensure steady separator liquid level at 50%.'
    ],
    emergency_action: 'Lock valve XMV_7 in cascade with level controller to prevent empty-vessel pump trips.',
    nominal_baseline: '25.1 m3/h'
  },

  XMEAS_29: { sensor_id: 'XMEAS_29', name: 'Purge Comp A', component_name: 'Purge Gas Chromatograph GC-2 & Vent Header', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-301', is_thermal: false, overheat_diagnosis: 'PURGE COMPOSITION A SHIFT: Valuable Reactant A venting in purge gas deviated from 32.95 mol%.', physical_mechanism: 'Vapor-liquid equilibrium shifts caused by temperature fluctuations change the molar ratio of Reactant A vented through Stream 9.', solution_steps: ['Adjust separator temperature to 80.1 °C.', 'Tune purge valve XMV_6 to minimize Reactant A flare loss.', 'Calibrate GC-2 analyzer sample probe.'], emergency_action: 'Throttle purge flow if A loss exceeds economic limits.', nominal_baseline: '32.95 mol%' },
  XMEAS_30: { sensor_id: 'XMEAS_30', name: 'Purge Comp B', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-302', is_thermal: false, overheat_diagnosis: 'PURGE COMPOSITION B DRIFT: Component B in purge gas drifted from 13.80 mol%.', physical_mechanism: 'Gas equilibrium changes in separator drum alter inert B venting rates.', solution_steps: ['Check separator pressure and temperature.', 'Verify GC-2 analyzer detector zero point.'], emergency_action: 'Maintain nominal purge rate to prevent B buildup.', nominal_baseline: '13.80 mol%' },
  XMEAS_31: { sensor_id: 'XMEAS_31', name: 'Purge Comp C', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-303', is_thermal: false, overheat_diagnosis: 'PURGE COMPOSITION C SHIFT: Reactant C in purge gas deviated from 23.95 mol%.', physical_mechanism: 'Vapor equilibrium shifts caused by condenser temperature rise cause excess C to escape in purge.', solution_steps: ['Restore condenser cooling to subcool Stream 8.', 'Trim purge flow to retain Reactant C.'], emergency_action: 'Adjust purge valve XMV_6 setpoint.', nominal_baseline: '23.95 mol%' },
  XMEAS_32: { sensor_id: 'XMEAS_32', name: 'Purge Comp D', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-304', is_thermal: false, overheat_diagnosis: 'PURGE COMPOSITION D LOSS: Reactant D vapor carryover drifted from 1.25 mol%.', physical_mechanism: 'Higher separator temperature vaporizes heavy liquid D into purge stream.', solution_steps: ['Lower separator temperature to 80.1 °C.', 'Check condenser cooling water valve XMV_11.'], emergency_action: 'Cool condenser to knock down D vapor.', nominal_baseline: '1.25 mol%' },
  XMEAS_33: { sensor_id: 'XMEAS_33', name: 'Purge Comp E', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-305', is_thermal: false, overheat_diagnosis: 'PURGE COMPOSITION E LOSS: Reactant E vapor carryover drifted from 18.55 mol%.', physical_mechanism: 'Temperature excursions vaporize liquid E into the recycle and purge streams.', solution_steps: ['Restore separator flash equilibrium at 80.1 °C.', 'Calibrate GC-2 optical sensor.'], emergency_action: 'Re-establish condenser heat duty.', nominal_baseline: '18.55 mol%' },
  XMEAS_34: { sensor_id: 'XMEAS_34', name: 'Purge Comp F', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-306', is_thermal: false, overheat_diagnosis: 'INERT F VENTING RATE SHIFT: Component F venting drifted from 2.25 mol%.', physical_mechanism: 'F must be vented in exact proportion to avoid buildup or excessive loss of reactants.', solution_steps: ['Regulate purge valve XMV_6 to achieve exactly 2.25 mol% F in purge gas.', 'Inspect vent backpressure.'], emergency_action: 'Maintain purge rate above 0.30 kscmh.', nominal_baseline: '2.25 mol%' },
  XMEAS_35: { sensor_id: 'XMEAS_35', name: 'Purge Comp G', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-307', is_thermal: false, overheat_diagnosis: 'PRODUCT G LOSS TO FLARE: Desired product G is vaporizing and escaping in purge gas (nominal: 4.80 mol%).', physical_mechanism: 'Product G is a liquid product. High separator temperatures cause G to flash into the vapor phase and vent out through purge valve XMV_6, wasting expensive product.', solution_steps: ['Cool separator liquid immediately to condense Product G.', 'Restore Condenser CW Valve XMV_11 to nominal opening.', 'Throttle purge valve to reduce G loss.'], emergency_action: 'Trim purge valve to avoid flaring finished Product G.', nominal_baseline: '4.80 mol%' },
  XMEAS_36: { sensor_id: 'XMEAS_36', name: 'Purge Comp H', component_name: 'Purge Gas Chromatograph GC-2', equipment_unit: 'Vapor-Liquid Separator (UNIT_SEPARATOR)', component_type: 'Online Gas Analyzer', actuator_tag: 'XMV_6', pid_tag: 'AIC-308', is_thermal: false, overheat_diagnosis: 'PRODUCT H LOSS TO FLARE: Desired product H is escaping through the purge vent (nominal: 2.45 mol%).', physical_mechanism: 'Thermal boiling in separator flashes Product H into the purge header.', solution_steps: ['Subcool condenser outlet below 80.1 °C.', 'Verify purge composition H returns to 2.45 mol%.'], emergency_action: 'Check condenser cooling water temperature.', nominal_baseline: '2.45 mol%' },

  // =========================================================================
  // UNIT_COMPRESSOR (Recycle Compressor)
  // =========================================================================
  XMEAS_5: {
    sensor_id: 'XMEAS_5',
    name: 'Recycle Flow',
    component_name: 'Recycle Gas Piping & Centrifugal Compressor Anti-Surge Valve (XMV_5)',
    equipment_unit: 'Recycle Compressor (UNIT_COMPRESSOR)',
    component_type: 'Centrifugal Compressor Loop & Anti-Surge Bypass',
    actuator_tag: 'XMV_5 (Compressor Bypass)',
    pid_tag: 'FIC-401 / Recycle Gas Rate',
    is_thermal: false,
    overheat_diagnosis: 'RECYCLE LOOP FLOW ANOMALY: Recycle gas flow drifted from 26.9 kscmh, altering reactant recycle velocity into reactor combined feed manifold.',
    physical_mechanism: 'Density variations in separator vapor or anti-surge valve XMV_5 throttling disrupt compressor aerodynamic head, shifting recycle flow.',
    solution_steps: [
      'Modulate anti-surge bypass valve XMV_5 to re-establish 26.9 kscmh recycle flow.',
      'Check compressor suction filter differential pressure.',
      'Verify compressor rotor speed and lubrication oil temperature.'
    ],
    emergency_action: 'Open anti-surge bypass valve immediately if compressor approaches aerodynamic surge boundary.',
    nominal_baseline: '26.9 kscmh'
  },

  XMEAS_20: {
    sensor_id: 'XMEAS_20',
    name: 'Compressor Work',
    component_name: 'Centrifugal Compressor Impeller & Electric Drive Motor',
    equipment_unit: 'Recycle Compressor (UNIT_COMPRESSOR)',
    component_type: 'Electric Motor & Rotating Shaft Assembly',
    actuator_tag: 'XMV_5',
    pid_tag: 'JI-401 / Compressor Power',
    is_thermal: true,
    overheat_diagnosis: 'MOTOR OVERLOAD FROM GAS SURGE: Compressor electric power consumption has exceeded 341.0 kW due to gas density shifts and increased volumetric load caused by plant pressure excursions.',
    physical_mechanism: 'When upstream reactor overpressurizes, suction gas density into the compressor increases, demanding higher shaft torque (Work = m_dot * Head / efficiency), overloading the drive motor.',
    solution_steps: [
      'Modulate anti-surge recycle valve XMV_5 to relieve suction volumetric load.',
      'Reduce plant system pressure by addressing reactor overheating and modulating purge.',
      'Check motor stator winding temperatures and bearing vibration levels.',
      'Restore compressor shaft power to nominal 341.0 kW.'
    ],
    emergency_action: 'Slightly open compressor bypass line to prevent electric motor over-current tripping.',
    nominal_baseline: '341.0 kW'
  },

  // =========================================================================
  // UNIT_STRIPPER (Product Stripper Column)
  // =========================================================================
  XMEAS_18: {
    sensor_id: 'XMEAS_18',
    name: 'Stripper Temperature',
    component_name: 'Stripper Reboiler Thermosyphon Tube Bundle & Steam Heat Exchanger',
    equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)',
    component_type: 'Column Base Reboiler & Thermal Sump',
    actuator_tag: 'XMV_9 (Reboiler Steam Valve)',
    pid_tag: 'TC-501 / Stripper Sump Temp',
    is_thermal: true,
    overheat_diagnosis: 'MACHINE OVERHEATING FROM THIS COMPONENT: Stripper bottom temperature has exceeded 65.7 °C because Reboiler Steam Valve XMV_9 is delivering excess heat duty, boiling off valuable product liquid.',
    physical_mechanism: 'The stripping column boils light reactants (A, C) overhead to purify liquid product (G, H). Excess steam flow from XMV_9 overheats the column bottom, causing product G & H thermal degradation and excessive overhead vapor surging.',
    solution_steps: [
      'Throttle Reboiler Steam Control Valve XMV_9 back to nominal 1085 kg/h flow rate.',
      'Inspect steam control loop TC-501 tuning parameters to eliminate thermal cycling.',
      'Verify column bottoms temperature stabilizes at nominal 65.7 °C.',
      'Check product purity to confirm G and H meet 53.75% and 43.85% specifications.'
    ],
    emergency_action: 'Trim steam valve XMV_9 by 15% immediately if column bottom temperature exceeds 72 °C.',
    nominal_baseline: '65.7 °C'
  },

  XMEAS_19: {
    sensor_id: 'XMEAS_19',
    name: 'Stripper Steam Flow',
    component_name: 'Reboiler Steam Supply Valve (XMV_9) & Steam Condensate Trap',
    equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)',
    component_type: 'Pneumatic Steam Control Valve & Condensate Trap',
    actuator_tag: 'XMV_9',
    pid_tag: 'FCV-509 / Reboiler Steam Flow',
    is_thermal: true,
    overheat_diagnosis: 'STEAM VALVE EXCURSION CAUSING OVERHEAT: Steam flow deviated from 1085.0 kg/h, directly overheating the stripper column base.',
    physical_mechanism: 'Valve XMV_9 regulates steam to the thermosyphon reboiler. Valve stiction or steam header pressure swings alter column heat duty, driving bottom temperature excursions.',
    solution_steps: [
      'Calibrate Steam Valve XMV_9 smart positioner.',
      'Inspect condensate trap for water-logging or steam blowing.',
      'Reset flow setpoint to nominal 1085.0 kg/h.'
    ],
    emergency_action: 'Switch steam controller to manual and lock valve position at 45% nominal stroke.',
    nominal_baseline: '1085.0 kg/h'
  },

  XMEAS_15: {
    sensor_id: 'XMEAS_15',
    name: 'Stripper Level',
    component_name: 'Stripper Column Sump & Product Stream Control Valve (XMV_8)',
    equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)',
    component_type: 'Liquid Holdup & Discharge Control Loop',
    actuator_tag: 'XMV_8',
    pid_tag: 'LIC-501 / Stripper Sump Level',
    is_thermal: false,
    overheat_diagnosis: 'COLUMN SUMP LEVEL EXCURSION: Stripper bottom level deviated from 50.0% due to reboiler boil-off rate or product draw imbalance.',
    physical_mechanism: 'Imbalance between feed underflow from separator (XMEAS_14) and product draw (XMEAS_17) creates level fluctuations that risk reboiler tube uncovery.',
    solution_steps: [
      'Modulate Product Underflow Valve XMV_8 to re-establish 50.0% level.',
      'Ensure separator feed underflow flow rate is steady at 25.1 m³/h.',
      'Verify reboiler heat duty does not cause flash cavitation in bottoms pump.'
    ],
    emergency_action: 'Throttle valve XMV_8 if level drops below 35% to protect reboiler tube bundles from running dry.',
    nominal_baseline: '50.0 %'
  },

  XMEAS_16: {
    sensor_id: 'XMEAS_16',
    name: 'Stripper Pressure',
    component_name: 'Stripper Overhead Vapor Header & Offgas Condenser',
    equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)',
    component_type: 'Column Overhead Pressure Control Loop',
    actuator_tag: 'XMV_9 / Column Vent',
    pid_tag: 'PIC-501 / Stripper Pressure',
    is_thermal: false,
    overheat_diagnosis: 'STRIPPER OVERPRESSURE: Column pressure rose above 3010.0 kPa due to high reboiler steam boil-off rate.',
    physical_mechanism: 'High reboiler temperatures vaporize excess liquid, flooding column trays and elevating overhead vapor pressure.',
    solution_steps: [
      'Trim reboiler steam valve XMV_9 to moderate boil-off rate.',
      'Check overhead vapor line to condenser for restriction.',
      'Restore column pressure to 3010.0 kPa.'
    ],
    emergency_action: 'Open column pressure control bypass if pressure exceeds 3200 kPa.',
    nominal_baseline: '3010.0 kPa'
  },

  XMEAS_17: {
    sensor_id: 'XMEAS_17',
    name: 'Stripper Underflow Rate',
    component_name: 'Product Stream Transfer Pump & Bottoms Flow Valve XMV_8',
    equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)',
    component_type: 'Liquid Product Delivery Line',
    actuator_tag: 'XMV_8',
    pid_tag: 'FIC-502 / Product Stream Flow',
    is_thermal: false,
    overheat_diagnosis: 'FINISHED PRODUCT FLOW DRIFT: Final product delivery flow drifted from nominal 22.9 m³/h.',
    physical_mechanism: 'Valve XMV_8 modulates finished product delivery to storage. Variations disrupt overall plant mass balance.',
    solution_steps: [
      'Calibrate flow control loop FIC-502 to maintain 22.9 m³/h.',
      'Verify bottoms pump discharge pressure.',
      'Ensure stripper sump level is stabilized at 50%.'
    ],
    emergency_action: 'Lock valve XMV_8 in auto level cascade.',
    nominal_baseline: '22.9 m3/h'
  },

  XMEAS_37: { sensor_id: 'XMEAS_37', name: 'Product Comp D', component_name: 'Product Stream Gas Chromatograph GC-3', equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)', component_type: 'Product Quality Analyzer', actuator_tag: 'XMV_9', pid_tag: 'AIC-501', is_thermal: false, overheat_diagnosis: 'PRODUCT PURITY OFF-SPEC: Residual Component D impurity in product stream drifted from 0.15 mol%.', physical_mechanism: 'Reboiler steam duty directly determines separation of light D from heavy products G and H.', solution_steps: ['Adjust reboiler steam flow to 1085 kg/h to strip light components overhead.', 'Verify column temperature profile.'], emergency_action: 'Recycle off-spec product to feed tank if D exceeds 0.35 mol%.', nominal_baseline: '0.15 mol%' },
  XMEAS_38: { sensor_id: 'XMEAS_38', name: 'Product Comp E', component_name: 'Product Stream Gas Chromatograph GC-3', equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)', component_type: 'Product Quality Analyzer', actuator_tag: 'XMV_9', pid_tag: 'AIC-502', is_thermal: false, overheat_diagnosis: 'PRODUCT PURITY OFF-SPEC: Residual Component E impurity in product stream drifted from 0.85 mol%.', physical_mechanism: 'Stripping tray efficiency controls stripping of residual E from finished product.', solution_steps: ['Tune reboiler steam duty to strip E overhead.', 'Inspect GC-3 column separation peak.'], emergency_action: 'Maintain column temperature at 65.7 °C.', nominal_baseline: '0.85 mol%' },
  XMEAS_39: { sensor_id: 'XMEAS_39', name: 'Product Comp F', component_name: 'Product Stream Gas Chromatograph GC-3', equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)', component_type: 'Product Quality Analyzer', actuator_tag: 'XMV_9', pid_tag: 'AIC-503', is_thermal: false, overheat_diagnosis: 'INERT CONTAMINATION: Component F in product stream drifted from 0.05 mol%.', physical_mechanism: 'Inert F should be completely stripped overhead; presence in bottoms indicates column stripping failure.', solution_steps: ['Ensure reboiler temperature is at least 65.7 °C.', 'Check column feed tray location.'], emergency_action: 'Increase steam flow by 5% to purge light inerts.', nominal_baseline: '0.05 mol%' },
  XMEAS_40: { sensor_id: 'XMEAS_40', name: 'Product Comp G', component_name: 'Product Stream Gas Chromatograph GC-3', equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)', component_type: 'Primary Product Purity Assay', actuator_tag: 'XMV_2 / XMV_10', pid_tag: 'AIC-504 / Target Product G', is_thermal: false, overheat_diagnosis: 'PRIMARY PRODUCT G OFF-SPEC: Concentration of desired Product G drifted from target 53.75 mol%.', physical_mechanism: 'Product G selectivity is governed by reactor temperature and Reactant D feed rate. Core overheating alters reaction kinetics, hurting G yield.', solution_steps: ['Stabilize reactor core temperature at 120.4 °C to maintain optimal reaction selectivity for G.', 'Calibrate Reactant D feed rate (Stream 2) to 3664 kg/h.', 'Confirm GC-3 Product G assay reads 53.75 mol%.'], emergency_action: 'Tune Reactant D/E ratio to re-align product selectivity.', nominal_baseline: '53.75 mol%' },
  XMEAS_41: { sensor_id: 'XMEAS_41', name: 'Product Comp H', component_name: 'Product Stream Gas Chromatograph GC-3', equipment_unit: 'Product Stripper Column (UNIT_STRIPPER)', component_type: 'Co-Product Purity Assay', actuator_tag: 'XMV_3 / XMV_10', pid_tag: 'AIC-505 / Target Product H', is_thermal: false, overheat_diagnosis: 'CO-PRODUCT H OFF-SPEC: Concentration of co-product H drifted from target 43.85 mol%.', physical_mechanism: 'Reaction kinetics for H depend directly on Reactant E feed and reactor temperature stability.', solution_steps: ['Align Reactant E feed rate (Stream 3) to 4505 kg/h.', 'Keep reactor core temperature stabilized at 120.4 °C.', 'Verify Product H concentration stabilizes at 43.85 mol%.'], emergency_action: 'Adjust feed ratio controllers to balance G/H split.', nominal_baseline: '43.85 mol%' },

  // =========================================================================
  // UNIT_FEED (Reactant Feed System)
  // =========================================================================
  XMEAS_1: {
    sensor_id: 'XMEAS_1',
    name: 'A Feed Flow',
    component_name: 'Reactant A Flow Control Valve (XMV_1) & Positive Displacement Metering Pump',
    equipment_unit: 'Reactant Feed System (UNIT_FEED)',
    component_type: 'Liquid Metering Pump & Control Valve Header',
    actuator_tag: 'XMV_1 (Reactant A Valve)',
    pid_tag: 'FIC-001 / Stream 1 Flow',
    is_thermal: false,
    overheat_diagnosis: 'FEED RATE IMBALANCE TRIGGERING RUNAWAY: Reactant A feed rate deviated from 0.2505 kscmh. An excess of A accelerates core exothermic reaction rates, causing reactor overheating.',
    physical_mechanism: 'Reactant A feeds directly into the exothermic synthesis of products G and H. A surge in A feed flow drives intense chemical heat generation inside the CSTR, overwhelming jacket cooling.',
    solution_steps: [
      'Stroke Reactant A Control Valve XMV_1 to re-establish nominal 0.2505 kscmh flow rate.',
      'Check metering pump P-101 discharge pressure and dampener bladder.',
      'If reactor is currently overheating, trim A feed flow by 15% to suppress heat release rate.'
    ],
    emergency_action: 'Trip Reactant A feed pump if reactor temperature exceeds 132 °C safety threshold.',
    nominal_baseline: '0.2505 kscmh'
  },

  XMEAS_2: {
    sensor_id: 'XMEAS_2',
    name: 'D Feed Flow',
    component_name: 'Reactant D Feed Control Valve (XMV_2) & Mass Flowmeter Header',
    equipment_unit: 'Reactant Feed System (UNIT_FEED)',
    component_type: 'Liquid Transfer Header & Control Valve',
    actuator_tag: 'XMV_2 (Reactant D Valve)',
    pid_tag: 'FIC-002 / Stream 2 Flow',
    is_thermal: false,
    overheat_diagnosis: 'REACTANT D RATE SURGE: Feed rate deviated from 3664.0 kg/h, driving exothermic synthesis of Product G and escalating reactor heat release.',
    physical_mechanism: 'Reactant D is consumed in the primary exothermic reaction A + C + D -> G. Over-feeding D accelerates reactor heat generation.',
    solution_steps: [
      'Calibrate Reactant D mass flow controller FIC-002 to maintain 3664.0 kg/h.',
      'Verify feed storage tank booster pump pressure.',
      'Trim valve XMV_2 if reactor core temperature is currently elevated.'
    ],
    emergency_action: 'Throttle valve XMV_2 to 80% nominal to slow heat generation.',
    nominal_baseline: '3664.0 kg/h'
  },

  XMEAS_3: {
    sensor_id: 'XMEAS_3',
    name: 'E Feed Flow',
    component_name: 'Reactant E Feed Control Valve (XMV_3) & Transfer Line',
    equipment_unit: 'Reactant Feed System (UNIT_FEED)',
    component_type: 'Liquid Transfer Header & Control Valve',
    actuator_tag: 'XMV_3 (Reactant E Valve)',
    pid_tag: 'FIC-003 / Stream 3 Flow',
    is_thermal: false,
    overheat_diagnosis: 'REACTANT E RATE DRIFT: Feed rate drifted from 4505.0 kg/h, altering reaction stoichiometry and product H formation rate.',
    physical_mechanism: 'Reactant E participates in the exothermic synthesis of Product H. Flow drifts upset the thermal and stoichiometric balance.',
    solution_steps: [
      'Regulate Valve XMV_3 to stabilize Reactant E delivery at 4505.0 kg/h.',
      'Inspect mass flowmeter signal cable and transmitter zero.',
      'Verify storage tank suction level.'
    ],
    emergency_action: 'Re-align flow setpoint with product H quality assay.',
    nominal_baseline: '4505.0 kg/h'
  },

  XMEAS_4: {
    sensor_id: 'XMEAS_4',
    name: 'A+C Mixed Feed Flow',
    component_name: 'Stream 4 Mixed Feed Control Valve (XMV_4) & Compressor Influx Header',
    equipment_unit: 'Reactant Feed System (UNIT_FEED)',
    component_type: 'Gas Manifold & Mixing Control Valve',
    actuator_tag: 'XMV_4 (A+C Mixed Valve)',
    pid_tag: 'FIC-004 / Stream 4 Flow',
    is_thermal: false,
    overheat_diagnosis: 'MIXED GAS SUPPLY DRIFT: Mixed reactant feed rate deviated from 9.34 kscmh, altering reactor total gas throughput and stoichiometry.',
    physical_mechanism: 'Stream 4 supplies primary gaseous reactants A & C. Delivery changes alter reactor gas residence time and partial pressures.',
    solution_steps: [
      'Modulate control valve XMV_4 to re-establish 9.34 kscmh throughput.',
      'Check upstream supply pressure from Reactants A & C vaporizer headers.',
      'Verify combined feed Stream 6 stabilizes at 42.3 kscmh.'
    ],
    emergency_action: 'Lock valve XMV_4 at 50% stroke if pressure regulator oscillates.',
    nominal_baseline: '9.34 kscmh'
  }
};

/**
 * Returns the domain-grounded diagnostic & solution package for any sensor ID.
 */
export function getSensorSolution(sensorId, currentValue, normalValue, primaryUnit) {
  const fallback = {
    sensor_id: sensorId,
    name: sensorId,
    component_name: `Process Component for ${sensorId}`,
    equipment_unit: primaryUnit || 'Industrial Process Unit',
    component_type: 'Process Instrumentation Loop',
    actuator_tag: 'Local Control Loop Actuator',
    pid_tag: 'Loop Controller',
    is_thermal: false,
    overheat_diagnosis: `COMPONENT ANOMALY: Sensor ${sensorId} has deviated from nominal operating state (${normalValue}).`,
    physical_mechanism: 'Process deviation detected in the flowsheet topology causing downstream cascade disturbances.',
    solution_steps: [
      `Inspect component calibration and wiring for ${sensorId}.`,
      `Adjust associated actuator to re-establish nominal operating baseline of ${normalValue}.`,
      'Verify upstream and downstream process parameters restabilize.'
    ],
    emergency_action: 'Engage manual loop bypass if deviation exceeds alarm thresholds.',
    nominal_baseline: `${normalValue}`
  };

  const sol = SENSOR_SOLUTIONS[sensorId] || fallback;

  // Calculate dynamic deviation
  let devPercent = 0;
  if (currentValue !== undefined && normalValue !== 0) {
    devPercent = ((currentValue - normalValue) / normalValue) * 100;
  }

  // Check if machine is overheating
  const isElevated = currentValue > normalValue;
  const isOverheatingAlert = sol.is_thermal && isElevated && Math.abs(devPercent) >= 2.0;

  return {
    ...sol,
    current_value: currentValue,
    dev_percent: devPercent,
    is_overheated: isOverheatingAlert,
    formatted_dev: `${devPercent > 0 ? '+' : ''}${devPercent.toFixed(1)}%`
  };
}
