import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_figure, add_table_data
)

def build_chapter_2(doc):
    add_chapter_header(doc, 2, "System Analysis")

    add_section_heading(doc, "2.1 Problem Definition & Multi-Physics Bottleneck")
    add_paragraph(doc, (
        "In large-scale continuous manufacturing facilities, isolating the true root cause of an operational "
        "disturbance is extraordinarily challenging due to complex multi-physics coupling and dynamic recycling. "
        "Unlike discrete systems where components operate in isolated sequences, chemical manufacturing plants "
        "recirculate energy, vapors, and unreacted liquids across multiple interconnected units. When an initial "
        "hardware fault occurs—such as a cooling water heat exchanger fouling, a control valve sticking at 100%, "
        "or a feed stream pressure surge—the perturbation does not stay confined to the initiating piece of equipment."
    ))
    add_paragraph(doc, (
        "Instead, the disturbance propagates downstream via mass convective transfer and upstream through high-pressure "
        "gas recycle loops. Within minutes, process variables across the entire flowsheet deviate from steady-state targets. "
        "Sensors monitoring reactor pressure, separator temperature, compressor power, and stripper level all violate "
        "alarm boundaries nearly simultaneously. In traditional operations, this results in an overwhelming ‘alarm flood’ "
        "of 100 to 500 alerts within minutes, making it nearly impossible for control room operators to identify the true "
        "originating failure."
    ))

    add_figure(doc, "report_assets/fig1_problem_solution_flow.png", "Figure 2.1: Conceptual Comparison of Traditional Alarm Floods vs. Proposed Explainable Industrial AI Framework", width_inches=6.0)

    add_section_heading(doc, "2.2 System Analysis & Operational Challenges")
    add_paragraph(doc, (
        "System analysis involves a rigorous examination of the operational, statistical, and topological characteristics "
        "of continuous chemical facilities. In continuous process manufacturing, operational anomalies exhibit four fundamental "
        "characteristics that defeat conventional diagnostic tools:"
    ))
    add_bullet(doc, "Because unit operations exchange fluids at high velocity, a failure in one unit affects downstream vessels within 30 to 90 seconds and upstream vessels via recycle within 120 seconds.", bold_prefix="1. Dynamic Temporal Propagation")
    add_bullet(doc, "Chemical reactions exhibit Arrhenius-type exponential temperature dependencies. A 5 °C rise in reactor core temperature can double the reaction rate, causing sudden pressure spikes and rapid runaway kinetics.", bold_prefix="2. Strong Non-Linear Coupling")
    add_bullet(doc, "Industrial sensors are subject to electrical interference, flow turbulence, and thermal convection noise, requiring robust statistical filtering to avoid false alarms.", bold_prefix="3. Sensor Measurement Noise")
    add_bullet(doc, "Anomalies in different components often produce identical downstream symptom patterns (e.g., reactor overpressure can be caused by cooling water loss, feed ratio shifts, or purge valve blockage).", bold_prefix="4. Symptom Equifinality")

    add_section_heading(doc, "2.3 Current System (SCADA / DCS / Static Thresholds) & Critical Limitations")
    add_paragraph(doc, (
        "The current industrial standard relies on legacy Distributed Control Systems (DCS) and Supervisory Control and "
        "Data Acquisition (SCADA) platforms equipped with static high/low boundary alarms, combined with manual operator review "
        "and occasional black-box machine learning models."
    ))
    add_paragraph(doc, "The critical limitations inherent in the current state of industrial practice include:")
    add_bullet(doc, "Sensors trigger alarms independently whenever instantaneous values exceed fixed upper or lower limits (e.g., > 105 °C), ignoring physical coupling and temporal causality.", bold_prefix="Independent Static Thresholds")
    add_bullet(doc, "During a major process upset, the control room display becomes saturated with hundreds of cascading warning messages, obscuring the primary failure.", bold_prefix="Alarm Floods and Cognitive Overload")
    add_bullet(doc, "Traditional deep neural networks or autoencoders predict that an anomaly exists, but cannot provide operators with the physical mechanism, P&ID stream paths, or causal explanation.", bold_prefix="Lack of Physical Explainability")
    add_bullet(doc, "Operators must consult multiple static piping diagrams, paper operating manuals, and disparate screens to infer what went wrong, wasting precious minutes before safety interlocks trip the plant.", bold_prefix="Fragmented Operational Workflow")
    add_bullet(doc, "When modern Generative AI or LLMs are deployed without physical grounding, they hallucinate non-existent plant units or recommend dangerous control adjustments that violate physical laws.", bold_prefix="LLM Hallucination Vulnerability")

    add_subsection_heading(doc, "Comparative Paradigm Analysis: Industrial Process Monitoring")
    add_paragraph(doc, (
        "To clearly position the technological leap represented by the proposed system, Table 2.1 compares traditional industrial "
        "monitoring tools against the Explainable Industrial AI Agent."
    ))

    comp_headers = ["Evaluation Dimension", "Legacy SCADA / DCS", "Deep Neural Networks", "Unconstrained LLMs", "Proposed Industrial AI Agent"]
    comp_data = [
        ["Root-Cause Isolation", "None (Raw Alarms)", "Statistical classification", "Ungrounded narrative", "Tri-Modal Deterministic Ranking"],
        ["Handling Alarm Floods", "Poor (Floods Display)", "Consolidates features", "Overwhelmed by token limit", "Filters to root initiating node in 1.2s"],
        ["Physical Explainability", "Zero (Only tag & limit)", "Black-Box (Uninterpretable)", "Plausible but often hallucinated", "Strict P&ID flow hops & Granger proof"],
        ["Hallucination Vulnerability", "Not Applicable", "Not Applicable", "Extremely High (Hallucinates)", "Zero (Enforced by mathematical gates)"],
        ["Inference Latency", "< 0.1s (Independent)", "0.5s - 2.0s", "5.0s - 15.0s (Cloud)", "1.2s (Optimized on local workstation)"],
        ["Actionable Operator Guidance", "None (Manual lookup)", "None (Raw probability)", "Generic advice", "Step-by-step downside recovery actions"],
        ["Closed-Loop Mitigation", "Emergency trip interlocks", "None (Read-only)", "None (Unsafe)", "One-click safety-clamped valve control"]
    ]
    add_table_data(doc, comp_headers, comp_data, [1.4, 1.4, 1.3, 1.4, 1.7])

    add_section_heading(doc, "2.4 Proposed System: Grounded Multi-Modal Temporal-Ontological AI Agent")
    add_paragraph(doc, (
        "The proposed Explainable Industrial AI Root-Cause Agent addresses every limitation of legacy SCADA systems "
        "by combining first-principles physical knowledge with cutting-edge causal machine learning and grounded AI agent orchestration."
    ))
    add_paragraph(doc, (
        "Instead of treating sensors in isolation, the proposed system ingests high-frequency telemetry into TimescaleDB "
        "hypertables and evaluates continuous reconstruction loss using PyTorch LSTM Autoencoders. When abnormal excursions occur, "
        "the system triggers a Tri-Modal Causal Fusion Engine that simultaneously evaluates:"
    ))
    add_bullet(doc, "Determines which sensor exhibited the earliest statistically significant departure from nominal baseline, establishing true chronological priority.", bold_prefix="1. Temporal Precedence Lead Time")
    add_bullet(doc, "Traverses an ontological Neo4j property graph encoding physical P&ID stream connectivity, calculating shortest directed flow paths to enforce mass-flow conservation.", bold_prefix="2. Graph-Theoretic Physical Proximity")
    add_bullet(doc, "Performs Vector Autoregression (VAR) F-tests across time-series windows to statistically confirm that the candidate variable's history improves forecasting of coupled downstream variables.", bold_prefix="3. Granger Causality VAR Modeling")
    add_paragraph(doc, (
        "The resulting composite causal score produces a deterministic ranking of root-cause candidates. A LangGraph state machine "
        "passes this verified ranking, along with physical unit metadata and historical Case-Based Reasoning (CBR) matches, to a locally "
        "hosted Mistral-7B LLM. The LLM is strictly constrained to verbalize the mathematical diagnosis, completely eliminating "
        "hallucinations. Finally, the interactive React 18 dashboard presents operators with a per-machine knowledge graph, "
        "step-by-step downside recovery actions, and one-click closed-loop valve mitigation."
    ))

    add_section_heading(doc, "2.5 Comprehensive Requirement Analysis")
    add_paragraph(doc, "A comprehensive requirements specification was developed to guide engineering implementation:")
    
    add_subsection_heading(doc, "Functional Requirements (FR)")
    add_bullet(doc, "Continuously ingest 41 process sensors and 12 valve actuators at 1 Hz from the Tennessee Eastman simulation into TimescaleDB.", bold_prefix="FR-1: Real-Time Telemetry Ingestion")
    add_bullet(doc, "Evaluate PyTorch LSTM reconstruction error and flag deviations exceeding 3.0 standard deviations from nominal steady state.", bold_prefix="FR-2: Dynamic Anomaly Detection")
    add_bullet(doc, "Execute shortest-path Dijkstra traversals on Neo4j P&ID graphs between anomalous sensor nodes to quantify physical flow distance.", bold_prefix="FR-3: Ontological Graph Traversal")
    add_bullet(doc, "Compute pairwise Vector Autoregression (VAR) F-tests across sliding time-series windows to assess directional predictive causality.", bold_prefix="FR-4: Statistical Granger Causality")
    add_bullet(doc, "Synthesize temporal lead time, graph proximity, and Granger statistics into a unified composite root-cause score.", bold_prefix="FR-5: Composite Causal Ranking")
    add_bullet(doc, "Query historical incident knowledge bases to retrieve matching historical work orders and verified recovery procedures.", bold_prefix="FR-6: Case-Based Reasoning Retrieval")
    add_bullet(doc, "Generate verified, non-hallucinatory narrative diagnostic summaries and component-level remediation action items.", bold_prefix="FR-7: Grounded LLM Verbalization")
    add_bullet(doc, "Provide a browser-based dashboard with Cytoscape knowledge graph, live trend charts, component recovery drawers, and one-click mitigation.", bold_prefix="FR-8: Operator Interactive Interface")

    add_subsection_heading(doc, "Non-Functional Requirements (NFR)")
    add_bullet(doc, "End-to-end causal inference across all 43 continuous channels must execute in under 2.0 seconds.", bold_prefix="NFR-1: Latency & Responsiveness")
    add_bullet(doc, "Top-1 root-cause classification accuracy across 21 standard benchmark faults must exceed 95.0%.", bold_prefix="NFR-2: Diagnostic Accuracy")
    add_bullet(doc, "The agent must achieve 0% fabricated sensor names, ungrounded equations, or non-existent physical units in verbalized output.", bold_prefix="NFR-3: Factual Faithfulness")
    add_bullet(doc, "All telemetry, graph data, and LLM inference must execute on local premises without cloud exposure.", bold_prefix="NFR-4: Cybersecurity & Privacy")
    add_bullet(doc, "The system must operate continuously on standard multi-core workstation hardware without requiring GPU clusters.", bold_prefix="NFR-5: Resource Efficiency")

    add_section_heading(doc, "2.6 Detailed Hardware & Software Specification Matrix")
    add_paragraph(doc, "The physical and logical computing requirements for development and production deployment are summarized in Table 2.2:")

    spec_headers = ["Category", "Minimum Specification", "Recommended Workstation", "Deployment Purpose"]
    spec_data = [
        ["Processor (CPU)", "Intel Core i5 / AMD Ryzen 5 (4 Cores)", "Intel Core i7/i9 (8+ Cores, 3.8 GHz)", "Parallel Granger VAR regressions & TEP simulation"],
        ["System Memory (RAM)", "8 GB DDR4", "16 GB - 32 GB DDR4/DDR5", "In-memory time-series buffers & Neo4j graph cache"],
        ["Storage (Disk)", "256 GB SSD", "512 GB NVMe M.2 SSD", "TimescaleDB hypertables, PyTorch weights, and logs"],
        ["Graphics (GPU)", "Integrated Intel/AMD Graphics", "NVIDIA RTX 3060/4060 (6 GB+ VRAM)", "Accelerated PyTorch LSTM inference & local LLM"],
        ["Operating System", "Microsoft Windows 10/11 (64-bit)", "Windows 11 Pro / Ubuntu 22.04 LTS", "Host operating system and container orchestration"],
        ["Python Runtime", "Python 3.10", "Python 3.11+ (64-bit)", "Core backend, scientific computing & agent engine"],
        ["Graph Engine", "Neo4j Community Edition 5.x", "Neo4j Enterprise / Docker 5.x", "P&ID topological graph queries & Cypher execution"],
        ["Time-Series DB", "PostgreSQL 14 + TimescaleDB 2.8", "TimescaleDB 2.14+ (Dockerized)", "High-throughput telemetry storage & compression"],
        ["Web Framework", "FastAPI 0.100+ & Uvicorn", "FastAPI + Gunicorn / Uvicorn Workers", "Asynchronous REST API and WebSocket streaming"],
        ["Frontend UI", "Node.js 18+ & React 18", "Node.js 20 LTS, React 18, Vite 5", "Interactive Cytoscape.js and Recharts dashboard"]
    ]
    add_table_data(doc, spec_headers, spec_data, [1.3, 1.8, 1.8, 1.6])

    add_section_heading(doc, "2.7 Comprehensive Platform & Technology Justification")
    add_paragraph(doc, (
        "The selection of the underlying architectural platforms was driven by strict industrial requirements for reliability, "
        "asynchronous concurrency, low latency, and deterministic execution:"
    ))
    add_bullet(doc, "Python provides unmatched mature scientific and machine learning libraries (PyTorch, NumPy, SciPy, Statsmodels) while offering rapid asynchronous integration through FastAPI.", bold_prefix="Python 3.11+")
    add_bullet(doc, "Relational databases degrade significantly when executing temporal aggregation queries across millions of rows. TimescaleDB automates hypertable chunking and transparent compression, providing sub-millisecond sliding-window lookups.", bold_prefix="TimescaleDB")
    add_bullet(doc, "Piping and Instrumentation Diagrams are inherently directed graphs. Querying multi-hop physical connectivity in relational SQL requires expensive recursive joins, whereas Neo4j executes Cypher path traversals in milliseconds.", bold_prefix="Neo4j Graph Database")
    add_bullet(doc, "Unlike traditional linear agents, LangGraph provides cycle-tolerant, stateful graph execution, allowing deterministic verification gates and conditional tool execution before LLM synthesis.", bold_prefix="LangGraph Orchestration")
    add_bullet(doc, "Hosting Mistral-7B locally via LM Studio eliminates costly cloud API latency, protects proprietary chemical formulas and operational telemetry, and ensures air-gapped security compliance.", bold_prefix="Local LLM Inference")
    add_bullet(doc, "React 18's virtual DOM, coupled with Vite's optimized bundling and Cytoscape.js Canvas rendering, ensures smooth 60 FPS graph navigation and live telemetry charting without operator lag.", bold_prefix="React 18 & Cytoscape.js")

    add_section_heading(doc, "2.8 Process Safety & HAZOP Risk Analysis Matrix")
    add_paragraph(doc, (
        "In chemical manufacturing, a Hazard and Operability (HAZOP) study identifies the severe consequences of process "
        "parameter deviations. The Explainable Industrial AI Root-Cause Agent serves as an automated safeguard against catastrophic "
        "HAZOP hazard scenarios. Table 2.3 documents the formal HAZOP deviation matrix across primary TEP plant units."
    ))

    hazop_headers = ["Unit Operation", "Process Parameter", "Guide Word", "Consequence / Hazard", "Agent Safeguard / Mitigation"]
    hazop_data = [
        ["CSTR Reactor (UNIT_REACTOR)", "Temperature", "MORE HIGH", "Thermal runaway; overpressurization; rupture disc blowout", "Isolate CW loss; ramp XMV_10 to 100%; trim A/C feed"],
        ["CSTR Reactor (UNIT_REACTOR)", "Pressure", "MORE HIGH", "Exceeds 3000 kPa mechanical vessel limit; relief valve lifts", "Detect purge restriction; vent Stream 9 via XMV_6"],
        ["Recycle Compressor (UNIT_COMP)", "Inlet Flow", "LESS LOW", "Aerodynamic compressor surge; blade vibration; shaft failure", "Open compressor anti-surge recycle bypass valve XMV_5"],
        ["Flash Separator (UNIT_SEP)", "Liquid Level", "MORE HIGH", "Liquid carryover into recycle compressor suction; slug damage", "Throttle separator underflow valve XMV_7 to drain liquid"],
        ["Stripper Column (UNIT_STRIP)", "Reboiler Temp", "MORE LOW", "Incomplete stripping; off-spec product contaminated with D/E", "Increase reboiler steam delivery valve XMV_9 to 65%"]
    ]
    add_table_data(doc, hazop_headers, hazop_data, [1.4, 1.1, 1.0, 2.0, 1.7])

    doc.add_page_break()
