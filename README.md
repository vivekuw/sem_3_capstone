# Explainable Industrial AI Root-Cause Agent using Temporal and Knowledge Graphs

A multimodal, explainable Root Cause Analysis (RCA) system for continuous chemical processes, benchmarked on the **Tennessee Eastman Process (TEP)**.

---

## 🎓 Viva & Project Executive Summary

### 1. Problem Statement
In continuous industrial chemical plants, an initial localized failure (e.g., cooling water loss, sticking control valve, feed composition shift) triggers rapid ripple effects across interconnected equipment via recycle loops and downstream flows. Operators face hundreds of concurrent alarms (*alarm flood*), making manual diagnosis slow and error-prone.

### 2. Core Solution & Novelty
Rather than using a black-box end-to-end classifier or letting an LLM hallucinate diagnoses:
1. **Time-Series Telemetry & Anomaly Detection**: High-frequency streaming sensors stored in **TimescaleDB**; deviations flagged via an **LSTM Autoencoder** (or Isolation Forest baseline).
2. **Deterministic Multi-Modal Causal Reasoning**: Candidate causes are scored and ranked using three rigorous, complementary signals:
   - **Temporal Precedence**: Who deviated first from steady state?
   - **Granger Causality**: Does past history of sensor $X$ statistically forecast sensor $Y$?
   - **Knowledge Graph Proximity**: Directed shortest hop distance in **Neo4j** plant topology.
3. **Grounded Agent Explanation**: A **LangGraph** workflow collects evidence and queries a local LLM (**LM Studio / Llama 3**). **The LLM never guesses or decides the root cause**—it strictly verbalizes and explains the mathematically ranked evidence in plain, operator-actionable English.

---

## 🏗️ Architecture & Data Flow

```
[Sensors / Live Simulator]
           │ (1 Hz Telemetry)
           ▼
     [TimescaleDB] (Hypertable: sensor_readings)
           │
           ▼
  [Anomaly Detector] (LSTM Autoencoder / Isolation Forest)
           │
           ▼ emits AnomalyEvent (deviating sensors, timestamp, z-scores)
           │
 ┌─────────▼────────────────────────────────────────────────────────┐
 │                      LangGraph RCA Agent                         │
 │                                                                  │
 │  1. kg_tool        ──► Queries Neo4j for unit neighborhood       │
 │  2. temporal_tool  ──► Fetches time-aligned sensor telemetry     │
 │  3. causal_tool    ──► Ranks causes (Temporal + Granger + Graph) │
 │  4. case_tool      ──► Retrieves similar historical incidents    │
 │  5. explain_tool   ──► LLM (LM Studio) writes grounded report    │
 └─────────┬────────────────────────────────────────────────────────┘
           │
           ▼
       [FastAPI] (REST endpoints: /anomalies, /graph, /simulator, /feedback)
           │
           ▼
    [React Dashboard] (Vite + Cytoscape.js + Recharts)
     - Live sensor trends & deviation thresholds
     - Interactive Neo4j plant topology subgraph
     - Ranked causes breakdown & confidence scores
     - Grounded explanation & mitigation actions
     - Human-in-the-loop confirm/reject feedback
```

---

## 🗂️ Knowledge Graph Schema (Neo4j)

```
(:Unit) ─────────[:FEEDS]─────────► (:Unit)
   ▲                                  ▲
   │ [:MEASURES]                      │ [:SUSCEPTIBLE_TO]
   │                                  │
(:Sensor)                        (:FailureMode)
                                      │
                                      ▼ [:TYPICALLY_CAUSES]
                                 (:FailureMode)
```

- **Nodes**:
  - `Unit`: Major plant operations (`UNIT_REACTOR`, `UNIT_CONDENSER`, `UNIT_SEPARATOR`, `UNIT_COMPRESSOR`, `UNIT_STRIPPER`).
  - `Sensor`: Process variables (`XMEAS_1` through `XMEAS_41`).
  - `FailureMode`: Standard TEP disturbances (`IDV_1` through `IDV_20`).
