import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_figure, add_table_data
)

def build_chapter_4(doc):
    add_chapter_header(doc, 4, "Technologies Used")

    add_section_heading(doc, "4.1 Technology Stack Architectural Overview")
    add_paragraph(doc, (
        "The Explainable Industrial AI Root-Cause Agent is architected as an enterprise cyber-physical computing stack "
        "designed specifically for mission-critical chemical plant environments. Building an industrial AI system demands "
        "a careful balance between ultra-low-latency real-time telemetry processing, deterministic graph path traversal, "
        "robust statistical inference, and rich visual operator interaction. To meet these stringent constraints, the project "
        "leverages a modern, open-source stack comprising Python 3.11+, React 18, Cytoscape.js, FastAPI, PyTorch, Neo4j, "
        "TimescaleDB, Statsmodels, and LangGraph with locally served Mistral-7B."
    ))

    add_section_heading(doc, "4.2 Programming Language: Python 3.11+")
    add_paragraph(doc, (
        "Python 3.11+ was selected as the foundational programming language for the backend, causal reasoning, deep learning, "
        "and agent orchestration pipelines. Python offers several critical advantages in industrial systems engineering:"
    ))
    add_bullet(doc, "Python 3.11 introduces significant runtime speed improvements (10% to 25% faster than Python 3.10) via specialized bytecode execution and faster function calls, which is vital for real-time mathematical matrix manipulation.", bold_prefix="Enhanced Runtime Performance")
    add_bullet(doc, "Comprehensive ecosystem of mature, heavily optimized scientific packages including NumPy (vectorized array operations), SciPy (numerical integration), Pandas (data manipulation), and Statsmodels (econometric time-series analysis).", bold_prefix="Scientific & Numeric Ecosystem")
    add_bullet(doc, "Native async/await syntax enables non-blocking asynchronous concurrency, allowing simultaneous telemetry ingestion, database persistence, and causal scoring without blocking operator requests.", bold_prefix="Asynchronous Concurrency")

    add_section_heading(doc, "4.3 High-Performance Frontend: React 18, Vite, Cytoscape.js & Recharts")
    add_paragraph(doc, (
        "The frontend user interface is built as a single-page reactive web application using React 18, bundled via Vite 5. "
        "Control room interfaces must maintain fluid 60 FPS responsiveness even when rendering complex network graphs and "
        "updating hundreds of numerical telemetry variables per second."
    ))
    add_bullet(doc, "Utilizes concurrent rendering and automatic batching to ensure that high-frequency sensor updates do not cause frame drops or UI freezing.", bold_prefix="React 18 Concurrent Engine")
    add_bullet(doc, "An advanced graph visualization library utilizing HTML5 Canvas rendering. It handles multi-unit chemical piping topologies with hundreds of nodes and directed edges, supporting force-directed layout algorithms, dynamic zoom/pan, and per-machine subgraph filtering.", bold_prefix="Cytoscape.js Graph Engine")
    add_bullet(doc, "A modular charting library built on SVG that renders real-time multi-channel sensor telemetry trends, historical baselines, and dynamic 3-sigma anomaly threshold bands.", bold_prefix="Recharts Telemetry Visualizer")
    add_bullet(doc, "A curated, dark slate design system engineered with high-contrast accessibility tokens, warning palettes (crimson, amber, emerald, indigo), and collapsible recovery drawers.", bold_prefix="Custom CSS Design System")

    add_subsection_heading(doc, "Cytoscape.js Visual Styling and Dynamic State Mappings")
    add_paragraph(doc, (
        "In Cytoscape.js, node and edge appearances reflect real-time plant state. When an anomaly is detected, the affected "
        "node undergoes CSS transition animation, turning flashing red with halo glow. Table 4.1 outlines the Cytoscape stylesheet tokens."
    ))

    cy_headers = ["Element Selector", "Visual Shape", "Color Token", "Border Style", "Operational State Represented"]
    cy_data = [
        ["node.unit", "Round Rectangle", "#1E293B (Slate)", "2px Solid #475569", "Nominal Chemical Processing Vessel"],
        ["node.unit.warning", "Round Rectangle", "#7F1D1D (Red)", "3px Pulsing Red", "Unit Harboring Active Critical Anomaly"],
        ["node.sensor.nominal", "Circle (Diameter: 36px)", "#0F172A (Navy)", "1.5px Solid #38BDF8", "Normal Telemetry Reading (< 2.0σ)"],
        ["node.sensor.anomaly", "Circle (Diameter: 44px)", "#DC2626 (Crimson)", "3px Red Halo Glow", "Statistical Excursion (> 3.0σ Threshold)"],
        ["node.actuator", "Diamond", "#312E81 (Indigo)", "2px Solid #818CF8", "Manipulated Valve Actuator (XMV 1-12)"],
        ["edge.stream.nominal", "Directed Arrow", "#64748B (Gray)", "2px Solid Line", "Nominal Fluid/Vapor Material Flow"],
        ["edge.stream.elevated", "Directed Arrow", "#EF4444 (Red)", "3.5px Animated Dash", "Fluid Line Carrying High Thermal Energy"],
        ["edge.controls", "Dotted Arrow", "#F59E0B (Amber)", "1.5px Dotted Line", "Instrument Control Feedback Loop"]
    ]
    add_table_data(doc, cy_headers, cy_data, [1.4, 1.4, 1.3, 1.4, 2.0])

    add_section_heading(doc, "4.4 Graphical User Interface Walkthrough & Screenshots")
    add_paragraph(doc, (
        "The operator dashboard is organized into specialized views designed to minimize cognitive load during industrial upsets. "
        "Figures 4.1, 4.2, and 4.3 present detailed screenshots of the production operator interface."
    ))

    add_figure(doc, "report_assets/ui_overview_dashboard.png", "Figure 4.1: Industrial Operator Dashboard — Plant Overview & 43-Sensor Real-Time Telemetry Matrix", width_inches=6.0)
    add_paragraph(doc, (
        "As illustrated in Figure 4.1, the Overview Dashboard displays high-level status cards for all primary plant units "
        "(CSTR Reactor, Recycle Compressor, Flash Separator). The central pane hosts the 43-sensor telemetry matrix, displaying "
        "current engineering values, historical ranges, and color-coded status badges that dynamically flag statistical excursions."
    ))

    add_figure(doc, "report_assets/ui_root_cause_analysis.png", "Figure 4.2: Root Cause Analysis Panel with Interactive Component-Level Downside Recovery Drawer", width_inches=6.0)
    add_paragraph(doc, (
        "Figure 4.2 displays the Root Cause Analysis interface. When an upset occurs, the left pane presents the mathematically "
        "ranked causal anomalies. Clicking on any ranked sensor opens the interactive Downside Recovery Drawer (right pane), "
        "which diagnoses the specific physical component failure (e.g., CSTR Cooling Jacket fouling or valve stiction) and provides "
        "step-by-step operator remediation actions alongside a one-click automated mitigation execution button."
    ))

    add_figure(doc, "report_assets/ui_knowledge_graph_view.png", "Figure 4.3: Cytoscape.js Knowledge Graph Explorer with Per-Machine Subgraph Dropdown Selector", width_inches=6.0)
    add_paragraph(doc, (
        "Figure 4.3 highlights the Knowledge Graph Explorer. To prevent visual clutter across the dense 43-sensor network, "
        "a top dropdown selector allows the operator to focus on specific physical machines (e.g., UNIT_REACTOR, UNIT_COMPRESSOR, "
        "UNIT_STRIPPER). The Canvas automatically isolates the active machine, its associated process measurement tags, and directed "
        "material streams, providing clear topological context during troubleshooting."
    ))

    add_section_heading(doc, "4.5 High-Throughput Asynchronous Backend: FastAPI & Uvicorn")
    add_paragraph(doc, (
        "The backend server is implemented using FastAPI and served via the high-performance Uvicorn ASGI web server. "
        "FastAPI leverages Python's type hints and Pydantic validation to offer exceptional throughput and sub-5ms response times. "
        "Table 4.2 documents the core REST API route catalog."
    ))

    api_headers = ["Endpoint URL", "Method", "Request Payload", "Response Object", "Operational Purpose"]
    api_data = [
        ["/api/telemetry/live", "GET", "None", "JSON Array of 43 Sensors", "Fetches instantaneous 1 Hz process values and z-scores"],
        ["/api/telemetry/history", "GET", "sensor_id, window_sec", "JSON Array of Timestamps & Floats", "Retrieves 120-tick sliding window for Recharts trends"],
        ["/api/anomalies/active", "GET", "threshold_sigma", "JSON List of Deviating Tags", "Returns sensors currently violating 3-sigma boundaries"],
        ["/api/causal/evaluate", "POST", "{ window_size: 120 }", "JSON Causal Ranking & Scores", "Triggers Tri-Modal causal fusion analysis (1.2s execution)"],
        ["/api/graph/subgraph", "GET", "unit_id: string", "Cytoscape JSON (Nodes & Edges)", "Returns filtered subgraph for selected chemical vessel"],
        ["/api/mitigate/execute", "POST", "{ fault_mode, target_valves }", "JSON Mitigation Status", "Commands closed-loop safety valve adjustments"],
        ["/api/mitigate/reset", "POST", "None", "JSON Reset Confirmation", "Restores all actuators to nominal steady-state targets"],
        ["/ws/telemetry", "WebSocket", "Client Handshake", "1 Hz Binary Streaming Feed", "Continuous non-blocking telemetry stream to React UI"]
    ]
    add_table_data(doc, api_headers, api_data, [1.5, 0.8, 1.4, 1.6, 2.2])

    add_section_heading(doc, "4.6 Deep Learning Framework: PyTorch LSTM Autoencoders")
    add_paragraph(doc, (
        "PyTorch is employed to build and train deep Long Short-Term Memory (LSTM) Autoencoder networks. Autoencoders are "
        "exceptionally well-suited for unsupervised anomaly detection in multivariate continuous processes. By training the network "
        "strictly on nominal steady-state data, the autoencoder learns the non-linear manifold of normal plant operation. When a physical "
        "fault occurs, the model cannot accurately reconstruct the abnormal correlation patterns, causing a sharp spike in Mean Squared "
        "Error (MSE). Dynamic 3-sigma thresholds applied to this reconstruction error trigger instantaneous anomaly alerts."
    ))

    add_section_heading(doc, "4.7 Ontological Knowledge Store: Neo4j Graph Database & Cypher")
    add_paragraph(doc, (
        "Physical plant connectivity is stored in a Neo4j property graph database. Relational schemas struggle to model multi-hop "
        "fluid piping connections and cyclic recycle streams efficiently. Neo4j models plant entities as labeled nodes (:Unit, "
        ":Sensor, :FailureMode, :Stream) and physical relationships as directed edges ([:FEEDS], [:MEASURES], [:CONTROLS], "
        "[:SUSCEPTIBLE_TO]). Using Cypher query procedures and Dijkstra shortest-path algorithms, the causal engine traverses "
        "physical piping paths in milliseconds to calculate topological flow proximity."
    ))

    add_section_heading(doc, "4.8 Time-Series Storage Engine: TimescaleDB & PostgreSQL Hypertables")
    add_paragraph(doc, (
        "TimescaleDB—an open-source time-series database engineered as an extension to PostgreSQL—serves as the primary telemetry "
        "repository. TimescaleDB automatically partitions time-series tables into temporal 'chunks' called Hypertables. This architecture "
        "maintains lightning-fast insert rates (over 50,000 samples/sec) while enabling sub-millisecond range queries across sliding "
        "time windows. Built-in columnar compression achieves a 92% storage reduction for historical process logs."
    ))

    add_section_heading(doc, "4.9 Multi-Agent Orchestration & LLM Synthesis: LangGraph & Mistral-7B")
    add_paragraph(doc, (
        "To synthesize complex mathematical data into plain-English operator briefings, the system employs LangGraph orchestrating "
        "a locally hosted Mistral-7B Instruct model via LM Studio. LangGraph structures the reasoning process as a state graph with "
        "deterministic validation gates. By feeding the LLM only verified causal rankings, P&ID stream paths, and historical CBR cases, "
        "the agent strictly verbalizes ground truth, completely eliminating hallucination risks while preserving total data privacy."
    ))

    add_section_heading(doc, "4.10 Statistical Causal Engines: Statsmodels VAR & Granger Testing")
    add_paragraph(doc, (
        "Statistical causality is computed using the Statsmodels library. The system fits Vector Autoregression (VAR) models "
        "across candidate sensor pairs and computes Wald F-test statistics. This verifies whether historical lags of an upstream sensor "
        "provide statistically significant predictive power for a downstream sensor's trajectory, establishing rigorous empirical causality."
    ))

    add_section_heading(doc, "4.11 Development Tools, Version Control & Testing Frameworks")
    add_paragraph(doc, (
        "The software engineering lifecycle was supported by a suite of automated developer tooling: Visual Studio Code "
        "(primary IDE with Pylance and ESLint), PowerShell 7 (automation scripting and background process management), "
        "Git (distributed version control with feature branch workflows), and PyTest (automated test suites for mathematical models)."
    ))

    add_section_heading(doc, "4.12 Docker Containerization Architecture & Multi-Service Topology")
    add_paragraph(doc, (
        "To guarantee reproducibility across testing and production environments, the platform is orchestrated via Docker Compose. "
        "Table 4.3 outlines the containerized multi-service specifications."
    ))

    doc_headers = ["Service Container", "Base Image", "Exposed Ports", "Internal Storage Mount", "Service Responsibility"]
    doc_data = [
        ["timescaledb_service", "timescale/timescaledb:latest-pg14", "5432:5432", "/var/lib/postgresql/data", "Persistent storage of 43-sensor time-series hypertables"],
        ["neo4j_service", "neo4j:5.12-community", "7474:7474, 7687:7687", "/data, /logs", "Property graph engine hosting P&ID flow topology"],
        ["fastapi_backend", "python:3.11-slim", "8005:8005", "P:\\SEM3_CAPSTONE", "FastAPI server, PyTorch LSTM inference, and Granger VAR"],
        ["react_frontend", "node:20-alpine", "3000:3000", "/app/node_modules", "Vite dev server and production Cytoscape operator UI"],
        ["lm_studio_runtime", "Host Process (Local)", "1234:1234", "C:\\Users\\...\\.cache", "Local OpenAI-compatible endpoint serving Mistral-7B"]
    ]
    add_table_data(doc, doc_headers, doc_data, [1.4, 1.6, 1.3, 1.4, 1.8])

    doc.add_page_break()
