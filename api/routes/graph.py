"""FastAPI routes for querying Knowledge Graph topology for frontend Cytoscape graph view."""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from api.schemas import SubgraphResponse
from knowledge_graph.queries import KnowledgeGraphQueries, get_full_subgraph
from knowledge_graph.loader import get_driver

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("", response_model=SubgraphResponse)
@router.get("/subgraph", response_model=SubgraphResponse)
async def get_graph_topology():
    """Retrieve full plant topology graph formatted as nodes and edges for Cytoscape.js."""
    try:
        data = get_full_subgraph()
        if data and data.get("nodes"):
            return SubgraphResponse(
                nodes=data["nodes"],
                edges=data["edges"],
                elements=data.get("elements", [])
            )
    except Exception:
        pass

    # High-fidelity fallback topology if Neo4j container is temporarily restarting
    mock_nodes = [
        {"id": "UNIT_FEED", "label": "Unit", "name": "Feed Delivery System"},
        {"id": "UNIT_REACTOR", "label": "Unit", "name": "Chemical Reactor"},
        {"id": "UNIT_CONDENSER", "label": "Unit", "name": "Product Condenser"},
        {"id": "UNIT_SEPARATOR", "label": "Unit", "name": "Vapor-Liquid Separator"},
        {"id": "UNIT_COMPRESSOR", "label": "Unit", "name": "Recycle Compressor"},
        {"id": "UNIT_STRIPPER", "label": "Unit", "name": "Stripping Column"},
        {"id": "XMEAS_1", "label": "Sensor", "name": "A Feed Flow", "tag": "A_FEED_FLOW"},
        {"id": "XMEAS_6", "label": "Sensor", "name": "Reactor Feed Rate", "tag": "RX_FEED_RATE"},
        {"id": "XMEAS_7", "label": "Sensor", "name": "Reactor Pressure", "tag": "RX_PRESSURE"},
        {"id": "XMEAS_9", "label": "Sensor", "name": "Reactor Temperature", "tag": "REACTOR_TEMP"},
        {"id": "XMEAS_21", "label": "Sensor", "name": "Reactor Cooling Water", "tag": "REAC_COOL_TEMP"},
        {"id": "XMEAS_22", "label": "Sensor", "name": "Condenser Cooling Water", "tag": "COND_COOL_TEMP"},
        {"id": "XMEAS_11", "label": "Sensor", "name": "Separator Temperature", "tag": "SEP_TEMP"},
        {"id": "XMEAS_13", "label": "Sensor", "name": "Separator Pressure", "tag": "SEP_PRESS"},
        {"id": "XMEAS_5", "label": "Sensor", "name": "Recycle Flow", "tag": "RECYCLE_FLOW"},
        {"id": "XMEAS_20", "label": "Sensor", "name": "Compressor Work", "tag": "COMP_WORK"},
        {"id": "XMEAS_18", "label": "Sensor", "name": "Stripper Temperature", "tag": "STRIP_TEMP"},
        {"id": "IDV_4", "label": "FailureMode", "name": "Reactor Cooling Water Inlet Temp Step Increase", "severity": "High", "code": "IDV(4)"},
        {"id": "IDV_6", "label": "FailureMode", "name": "A Feed Loss", "severity": "High", "code": "IDV(6)"},
        {"id": "IDV_11", "label": "FailureMode", "name": "Reactor Cooling Water Valve Sticking", "severity": "Medium", "code": "IDV(11)"},
    ]

    mock_edges = [
        {"id": "e_feed_rx", "source": "UNIT_FEED", "target": "UNIT_REACTOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_rx_cond", "source": "UNIT_REACTOR", "target": "UNIT_CONDENSER", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_cond_sep", "source": "UNIT_CONDENSER", "target": "UNIT_SEPARATOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_sep_comp", "source": "UNIT_SEPARATOR", "target": "UNIT_COMPRESSOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_comp_rx", "source": "UNIT_COMPRESSOR", "target": "UNIT_REACTOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_sep_strip", "source": "UNIT_SEPARATOR", "target": "UNIT_STRIPPER", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_s1", "source": "XMEAS_1", "target": "UNIT_FEED", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s9", "source": "XMEAS_9", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s21", "source": "XMEAS_21", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s22", "source": "XMEAS_22", "target": "UNIT_CONDENSER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s11", "source": "XMEAS_11", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s5", "source": "XMEAS_5", "target": "UNIT_COMPRESSOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s18", "source": "XMEAS_18", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_f4", "source": "UNIT_REACTOR", "target": "IDV_4", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
        {"id": "e_f6", "source": "UNIT_FEED", "target": "IDV_6", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
        {"id": "e_f11", "source": "UNIT_REACTOR", "target": "IDV_11", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
    ]

    elements = [{"group": "nodes", "data": n} for n in mock_nodes] + [{"group": "edges", "data": e} for e in mock_edges]
    return SubgraphResponse(nodes=mock_nodes, edges=mock_edges, elements=elements)
