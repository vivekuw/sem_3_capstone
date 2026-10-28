"""Chemical RCA Agent - Main FastAPI Application Server (Phase 8).

Routes:
  - Anomalies & RCA: GET /api/anomalies, GET /api/anomalies/{id}, POST /api/anomalies/analyze
  - Plant Graph:     GET /api/graph, GET /api/graph/subgraph (Cytoscape JSON)
  - Plant Simulator: GET /api/simulator/status, GET /api/simulator/faults, POST /api/simulator/inject, POST /api/simulator/clear, POST /api/simulator/step
  - Feedback:        POST /api/feedback, GET /api/feedback
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.routes import anomalies, graph, simulator, feedback

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

app = FastAPI(
    title="Chemical Process Root-Cause Analysis Agent API",
    description="Explainable Industrial AI Root-Cause Agent for Tennessee Eastman Process (TEP).",
    version="1.0.0",
)

# Enable CORS for React development server (Vite default :5173, CRA default :3000, and general origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with /api prefix
app.include_router(anomalies.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")

# Also register without /api prefix for convenience
app.include_router(anomalies.router)
app.include_router(graph.router)
app.include_router(simulator.router)
app.include_router(feedback.router)


@app.get("/")
async def root():
    return {
        "service": "Chemical RCA Agent API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "routes": {
            "anomalies": "/api/anomalies",
            "rca_analysis": "/api/anomalies/analyze",
            "graph_subgraph": "/api/graph/subgraph",
            "simulator_status": "/api/simulator/status",
            "simulator_inject": "/api/simulator/inject",
            "feedback": "/api/feedback",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Chemical RCA Agent API"}


@app.get("/api/llm/status")
@app.get("/llm/status")
def get_llm_status():
    """Check connectivity to LM Studio local server and return loaded model."""
    import urllib.request
    import json
    base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    configured_model = os.getenv("LLM_MODEL_NAME", "mistralai/mistral-7b-instruct-v0.3")
    try:
        url = f"{base_url.rstrip('/')}/models"
        req = urllib.request.Request(url, headers={"Authorization": "Bearer lm-studio"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("id") for m in data.get("data", [])]
            active_model = models[0] if models else configured_model
            return {
                "online": True,
                "base_url": base_url,
                "active_model": active_model,
                "available_models": models,
            }
    except Exception as exc:
        return {
            "online": False,
            "base_url": base_url,
            "active_model": configured_model,
            "error": str(exc),
        }


@app.get("/api/db/status")
@app.get("/db/status")
def get_db_status():
    """Non-blocking socket check for TimescaleDB and Neo4j connectivity."""
    import socket

    def check_port(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except Exception:
            return False

    timescale_host = os.getenv("TIMESCALE_HOST", "localhost")
    timescale_port = int(os.getenv("TIMESCALE_PORT", 5432))

    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_host = "localhost"
    neo4j_port = 7687
    if "://" in neo4j_uri:
        clean_uri = neo4j_uri.split("://")[-1]
        if ":" in clean_uri:
            parts = clean_uri.split(":")
            neo4j_host = parts[0]
            try:
                neo4j_port = int(parts[1].split("/")[0])
            except ValueError:
                neo4j_port = 7687

    neo4j_active = check_port(neo4j_host, neo4j_port)
    timescale_active = check_port(timescale_host, timescale_port)
    fallback_active = not (neo4j_active and timescale_active)

    return {
        "neo4j": neo4j_active,
        "timescaledb": timescale_active,
        "fallback_mode": fallback_active,
        "details": {
            "neo4j_uri": neo4j_uri,
            "timescale": f"{timescale_host}:{timescale_port}",
        },
    }

    import uvicorn
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8005))
    print(f"Starting Chemical RCA Agent API server at http://{host}:{port} ...")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