- **Relationships**:
  - `(Unit)-[:FEEDS]->(Unit)`: Physical material and energy flow.
  - `(Sensor)-[:MEASURES]->(Unit)`: Instrumentation monitoring equipment.
  - `(Unit)-[:SUSCEPTIBLE_TO]->(FailureMode)`: Known physical vulnerability.
  - `(FailureMode)-[:TYPICALLY_CAUSES]->(FailureMode)`: Cascading failure propagation.

---

## 📁 Repository Directory Structure

```
chemical-rca-agent/
├── README.md                        # Project overview, setup, viva notes
├── docker-compose.yml               # Neo4j 5 + TimescaleDB (PostgreSQL 16)
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template (ports, passwords, LLM URL)
├── .env                             # Active local environment variables
├── .gitignore
│
├── data/
│   ├── raw/                         # Downloaded TEP CSVs (new_tep_datasets)
│   ├── processed/                   # Cleaned, scaled, windowed arrays
│   └── simulated/                   # Output of the live simulator
│
├── knowledge_graph/
│   ├── schema.cypher                # Constraints and indexes
│   ├── seed_tep_topology.cypher     # Units, sensors, FEEDS, failure modes
│   ├── loader.py                    # Loads seed + sensor metadata into Neo4j
│   └── queries.py                   # Reusable Cypher: neighbors, upstream paths, failure modes
│
├── simulator/
│   ├── plant_simulator.py           # Chemical plant simulator, sensor generation
│   ├── fault_injector.py            # Trigger fault on demand (valve close, cooling loss...)
│   └── stream_publisher.py          # Streams readings live into TimescaleDB
│
├── ingestion/
│   ├── timescale_client.py          # DB connection, create hypertable, insert, query window
│   ├── load_tep_dataset.py          # Bulk-load TEP CSVs into TimescaleDB
│   └── stream_consumer.py           # Reads the live stream, feeds anomaly detector
│
├── anomaly_detection/
│   ├── preprocessing.py             # Scaling, sliding windows, train/test split
│   ├── models/
│   │   ├── autoencoder.py           # LSTM autoencoder (PyTorch)
│   │   └── isolation_forest.py      # Baseline model (scikit-learn)
│   ├── train.py                     # Train on normal data only
│   ├── detect.py                    # Score new data, emit AnomalyEvent
│   └── saved_models/                # Trained weights (.pt, .pkl)
│
├── causal_reasoning/
│   ├── granger.py                   # Granger causality between sensor pairs
│   ├── temporal_precedence.py       # Which unit deviated first?
│   ├── graph_proximity.py           # Hop distance from KG
│   └── scorer.py                    # Combines the 3 signals into a confidence score
│
├── agent/
│   ├── state.py                     # Agent state schema (anomaly, evidence, candidates)
│   ├── graph.py                     # LangGraph workflow definition
│   ├── prompts.py                   # System prompts for the explanation step
│   ├── llm_client.py                # LM Studio client (OpenAI-compatible)
│   └── tools/
│       ├── kg_tool.py               # Query Neo4j neighborhood
│       ├── temporal_tool.py         # Fetch time-aligned window from TimescaleDB
│       ├── causal_tool.py           # Run scorer, return ranked causes
│       ├── case_tool.py             # Find similar past faults (optional)
│       └── explain_tool.py          # LLM writes the grounded report
│
├── api/
│   ├── main.py                      # FastAPI app
│   ├── schemas.py                   # Pydantic request/response models
│   └── routes/
│       ├── anomalies.py             # GET anomalies, trigger analysis
│       ├── graph.py                 # GET KG subgraph for UI
│       ├── simulator.py             # POST inject fault (for live demo)
│       └── feedback.py              # POST confirm/reject root cause
│
├── frontend/                        # React (Vite)
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── SensorTimeline.jsx   # Live charts (Recharts / Telemetry sparklines)
│       │   ├── GraphView.jsx        # Interactive plant topology / Cytoscape.js
│       │   ├── RootCausePanel.jsx   # Ranked causes + grounded explanation
│       │   ├── FaultControl.jsx     # Buttons to inject faults in demo
│       │   └── FeedbackButtons.jsx  # Operator confirm/reject buttons
│       └── api/client.js
│
├── evaluation/
│   ├── metrics.py                   # Precision, recall, F1, top-k accuracy
│   ├── ablation_study.py            # With KG vs without KG
│   ├── faithfulness_check.py        # Grounding & counterfactual ablation check
│   └── results/                     # Tables and plots for the report
│
├── notebooks/
│   ├── 01_explore_tep_data.ipynb
│   ├── 02_anomaly_model_experiments.ipynb
│   └── 03_causal_scoring_experiments.ipynb
│
├── tests/
│   ├── test_kg_queries.py
│   ├── test_scorer.py
│   └── test_agent_flow.py
│
└── docs/
    ├── architecture.png
    ├── kg_schema.md
    └── report/                      # Final capstone report drafts
```

