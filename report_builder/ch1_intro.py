import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_table_data
)

def build_chapter_1(doc):
    add_chapter_header(doc, 1, "Introduction")

    add_section_heading(doc, "1.1 Industrial Background & Continuous Manufacturing")
    add_paragraph(doc, (
        "In the contemporary process systems engineering domain, large-scale chemical manufacturing "
        "facilities represent the backbone of global industrial production, supplying bulk petrochemicals, "
        "specialty polymers, fertilizers, and active pharmaceutical ingredients. Unlike discrete manufacturing "
        "paradigms—where operations occur in isolated, mechanically decoupled cells—continuous chemical "
        "processes operate under rigorous multi-physics coupling. Chemical reactors, flash separators, "
        "distillation and stripping columns, heat exchangers, and recycle gas compressors are physically "
        "linked through complex piping networks and high-throughput material streams. Material and energy "
        "recycle loops are deliberately engineered into the process topology to maximize thermodynamic "
        "efficiency, capture unreacted raw precursors, minimize waste discharge, and reduce operating expenditures."
    ))
    add_paragraph(doc, (
        "However, these very same recycle loops introduce severe non-linear dynamic feedback mechanisms into "
        "the physical plant. A chemical facility is never static; it experiences continuous thermodynamic, "
        "kinetic, and fluid dynamic disturbances originating from raw feed variations, ambient temperature "
        "cycles, catalyst decay, valve stiction, and heat exchanger fouling. To maintain operational stability, "
        "Distributed Control Systems (DCS) and Supervisory Control and Data Acquisition (SCADA) platforms "
        "continuously ingest high-frequency telemetry from thousands of process sensors. When local control "
        "loops fail to reject an anomaly, the plant drifts from its nominal operating envelope, threatening "
        "equipment integrity, personnel safety, environmental compliance, and plant economic viability."
    ))

    add_section_heading(doc, "1.2 The Industrial Dilemma: Alarm Flooding & Cascading Failures")
    add_paragraph(doc, (
        "When an anomalous disturbance or equipment failure manifests in a modern process facility—such as a "
        "cooling water pump trip, valve stem packing failure, or feed composition step change—the physical perturbation "
        "does not remain localized to the initiating piece of equipment. Due to rapid fluid convective transport and vapor-liquid "
        "equilibrium shifts, the disturbance propagates downstream through product transfer lines and upstream through "
        "gas recycle headers within seconds. Consequently, a single initiating root cause triggers a massive surge of "
        "correlated high/low alarms across disparate unit operations."
    ))
    add_paragraph(doc, (
        "In modern chemical facilities, it is not uncommon for a single component anomaly to unleash over 300 to 500 "
        "alarms within a 10-minute window. This pathological phenomenon is formally termed an ‘Alarm Flood’ in the "
        "ISA-18.2 / IEC 62682 alarm management standards. Under an alarm flood condition, human control room operators "
        "are subjected to extreme cognitive overload. The human brain cannot parse 50 alarm messages per minute while "
        "simultaneously diagnosing multi-variable non-linear differential algebraic equations in real time. As a direct "
        "consequence, operators are frequently unable to isolate the true initiating root cause, leading to misdiagnoses, "
        "inappropriate manual control actions, emergency automated plant trips, or in catastrophic scenarios, runaway "
        "exothermic explosions and toxic atmospheric releases."
    ))

    add_section_heading(doc, "1.3 Purpose and Significance of the Project")
    add_paragraph(doc, (
        "The purpose of this capstone research project is to develop, evaluate, and demonstrate an autonomous, "
        "explainable, and deterministic Industrial AI Root-Cause Analysis (RCA) Agent capable of resolving alarm floods "
        "in real time. The proposed solution bridges the critical divide between deep statistical anomaly detection "
        "and physical engineering knowledge by coupling dynamic time-series inference with ontological Piping and "
        "Instrumentation Diagram (P&ID) topology."
    ))
    add_paragraph(doc, (
        "Conventional artificial intelligence approaches in industrial process monitoring suffer from two severe polar defects: "
        "(1) Purely data-driven black-box neural networks (such as deep autoencoders, CNNs, or LSTMs) can detect anomalies "
        "with high sensitivity but fail to provide transparent physical rationales or distinguish between an initiating cause "
        "and downstream operational symptoms; (2) Generative Large Language Models (LLMs) possess extraordinary reasoning "
        "capabilities but suffer from ungrounded hallucinations, fabricating imaginary chemical reactions or misidentifying "
        "actuator tags when detached from verified mathematical and physical constraints."
    ))
    add_paragraph(doc, (
        "This project pioneers a hybrid, cyber-physical architecture where deep learning detects statistical excursions, "
        "a Tri-Modal Causal Engine (incorporating Temporal Precedence, Graph-Theoretic P&ID proximity, and Granger Causality) "
        "determines the true initiating failure, and a LangGraph-orchestrated LLM verbalizes the exact mathematical ranking "
        "into clear, actionable operator guidance and automated actuator mitigations. The significance of this research lies in "
        "its ability to convert overwhelming alarm floods into immediate, trusted, and verified operator recovery steps."
    ))

    add_section_heading(doc, "1.4 Core System Features & Technological Innovations")
    add_paragraph(doc, (
        "The engineered Explainable Industrial AI Root-Cause Agent incorporates several state-of-the-art features designed "
        "specifically for mission-critical chemical plant environments:"
    ))
    add_bullet(doc, "Full 43-channel continuous telemetry streaming at 1 Hz across the Tennessee Eastman Process flowsheet, simulating first-principles non-linear differential equations of 6 coupled units.", bold_prefix="Comprehensive TEP Simulation")
    add_bullet(doc, "High-performance time-series ingestion utilizing PostgreSQL hypertables with columnar chunk compression and optimized sliding-window retrieval.", bold_prefix="TimescaleDB Storage Engine")
    add_bullet(doc, "PyTorch-based deep LSTM Autoencoder network calculating continuous multi-sensor reconstruction error with dynamic 3-sigma excursion thresholds.", bold_prefix="Deep Anomaly Detection")
    add_bullet(doc, "Neo4j property graph encoding complete chemical plant equipment, process sensors, material piping streams, and known physical failure modes.", bold_prefix="Ontological Knowledge Graph")
    add_bullet(doc, "Deterministic mathematical fusion uniting temporal anomaly lead times, directed graph flow proximity, and Vector Autoregression (VAR) Granger causality.", bold_prefix="Tri-Modal Causal Engine")
    add_bullet(doc, "Algorithmic regression pruning reducing pairwise causal analysis across all 43 continuous channels from 35.4 seconds to 1.2 seconds.", bold_prefix="Sub-2-Second Real-Time Latency")
    add_bullet(doc, "Locally hosted Mistral-7B LLM guided by LangGraph state machines, enforcing strict mathematical grounding with verified zero hallucinations.", bold_prefix="Grounded LLM Verbalization")
    add_bullet(doc, "React 18 and Cytoscape.js operator interface featuring per-machine subgraph filtering, live Recharts telemetry trends, interactive downside component diagnosis drawers, and one-click closed-loop valve mitigation.", bold_prefix="Interactive Operator Dashboard")

    add_section_heading(doc, "1.5 Formal Project Objectives")
    add_paragraph(doc, "To establish rigorous engineering criteria, the project defined the following core academic and practical objectives:")
    add_bullet(doc, "Accurately simulate the complete non-linear dynamics of the Tennessee Eastman continuous chemical plant, including all 41 continuous process sensors, 12 manipulated valves, and 21 standard process disturbance modes (IDV 1 to IDV 21).", bold_prefix="Objective 1: Multi-Physics Simulation")
    add_bullet(doc, "Implement an automated anomaly detection subsystem capable of flagging abnormal process excursions within 15 seconds of physical disturbance onset with a false positive rate below 3.0%.", bold_prefix="Objective 2: Rapid Anomaly Flagging")
    add_bullet(doc, "Construct an ontological property graph in Neo4j representing all units, piping connections, stream directions, sensor measurement tags, and operational interlocks.", bold_prefix="Objective 3: Ontological Modeling")
    add_bullet(doc, "Formulate and validate a mathematically sound composite causal scoring algorithm that synthesizes temporal lead times, topological shortest-path distances, and statistical Granger F-test statistics.", bold_prefix="Objective 4: Deterministic Causal Fusion")
    add_bullet(doc, "Optimize causal regression computation to guarantee real-time execution (< 2.0 seconds) on standard workstation hardware without requiring GPU clusters.", bold_prefix="Objective 5: Real-Time Latency Optimization")
    add_bullet(doc, "Achieve over 95% top-1 root-cause identification accuracy across benchmark fault scenarios while ensuring 100% factual faithfulness in LLM-generated recommendations.", bold_prefix="Objective 6: Diagnostic Accuracy & Faithfulness")
    add_bullet(doc, "Deliver a responsive, industrial-grade operator dashboard equipped with interactive graph navigation, downside component remediation steps, and automated closed-loop mitigation actions.", bold_prefix="Objective 7: Operator Decision Support")

    add_section_heading(doc, "1.6 Industrial Scope, Boundary Conditions & Assumptions")
    add_paragraph(doc, (
        "The engineering scope of this project encompasses continuous chemical plant operations, focusing specifically on the "
        "widely accepted Tennessee Eastman Process benchmark developed by the Eastman Chemical Company. The boundary conditions "
        "and working assumptions governing this investigation are delineated as follows:"
    ))
    add_bullet(doc, "The process simulation models continuous steady-state and dynamic transient operations under nominal production Mode 1 (Base Case 50/50 G/H product ratio).", bold_prefix="Operational Regime")
    add_bullet(doc, "Process measurements consist of 41 continuous sensor variables (temperatures, pressures, flow rates, levels, analyzer compositions) and 12 manipulated valve positions, sampled uniformly at 1-second intervals.", bold_prefix="Data Ingestion Boundary")
    add_bullet(doc, "The physical plant boundary comprises five primary processing units: Two-phase CSTR Reactor, Product Condenser, Vapor-Liquid Flash Separator, Recycle Gas Compressor, and Reboiled Stripper Column.", bold_prefix="Unit Battery Limits")
    add_bullet(doc, "Sensor measurements are subjected to Gaussian white noise and realistic calibration drifts to replicate actual industrial instrumentation performance.", bold_prefix="Instrumentation Noise Model")
    add_bullet(doc, "Safety interlock trip envelopes are parameterized based on Eastman Chemical engineering specifications (e.g., maximum reactor pressure of 3,000 kPa gauge and maximum temperature of 175 °C).", bold_prefix="Safety Constraints")
    add_bullet(doc, "The LLM inference runtime is hosted strictly on local premises via LM Studio (Mistral-7B Instruct), preventing proprietary industrial telemetry from traversing external public networks.", bold_prefix="Cybersecurity & Data Privacy")

    add_section_heading(doc, "1.7 Industrial Standards Compliance (ISA-18.2, IEC 62682 & OSHA PSM)")
    add_paragraph(doc, (
        "To ensure seamless industrial adoption, the system architecture adheres strictly to globally recognized industrial process "
        "safety and alarm management standards. In conventional process plants, poor alarm management directly breaches regulatory "
        "compliance frameworks. Table 1.1 delineates how the Explainable Industrial AI Root-Cause Agent maps directly to industrial standards."
    ))

    std_headers = ["Standard / Regulation", "Key Regulatory Requirement", "Traditional SCADA Failure", "Proposed AI System Solution"]
    std_data = [
        ["ANSI/ISA-18.2-2016", "Limit alarm flood to < 10 alarms per 10 minutes", "Generates 300+ raw alarms during unit trips", "Collapses flood into single ranked causal origin in 1.2s"],
        ["IEC 62682 Edition 1.1", "Provide actionable operator guidance and clear priority", "Displays flashing red alarms without recovery steps", "Presents component-level downside drawer with action steps"],
        ["OSHA 1910.119 (PSM)", "Process safety information & operating procedures", "Paper operating manuals often inaccessible during trips", "Incorporate verified Case-Based Reasoning procedures"],
        ["API RP 754", "Leading process safety indicators and trip prevention", "Reacts after safety relief valves lift and vent gas", "Early 3-sigma anomaly flagging permits proactive mitigation"],
        ["IEC 61508 / 61511", "Functional safety & Safety Instrumented Systems (SIS)", "Black-box AI is forbidden in safety loops", "Deterministic mathematical fusion guarantees explainability"]
    ]
    add_table_data(doc, std_headers, std_data, [1.4, 2.0, 1.8, 2.0])

    add_section_heading(doc, "1.8 Organization of the Report")
    add_paragraph(doc, (
        "This project report is systematically organized into ten comprehensive chapters designed to document the academic, "
        "mathematical, and engineering aspects of the research:"
    ))
    add_bullet(doc, "Establishes industrial context, multi-physics recycling challenges, alarm flood dilemmas, formal objectives, scope, and regulatory standards compliance.", bold_prefix="Chapter 1: Introduction")
    add_bullet(doc, "Provides deep problem definition, operational challenges, legacy SCADA limitations, proposed system innovations, functional requirements, and hardware/software matrices.", bold_prefix="Chapter 2: System Analysis")
    add_bullet(doc, "Details the chemical kinetics, reaction mechanisms, stream thermodynamic balances, exhaustive tables of 41 continuous sensors and 12 actuators, and the 21 benchmark fault modes.", bold_prefix="Chapter 3: Dataset Description")
    add_bullet(doc, "Reviews the technology stack (Python, React 18, Cytoscape, FastAPI, PyTorch, Neo4j, TimescaleDB, LangGraph) and presents operator dashboard screenshots and UI walkthroughs.", bold_prefix="Chapter 4: Technologies Used")
    add_bullet(doc, "Presents mathematical formulations for LSTM reconstruction error, temporal precedence lead, Dijkstra P&ID proximity, Granger VAR F-tests, composite causal scoring, and CBR.", bold_prefix="Chapter 5: Methods & Mathematical Algorithms")
    add_bullet(doc, "Details 5-tier architecture topology, data flow lifecycles, project Gantt chart, TimescaleDB DDL, Neo4j property graph schema, and execution flowcharts.", bold_prefix="Chapter 6: System Design")
    add_bullet(doc, "Walks through codebase implementation, FastAPI routes, CausalReasoningEngine, Neo4j Cypher procedures, React downside drawers, and automated plant simulation cascades.", bold_prefix="Chapter 7: Implementation Details")
    add_bullet(doc, "Documents 15-case QA test report matrix, execution latency benchmarks (35.4s to 1.2s), 21-fault diagnostic accuracy benchmarks, ablation studies, and case studies (IDV 4 & IDV 1).", bold_prefix="Chapter 8: Results and Discussion")
    add_bullet(doc, "Summarizes core contributions, prototype limitations, and outlines future roadmaps including OPC-UA integration, automated P&ID scanning, and reinforcement learning mitigation.", bold_prefix="Chapter 9: Conclusion & Future Scope")
    add_bullet(doc, "Provides a formal academic bibliography comprising 35+ peer-reviewed citations across process systems engineering, causal inference, and industrial AI.", bold_prefix="Chapter 10: References & Bibliography")

    doc.add_page_break()
