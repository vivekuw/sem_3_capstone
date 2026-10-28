import docx
from docx.shared import Pt, RGBColor
from report_builder.helpers import (
    add_chapter_header, add_section_heading, add_subsection_heading,
    add_paragraph, add_bullet, add_figure, add_code_block, add_table_data
)

def build_chapter_6(doc):
    add_chapter_header(doc, 6, "System Design")

    add_section_heading(doc, "6.1 Architectural System Topology & Multi-Tier Schema")
    add_paragraph(doc, (
        "The Explainable Industrial AI Root-Cause Agent is architected as a decoupled, multi-tiered enterprise system. "
        "The architecture is organized into five distinct operational layers to maintain strict modularity, high scalability, "
        "and deterministic execution."
    ))

    add_figure(doc, "report_assets/fig2_system_architecture.png", "Figure 6.1: Five-Tier Cyber-Physical System Architecture of the Explainable Root-Cause Agent", width_inches=6.0)

    add_paragraph(doc, (
        "As illustrated in Figure 6.1, the five functional tiers operate in a coordinated pipeline:"
    ))
    add_bullet(doc, "Executes non-linear differential mass and energy balance equations across 6 coupled units (Feed System, CSTR Reactor, Condenser, Flash Separator, Stripper, Compressor), producing 41 sensor measurements and 12 valve signals at 1 Hz.", bold_prefix="Layer 1: Continuous Plant Simulation")
    add_bullet(doc, "TimescaleDB PostgreSQL hypertables provide high-throughput chunked storage; PyTorch LSTM Autoencoders continuously evaluate reconstruction errors against rolling 3-sigma thresholds.", bold_prefix="Layer 2: Real-Time Anomaly Detection & Storage")
    add_bullet(doc, "Orchestrates the Tri-Modal Causal Fusion Engine (Temporal Lead Scorer, Neo4j Graph Proximity Tool, Granger VAR Engine) and coordinates Case-Based Reasoning retrieval with Mistral-7B verbalization.", bold_prefix="Layer 3: Multi-Modal LangGraph Reasoning Agent")
    add_bullet(doc, "FastAPI backend running under Uvicorn, serving asynchronous REST endpoints (/api/telemetry, /api/anomalies, /api/mitigate) and bi-directional WebSocket channels.", bold_prefix="Layer 4: REST API & Agent Controller")
    add_bullet(doc, "Single-page React 18 interface with Cytoscape.js canvas rendering, Recharts live sensor telemetry, and an interactive component-level downside recovery drawer.", bold_prefix="Layer 5: Industrial Operator Dashboard")

    add_section_heading(doc, "6.2 Workflow & Data Flow Lifecycle")
    add_paragraph(doc, (
        "Data flows continuously through an automated cyber-physical cycle. Telemetry flows from the plant simulator, through "
        "ingestion buffers, into the anomaly scoring engine, through the causal graph traversals, and finally to the operator interface."
    ))

    add_figure(doc, "report_assets/fig3_plant_flowsheet.png", "Figure 6.2: Tennessee Eastman Process Physical Flowsheet and Chemical Recycling Topology", width_inches=6.0)

    add_paragraph(doc, (
        "Figure 6.2 details the physical plant connectivity. Reactant gases A, C, D, and E enter the CSTR Reactor (Stream 6). "
        "The exothermic product vapor exits via Stream 7 into the Condenser, where it is cooled into a two-phase mixture (Stream 8). "
        "The Vapor-Liquid Flash Separator disengages uncondensed gases (Stream 9 & Stream 5), recycling them back to the reactor "
        "through the centrifugal Compressor. Condensed liquids flow via Stream 10 to the Stripper Column, producing finished Products "
        "G and H (Stream 11). The data flow mirrors this physical topology: when an anomaly is detected, the causal engine traverses "
        "these exact material stream connections to trace upstream failure propagation."
    ))

    add_section_heading(doc, "6.3 Capstone Project Schedule & Milestones (Gantt Chart)")
    add_paragraph(doc, (
        "The capstone engineering project was structured across a 16-week rigorous lifecycle, spanning requirements definition, "
        "simulation modeling, algorithm development, hardware integration, benchmark testing, and thesis preparation. "
        "Figure 6.3 presents the formal project execution Gantt chart."
    ))

    add_figure(doc, "report_assets/fig4_gantt_chart.png", "Figure 6.3: Project Execution Schedule and Milestone Timeline (Gantt Chart)", width_inches=6.0)

    add_section_heading(doc, "6.4 Dual-Database Schema Design (TimescaleDB & Neo4j)")
    add_paragraph(doc, (
        "To fulfill both high-frequency time-series querying and complex ontological graph traversals, the system implements "
        "a hybrid dual-database architecture, combining TimescaleDB hypertables with a Neo4j property graph."
    ))

    add_figure(doc, "report_assets/fig9_database_schema.png", "Figure 6.4: Hybrid Dual-Database Schema: Time-Series Hypertable and Ontological Property Graph", width_inches=6.0)

    add_subsection_heading(doc, "TimescaleDB Physical Storage Schema & DDL")
    add_paragraph(doc, "The physical telemetry table is defined using PostgreSQL DDL and transformed into a TimescaleDB hypertable:")
    add_code_block(doc, (
        "-- TimescaleDB Telemetry Hypertable Schema Definition\n"
        "CREATE TABLE sensor_readings (\n"
        "    time         TIMESTAMPTZ NOT NULL,\n"
        "    sensor_id    VARCHAR(32) NOT NULL,\n"
        "    value        DOUBLE PRECISION NOT NULL,\n"
        "    plant_unit   VARCHAR(32) NOT NULL,\n"
        "    is_anomaly   BOOLEAN DEFAULT FALSE,\n"
        "    z_score      DOUBLE PRECISION DEFAULT 0.0,\n"
        "    CONSTRAINT pk_sensor_readings PRIMARY KEY (time, sensor_id)\n"
        ");\n\n"
        "-- Convert standard table into a TimescaleDB Hypertable with 1-hour chunks\n"
        "SELECT create_hypertable('sensor_readings', 'time', chunk_time_interval => INTERVAL '1 hour');\n\n"
        "-- Enable columnar chunk compression with Zstandard (ZSTD) compression\n"
        "ALTER TABLE sensor_readings SET (\n"
        "    timescaledb.compress,\n"
        "    timescaledb.compress_segmentby = 'sensor_id, plant_unit',\n"
        "    timescaledb.compress_orderby = 'time DESC'\n"
        ");\n"
        "SELECT add_compression_policy('sensor_readings', INTERVAL '2 hours');"
    ))

    add_subsection_heading(doc, "Neo4j Ontological Schema & Node Attributes")
    add_paragraph(doc, (
        "In Neo4j, physical assets and process logic are modeled via structured node labels and relationship types. "
        "Table 6.1 defines the graph schema properties and ontological constraints."
    ))

    kg_headers = ["Node / Edge Label", "Graph Entity Type", "Key Properties / Attributes", "Ontological Physical Purpose"]
    kg_data = [
        [":Unit", "Node", "id, name, type, max_temp, max_press", "Models primary physical vessels (CSTR, Separator, etc.)"],
        [":Sensor", "Node", "id, name, unit_id, nominal_val, span", "Continuous process instrumentation (XMEAS 1 to 41)"],
        [":Actuator", "Node", "id, name, fail_safe, nominal_pct", "Manipulated control valves (XMV 1 to 12)"],
        [":FailureMode", "Node", "code, description, severity, recovery", "Standard TEP benchmark disturbances (IDV 1 to 21)"],
        [":Stream", "Node", "id, phase, mass_flow, pressure", "Material fluid transport headers connecting units"],
        ["[:FEEDS]", "Directed Edge", "stream_id, phase, direction", "Fluid mass and momentum transfer between equipment"],
        ["[:MEASURES]", "Directed Edge", "p_and_id_tag, calibration_date", "Associates sensor instruments with physical vessels"],
        ["[:CONTROLS]", "Directed Edge", "loop_type, direct_reverse", "Links actuator valves to controlled unit operations"],
        ["[:SUSCEPTIBLE_TO]", "Directed Edge", "criticality, trigger_condition", "Maps failure modes to vulnerable processing vessels"]
    ]
    add_table_data(doc, kg_headers, kg_data, [1.4, 1.2, 2.0, 2.2])

    add_section_heading(doc, "6.5 System Module & Package Design")
    add_paragraph(doc, "The codebase is organized into high-cohesion, low-coupling Python packages:")
    add_bullet(doc, "Implements dynamic first-principles differential algebraic equations for TEP units and 21 disturbance injections.", bold_prefix="simulator/")
    add_bullet(doc, "Contains PyTorch LSTM Autoencoder architecture, dataset loader, and dynamic 3-sigma anomaly boundary trackers.", bold_prefix="anomaly_detection/")
    add_bullet(doc, "Houses Neo4j connection pool, Cypher query procedures, and graph initialization scripts.", bold_prefix="knowledge_graph/")
    add_bullet(doc, "Implements the Granger VAR F-test engine, temporal precedence lead scorer, and multi-modal causal fusion formula.", bold_prefix="causal_reasoning/")
    add_bullet(doc, "Defines the LangGraph state machine, tool definitions (temporal_tool, graph_proximity_tool, case_tool), and Mistral-7B client.", bold_prefix="agent/")
    add_bullet(doc, "FastAPI application, CORS middleware, WebSocket controllers, and Pydantic request/response schemas.", bold_prefix="api/")
    add_bullet(doc, "React 18 single-page application containing RootCausePanel, KnowledgeGraphPage, TelemetryTable, and RecoveryDrawer.", bold_prefix="frontend/src/")

    add_section_heading(doc, "6.6 Algorithm Execution Flowcharts")
    add_paragraph(doc, (
        "When the anomaly detection thread flags that one or more sensors have crossed dynamic thresholds, the controller triggers "
        "the automated causal resolution sequence: (1) Query active anomaly timestamps from TimescaleDB; (2) Retrieve candidate sensor "
        "subgraph from Neo4j; (3) Downsample regression candidate pairs to top 8 candidates; (4) Execute parallel pairwise Granger "
        "VAR regressions; (5) Calculate composite causal scores; (6) Query Case-Based Reasoning database; (7) Invoke LangGraph state "
        "graph to verbalize grounded narrative; (8) Stream results to the React operator dashboard."
    ))

    doc.add_page_break()