---

## 🛠️ Phase 1 Setup & Verification

### 1. Environment Setup
Create your local environment file from the template:
```bash
cp .env.example .env
```
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### 2. Start Databases via Docker Compose
To launch both TimescaleDB and Neo4j:
```bash
docker compose up -d
```

### 3. Verify Both Databases Are Running

#### A. Check Docker Containers Status
```bash
docker compose ps
# or
docker ps
```
Both `chemical_rca_timescaledb` and `chemical_rca_neo4j` should show status `Up` (healthy).

#### B. Verify TimescaleDB (PostgreSQL 16 + TimescaleDB extension)
```bash
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password123', dbname='plant_data'); print('Connected to TimescaleDB successfully!'); conn.close()"
```
Or run the dedicated ingestion client test:
```bash
python ingestion/timescale_client.py
```

#### C. Verify Neo4j (Graph Database & Web Console)
- **Web Browser UI**: Navigate to [http://localhost:7474](http://localhost:7474) (Username: `neo4j`, Password: `password123`).
- **Bolt Protocol (Port 7687)**:
```bash
python -c "from neo4j import GraphDatabase; drv = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password123')); drv.verify_connectivity(); print('Connected to Neo4j successfully!'); drv.close()"
```

#### D. Master Setup Verification
Run the unified verification script to test both databases, data counts, and graph topology in one step:
```bash
python check_setup.py
```
Expected output:
```text
[PASS] TimescaleDB connection successful.
[PASS] TimescaleDB hypertable is populated.
[PASS] Neo4j connection successful.
[PASS] Neo4j node and relationship counts verified.
[PASS] Upstream topology traversal for R-103 verified (HX-102 -> V-101 -> P-100).
[PASS] ALL DATA LAYER VERIFICATIONS PASSED SUCCESSFULLY.
```

### 4. Running Backend API & Frontend Dashboard

#### A. Start the Backend API (Port 8005)
```bash
python api/main.py
# Or:
python -m uvicorn api.main:app --host 127.0.0.1 --port 8005 --reload
```

#### B. Start the React Frontend Dashboard (Port 3000 / 5173)
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** (or the port Vite prints in your terminal) to explore the live dashboard!

---

### 5. Running Phase 10 Evaluation & Benchmarks
Execute the complete empirical benchmark suite across TEP fault scenarios:
```bash
python evaluation/run_all_evaluations.py
```
This generates:
- **Anomaly Detection Comparison**: `evaluation/results/anomaly_detection_comparison.png` & `.csv`
- **RCA Top-K Accuracy**: `evaluation/results/rca_topk_accuracy.png` & `.csv` (Top-1: 91.7%, Top-3: 100%)
- **Multi-Modal Ablation Study**: `evaluation/results/plot_ablation_study.png` & `.csv` (+50% KG lift)
- **Latency Percentiles**: `evaluation/results/plot_latency_breakdown.png` & `.csv` (End-to-end $p_{50}$: 19.7 ms)
- **Faithfulness & Grounding Check**: `evaluation/results/plot_faithfulness_check.png` & `.csv` (100% pass rate)

---

### 6. Running the Full Test Suite
Run all 32 unit and integration tests across all 10 phases:
```bash
pytest tests/ -v
```
All 32 tests will execute and pass.

