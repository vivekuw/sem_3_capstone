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


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8009))
    print(f"Starting Chemical RCA Agent API server at http://{host}:{port} ...")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
