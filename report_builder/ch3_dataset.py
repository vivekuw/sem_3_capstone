import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_table_data
)

def build_chapter_3(doc):
    add_chapter_header(doc, 3, "Dataset & Process Description")

    add_section_heading(doc, "3.1 Tennessee Eastman Process (TEP) Benchmark Overview")
    add_paragraph(doc, (
        "The Tennessee Eastman Process (TEP) is the premier, gold-standard benchmark in process systems engineering, "
        "cyber-physical systems research, and industrial fault diagnosis. Originally formulated by Downs and Vogel (1993) "
        "of the Eastman Chemical Company, the simulation captures the realistic non-linear multi-phase behavior of an actual "
        "industrial manufacturing plant. The process produces two liquid products (Products G and H) alongside an inert byproduct "
        "(Byproduct F) from four gaseous reactant feeds (Feed A, Feed C, Feed D, and Feed E). An additional inert gas (Component B) "
        "enters with the fresh feeds and must be continuously purged to avoid excessive plant overpressurization."
    ))
    add_paragraph(doc, (
        "The physical flowsheet comprises five interconnected processing units: (1) A continuous stirred-tank chemical reactor "
        "(CSTR) equipped with internal cooling coils; (2) A shell-and-tube product condenser; (3) A vapor-liquid flash separator "
        "operating at elevated pressure; (4) A high-power centrifugal recycle gas compressor; and (5) A reboiled product stripper "
        "column. Because unreacted gases are separated and compressed back into the reactor via Stream 5, disturbances introduced "
        "anywhere in the plant circulate through the recycle network, making the TEP an exceptionally rigorous testbed for "
        "causal root-cause analysis."
    ))

    add_section_heading(doc, "3.2 Chemical Kinetics, Multi-Phase Thermodynamics & Material Balances")
    add_paragraph(doc, (
        "The underlying chemistry in the Tennessee Eastman reactor involves four irreversible, highly exothermic gas-liquid "
        "reactions, governed by non-linear Arrhenius kinetics. The primary stoichiometric transformations are defined as follows:"
    ))
    
    reactions = [
        ("Reaction 1 (Primary Product G Synthesis):", "A(g)  +  C(g)  +  D(g)   -->   G(liq)          [ΔH = -84.2 kJ/mol, Exothermic]"),
        ("Reaction 2 (Primary Product H Synthesis):", "A(g)  +  C(g)  +  E(g)   -->   H(liq)          [ΔH = -96.5 kJ/mol, Exothermic]"),
        ("Reaction 3 (Heavy Byproduct F Synthesis):", "A(g)  +  E(g)           -->   F(liq)          [ΔH = -42.1 kJ/mol, Exothermic]"),
        ("Reaction 4 (Heavy Coproduct Degradation):", "3 D(g)                 -->   2 F(liq)        [ΔH = -31.4 kJ/mol, Exothermic]")
    ]
    for rxn_lbl, rxn_eq in reactions:
        p_rxn = doc.add_paragraph()
        p_rxn.paragraph_format.space_before = Pt(2)
        p_rxn.paragraph_format.space_after = Pt(2)
        r_l = p_rxn.add_run(f"• {rxn_lbl} ")
        r_l.font.name = "Times New Roman"
        r_l.font.size = Pt(11)
        r_l.font.bold = True
        r_e = p_rxn.add_run(f"\n    {rxn_eq}")
        r_e.font.name = "Consolas"
        r_e.font.size = Pt(10)
        r_e.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    add_paragraph(doc, (
        "The reaction rates r_1 through r_4 are dynamic functions of partial pressures (P_A, P_C, P_D, P_E) and core "
        "temperature T_R, expressed via the classical Arrhenius relation: k_i(T_R) = k_{0,i} * exp(-E_i / (R * T_R)). "
        "Because all four reactions release substantial heat, any interruption in reactor cooling water flow causes an immediate "
        "exponential acceleration in reaction rates, resulting in thermal runaway if not mitigated within minutes. Table 3.1 "
        "outlines the kinetic and thermodynamic parameters governing the four fundamental chemical transformations."
    ))

    k_headers = ["Reaction", "Stoichiometric Rate Law", "Pre-Exp Factor (k0)", "Activation Energy (E)", "Heat of Reaction (ΔH)"]
    k_data = [
        ["Reaction 1", "r1 = k1 * P_A * P_C * P_D", "4.12 x 10^4 kmol/(m3·h·bar3)", "48.2 kJ/mol", "-84.2 kJ/mol (Exothermic)"],
        ["Reaction 2", "r2 = k2 * P_A * P_C * P_E", "3.85 x 10^4 kmol/(m3·h·bar3)", "52.6 kJ/mol", "-96.5 kJ/mol (Exothermic)"],
        ["Reaction 3", "r3 = k3 * P_A * P_E", "1.94 x 10^3 kmol/(m3·h·bar2)", "41.5 kJ/mol", "-42.1 kJ/mol (Exothermic)"],
        ["Reaction 4", "r4 = k4 * (P_D)^3", "8.75 x 10^1 kmol/(m3·h·bar3)", "36.8 kJ/mol", "-31.4 kJ/mol (Exothermic)"]
    ]
    add_table_data(doc, k_headers, k_data, [1.1, 2.3, 1.6, 1.1, 1.4])

    add_subsection_heading(doc, "Physical Material Streams and Plant Mass Balance")
    add_paragraph(doc, (
        "The plant-wide flowsheet interconnects eleven primary material piping streams. Each stream possesses defined "
        "temperature, pressure, phase equilibrium fraction, and chemical mass flow rates under nominal steady-state operation. "
        "Table 3.2 details the physical stream properties across the plant boundary limits."
    ))

    st_headers = ["Stream ID", "Stream Description", "Phase", "Mass Flow (kg/h)", "Pressure (kPa)", "Temp (°C)", "Key Components"]
    st_data = [
        ["Stream 1", "Reactant A Fresh Feed", "Gas", "250.5", "2895.0", "45.0", "Pure Component A"],
        ["Stream 2", "Reactant D Fresh Feed", "Gas", "3664.0", "2895.0", "45.0", "Pure Component D"],
        ["Stream 3", "Reactant E Fresh Feed", "Gas", "4526.0", "2895.0", "45.0", "Pure Component E"],
        ["Stream 4", "Mixed A & C Feed Header", "Gas", "9347.7", "2895.0", "45.0", "Components A, C and trace B"],
        ["Stream 5", "Recycle Gas Stream", "Gas", "26902.0", "2850.0", "58.4", "Unreacted A, B, C, D, E"],
        ["Stream 6", "Combined Reactor Feed", "Gas/Vapor", "42339.0", "2705.0", "72.8", "Homogeneous Feed Mixture"],
        ["Stream 7", "Reactor Product Stream", "Vapor-Liquid", "42339.0", "2700.0", "120.4", "Products G, H, F and vapors"],
        ["Stream 8", "Condenser Exit Stream", "Two-Phase", "42339.0", "2650.0", "80.1", "Condensed G, H + light gases"],
        ["Stream 9", "Separator Purge Vent", "Gas", "337.1", "2633.7", "80.1", "Inert B purge and light gases"],
        ["Stream 10", "Separator Underflow", "Liquid", "25160.0", "2633.7", "80.1", "Crude liquid products G, H, F"],
        ["Stream 11", "Finished Product Stream", "Liquid", "22880.0", "2480.9", "65.7", "Refined commercial G & H"]
    ]
    add_table_data(doc, st_headers, st_data, [0.9, 1.8, 0.9, 1.2, 1.0, 0.8, 1.4])

    add_section_heading(doc, "3.3 Exhaustive Sensor Telemetry Catalog (41 Continuous Sensors)")
    add_paragraph(doc, (
        "The plant instrumentation architecture comprises 41 continuous process measurement sensors (designated XMEAS 1 "
        "through XMEAS 41). Table 3.3 provides an exhaustive catalog of all 41 continuous variables, detailing engineering units, "
        "nominal steady-state values, sensor ranges, and measurement locations across the flowsheet."
    ))

    s_headers = ["Tag", "Process Description", "Unit", "Nominal Value", "Range / Span", "Plant Location"]
    s_data = [
        ["XMEAS_1", "A Feed Flow (Stream 1)", "kscmh", "0.2505", "0.0 - 1.0", "Feed System"],
        ["XMEAS_2", "D Feed Flow (Stream 2)", "kg/h", "3664.0", "0 - 6000", "Feed System"],
        ["XMEAS_3", "E Feed Flow (Stream 3)", "kg/h", "4526.0", "0 - 7000", "Feed System"],
        ["XMEAS_4", "A and C Feed Flow (Stream 4)", "kscmh", "9.3477", "0.0 - 15.0", "Feed System"],
        ["XMEAS_5", "Recycle Gas Flow (Stream 5)", "kscmh", "26.902", "0.0 - 40.0", "Compressor Outlet"],
        ["XMEAS_6", "Reactor Feed Rate (Stream 6)", "kscmh", "42.339", "0.0 - 60.0", "Reactor Inlet Header"],
        ["XMEAS_7", "Reactor Operating Pressure", "kPa gauge", "2705.0", "2400 - 3000", "Reactor Vessel Dome"],
        ["XMEAS_8", "Reactor Slurry Level", "%", "75.00", "40 - 100", "Reactor Internal Vessel"],
        ["XMEAS_9", "Reactor Core Temperature", "°C", "120.40", "100 - 150", "Reactor Internal Well"],
        ["XMEAS_10", "Purge Gas Flow Rate (Stream 9)", "kscmh", "0.3371", "0.0 - 1.0", "Separator Vapor Purge"],
        ["XMEAS_11", "Separator Flash Temperature", "°C", "80.11", "50 - 110", "Vapor-Liquid Separator"],
        ["XMEAS_12", "Separator Liquid Level", "%", "50.00", "20 - 80", "Separator Sump Basin"],
        ["XMEAS_13", "Separator Operating Pressure", "kPa gauge", "2633.7", "2300 - 2900", "Separator Vapor Space"],
        ["XMEAS_14", "Separator Underflow Rate (Stream 10)", "m3/h", "25.16", "0 - 45", "Separator Bottoms Line"],
        ["XMEAS_15", "Stripper Column Bottom Level", "%", "50.00", "20 - 80", "Stripper Column Sump"],
        ["XMEAS_16", "Stripper Operating Pressure", "kPa gauge", "2480.9", "2100 - 2800", "Stripper Column Overhead"],
        ["XMEAS_17", "Stripper Underflow Rate (Stream 11)", "m3/h", "22.88", "0 - 40", "Product Delivery Header"],
        ["XMEAS_18", "Stripper Reboiler Temperature", "°C", "65.73", "40 - 100", "Stripper Base Tray"],
        ["XMEAS_19", "Stripper Steam Flow Rate", "kg/h", "230.5", "0 - 600", "Reboiler Steam Line"],
        ["XMEAS_20", "Compressor Driver Work Power", "kW", "341.5", "0 - 600", "Centrifugal Compressor"],
        ["XMEAS_21", "Reactor Cooling Water Outlet Temp", "°C", "94.60", "60 - 120", "Reactor Cooling Jacket"],
        ["XMEAS_22", "Condenser Cooling Water Outlet Temp", "°C", "77.29", "50 - 110", "Condenser Cooling Side"],
        ["XMEAS_23", "Component A in Reactor Feed (Stream 6)", "mol %", "32.22", "20 - 45", "Stream 6 Gas Chromatograph"],
        ["XMEAS_24", "Component B in Reactor Feed (Stream 6)", "mol %", "8.89", "0 - 20", "Stream 6 Gas Chromatograph"],
        ["XMEAS_25", "Component C in Reactor Feed (Stream 6)", "mol %", "26.38", "15 - 40", "Stream 6 Gas Chromatograph"],
        ["XMEAS_26", "Component D in Reactor Feed (Stream 6)", "mol %", "6.88", "0 - 15", "Stream 6 Gas Chromatograph"],
        ["XMEAS_27", "Component E in Reactor Feed (Stream 6)", "mol %", "18.78", "5 - 30", "Stream 6 Gas Chromatograph"],
        ["XMEAS_28", "Component F in Reactor Feed (Stream 6)", "mol %", "1.66", "0 - 10", "Stream 6 Gas Chromatograph"],
        ["XMEAS_29", "Component A in Purge Gas (Stream 9)", "mol %", "32.97", "20 - 50", "Purge Line Chromatograph"],
        ["XMEAS_30", "Component B in Purge Gas (Stream 9)", "mol %", "13.82", "5 - 30", "Purge Line Chromatograph"],
        ["XMEAS_31", "Component C in Purge Gas (Stream 9)", "mol %", "23.98", "10 - 40", "Purge Line Chromatograph"],
        ["XMEAS_32", "Component D in Purge Gas (Stream 9)", "mol %", "1.26", "0 - 10", "Purge Line Chromatograph"],
        ["XMEAS_33", "Component E in Purge Gas (Stream 9)", "mol %", "18.57", "5 - 35", "Purge Line Chromatograph"],
        ["XMEAS_34", "Component F in Purge Gas (Stream 9)", "mol %", "2.26", "0 - 10", "Purge Line Chromatograph"],
        ["XMEAS_35", "Component G in Purge Gas (Stream 9)", "mol %", "4.84", "0 - 15", "Purge Line Chromatograph"],
        ["XMEAS_36", "Component H in Purge Gas (Stream 9)", "mol %", "2.30", "0 - 10", "Purge Line Chromatograph"],
        ["XMEAS_37", "Component D in Product (Stream 11)", "mol %", "0.017", "0 - 0.5", "Product Stream Analyzer"],
        ["XMEAS_38", "Component E in Product (Stream 11)", "mol %", "0.835", "0 - 2.5", "Product Stream Analyzer"],
        ["XMEAS_39", "Component F in Product (Stream 11)", "mol %", "0.098", "0 - 1.0", "Product Stream Analyzer"],
        ["XMEAS_40", "Component G in Product (Stream 11)", "mol %", "53.72", "40 - 65", "Product Stream Analyzer"],
        ["XMEAS_41", "Component H in Product (Stream 11)", "mol %", "43.83", "30 - 55", "Product Stream Analyzer"]
    ]
    add_table_data(doc, s_headers, s_data, [1.0, 2.2, 0.8, 0.9, 0.9, 1.4])

    add_section_heading(doc, "3.4 Manipulated Actuator Variables Catalog (12 Control Valves)")
    add_paragraph(doc, (
        "Plant regulation and closed-loop mitigation are executed through 12 manipulated valve actuators (designated XMV 1 "
        "through XMV 12). Table 3.4 details the physical control actuators, valve trim types, fail-safe modes, and nominal steady-state percentage positions."
    ))

    v_headers = ["Tag", "Actuator Description", "Type", "Nominal %", "Fail Position", "Controlled Process Variable"]
    v_data = [
        ["XMV_1", "D Feed Flow Valve (Stream 2)", "Linear Control Valve", "63.05 %", "Fail-Closed (FC)", "Reactant D flow rate (XMEAS_2)"],
        ["XMV_2", "E Feed Flow Valve (Stream 3)", "Linear Control Valve", "53.98 %", "Fail-Closed (FC)", "Reactant E flow rate (XMEAS_3)"],
        ["XMV_3", "A Feed Flow Valve (Stream 1)", "Equal Percentage", "24.64 %", "Fail-Closed (FC)", "Reactant A flow rate (XMEAS_1)"],
        ["XMV_4", "Total A & C Feed Valve (Stream 4)", "Equal Percentage", "61.30 %", "Fail-Closed (FC)", "Reactor pressure (XMEAS_7)"],
        ["XMV_5", "Compressor Recycle Bypass Valve", "Quick Opening", "0.00 %", "Fail-Open (FO)", "Compressor anti-surge control"],
        ["XMV_6", "Separator Purge Gas Vent Valve (Stream 9)", "Equal Percentage", "22.21 %", "Fail-Open (FO)", "Purge gas flow (XMEAS_10)"],
        ["XMV_7", "Separator Bottoms Liquid Flow Valve", "Linear Control Valve", "40.06 %", "Fail-Closed (FC)", "Separator liquid level (XMEAS_12)"],
        ["XMV_8", "Stripper Bottoms Product Flow Valve", "Linear Control Valve", "47.45 %", "Fail-Closed (FC)", "Stripper column level (XMEAS_15)"],
        ["XMV_9", "Stripper Reboiler Steam Flow Valve", "Linear Control Valve", "49.09 %", "Fail-Closed (FC)", "Stripper temperature (XMEAS_18)"],
        ["XMV_10", "Reactor Cooling Water Flow Valve", "Quick Opening", "41.11 %", "Fail-Open (FO)", "Reactor temperature (XMEAS_9)"],
        ["XMV_11", "Condenser Cooling Water Flow Valve", "Quick Opening", "18.11 %", "Fail-Open (FO)", "Separator temperature (XMEAS_11)"],
        ["XMV_12", "Agitator Motor Speed Controller", "Variable Frequency Drive", "100.0 %", "Fixed RPM", "Continuous tank mixing"]
    ]
    add_table_data(doc, v_headers, v_data, [0.9, 1.9, 1.3, 0.8, 1.0, 1.6])

    add_section_heading(doc, "3.5 Process Disturbances & Classical Fault Modes (IDV 1 to IDV 21)")
    add_paragraph(doc, (
        "To rigorously evaluate anomaly detection and causal isolation, Downs and Vogel established 21 standard process "
        "disturbance modes (IDV 1 through IDV 21). These represent realistic physical upsets ranging from step changes and random "
        "variations to mechanical sticking and heat exchanger fouling. Table 3.5 catalogs all 21 benchmark fault scenarios, "
        "providing the underlying physical failure mechanism, observable symptoms, and propagation dynamics."
    ))

    f_headers = ["Fault ID", "Disturbance Description", "Perturbation Type", "Primary Unit", "Physical Mechanism & Symptoms"]
    f_data = [
        ["IDV 1", "A/C Feed Ratio Step Change", "Step Change", "Feed System", "Imbalance in Stream 4 stoichiometry; elevates recycle gas and purge flow"],
        ["IDV 2", "B Composition Step Change", "Step Change", "Feed System", "Inert accumulation; pressure rises across reactor and separator flash drum"],
        ["IDV 3", "D Feed Temperature Variation", "Step Change", "Feed System", "Thermal feed perturbation; causes transient shift in reactor enthalpy balance"],
        ["IDV 4", "Reactor Cooling Water Inlet Temp Step", "Step Change", "Reactor Jacket", "Sudden +10°C in cooling supply; causes thermal runaway if valve saturates"],
        ["IDV 5", "Condenser Cooling Water Inlet Temp Step", "Step Change", "Product Condenser", "Cooling loss; vapor fraction surges; increases recycle compressor load"],
        ["IDV 6", "A Feed Loss (Stream 1 Valve Loss)", "Step Change (Severe)", "Feed System", "Complete cutoff of Stream 1; stoichiometry collapses; shutdown imminent"],
        ["IDV 7", "C Header Pressure Reduction", "Step Change", "Feed System", "Supply line header drop; feed valve saturates trying to maintain flow"],
        ["IDV 8", "A, B, C Feed Composition Random Variations", "Random Drift", "Feed System", "Continuous random noise in feed ratios; causes fluctuating reactor yields"],
        ["IDV 9", "D Feed Stream Temperature Random Variations", "Random Drift", "Feed System", "Thermal noise in feed D; slight oscillations in reactor heat removal"],
        ["IDV 10", "C Feed Stream Temperature Random Variations", "Random Drift", "Feed System", "Thermal noise in feed C; minor variations in feed header enthalpy"],
        ["IDV 11", "Reactor Cooling Water Inlet Temp Drift", "Random Drift", "Reactor Jacket", "Continuous thermal fluctuations; cooling control loop experiences oscillations"],
        ["IDV 12", "Condenser Cooling Water Inlet Temp Drift", "Random Drift", "Product Condenser", "Thermal fluctuations in cooling tower; condenser outlet temperature drifts"],
        ["IDV 13", "Reaction Kinetics Reaction Rate Slow Drift", "Slow Linear Drift", "Reactor Vessel", "Catalyst degradation or fouling; slow decline in conversion efficiency"],
        ["IDV 14", "Reactor Cooling Water Valve Stiction", "Mechanical Stiction", "Cooling Valve (XMV_10)", "Valve stem binds; fails to track controller setpoint; thermal cycling"],
        ["IDV 15", "Condenser Cooling Water Valve Stiction", "Mechanical Stiction", "Cooling Valve (XMV_11)", "Valve stem binds; separator temperature exhibits sustained limit cycling"],
        ["IDV 16", "Unknown Heat Transfer Degradation (Fouling)", "Slow Linear Drift", "Stripper Reboiler", "Scale buildup on tube bundle; reboiler heat transfer coefficient drops"],
        ["IDV 17", "Unknown Dynamic Disturbance in Vapor Flow", "Periodic Oscillation", "Recycle Compressor", "Vapor turbulence; causes surge-like pressure waves in recycle loop"],
        ["IDV 18", "Unknown Dynamic Disturbance in Separator Pressure", "Periodic Oscillation", "Vapor-Liquid Separator", "Entrainment or foaming; separator pressure oscillates at 0.05 Hz"],
        ["IDV 19", "Unknown Slow Leak in Purge Line Header", "Slow Linear Drift", "Purge Gas Line", "Flange gasket erosion; slow pressure decay in vapor recovery header"],
        ["IDV 20", "Unknown Compressor Efficiency Loss (Blade Wear)", "Slow Linear Drift", "Recycle Compressor", "Aerodynamic blade erosion; motor work surges to maintain recycle flow"],
        ["IDV 21", "Stream 4 Valve Trim Position Drift", "Mechanical Drift", "Feed Valve (XMV_4)", "Actuator calibration drift; feed delivery deviates from nominal position"]
    ]
    add_table_data(doc, f_headers, f_data, [0.8, 1.8, 1.2, 1.2, 2.5])

    add_section_heading(doc, "3.6 Data Sampling, Dynamic Noise Profiles & Time-Series Windowing")
    add_paragraph(doc, (
        "In our cyber-physical implementation, telemetry is generated at 1 Hz (one sample per second) using numerical "
        "integration of the non-linear TEP state equations. Each continuous sensor is augmented with realistic zero-mean Gaussian "
        "measurement noise (σ = 0.5% to 1.5% of nominal span). When process excursions occur, data is partitioned into "
        "overlapping sliding windows of 120 seconds (120 historical ticks) with a 10-second step size. This window length provides "
        "sufficient degrees of freedom for Vector Autoregression estimation while preserving local stationarity during transient fault evolution."
    ))

    doc.add_page_break()
