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
    neo4j_online = False
    try:
        import socket
        with socket.create_connection(("localhost", 7687), timeout=0.15):
            neo4j_online = True
    except Exception:
        neo4j_online = False

    if neo4j_online:
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
        # UNIT_FEED sensors
        {"id": "XMEAS_1", "label": "Sensor", "name": "A Feed Flow", "tag": "A_FLOW"},
        {"id": "XMEAS_2", "label": "Sensor", "name": "D Feed Flow", "tag": "D_FLOW"},
        {"id": "XMEAS_3", "label": "Sensor", "name": "E Feed Flow", "tag": "E_FLOW"},
        {"id": "XMEAS_4", "label": "Sensor", "name": "A+C Feed Flow", "tag": "AC_FLOW"},
        # UNIT_REACTOR sensors
        {"id": "XMEAS_6", "label": "Sensor", "name": "Reactor Feed Rate", "tag": "RX_FEED"},
        {"id": "XMEAS_7", "label": "Sensor", "name": "Reactor Pressure", "tag": "RX_PRESS"},
        {"id": "XMEAS_8", "label": "Sensor", "name": "Reactor Level", "tag": "RX_LVL"},
        {"id": "XMEAS_9", "label": "Sensor", "name": "Reactor Temperature", "tag": "RX_TEMP"},
        {"id": "XMEAS_21", "label": "Sensor", "name": "Reactor Coolant Temp", "tag": "RX_CW_OUT"},
        {"id": "XMV_10", "label": "Sensor", "name": "Cooling Valve Pos", "tag": "CW_VALVE"},
        # UNIT_CONDENSER sensors
        {"id": "XMEAS_22", "label": "Sensor", "name": "Condenser Coolant Temp", "tag": "COND_CW_OUT"},
        {"id": "XMV_11", "label": "Sensor", "name": "Condenser Valve Pos", "tag": "COND_VALVE"},
        # UNIT_SEPARATOR sensors
        {"id": "XMEAS_10", "label": "Sensor", "name": "Purge Gas Rate", "tag": "PURGE_FLOW"},
        {"id": "XMEAS_11", "label": "Sensor", "name": "Separator Temperature", "tag": "SEP_TEMP"},
        {"id": "XMEAS_12", "label": "Sensor", "name": "Separator Level", "tag": "SEP_LVL"},
        {"id": "XMEAS_13", "label": "Sensor", "name": "Separator Pressure", "tag": "SEP_PRESS"},
        {"id": "XMEAS_14", "label": "Sensor", "name": "Separator Underflow", "tag": "SEP_FLOW"},
        # UNIT_COMPRESSOR sensors
        {"id": "XMEAS_5", "label": "Sensor", "name": "Recycle Flow", "tag": "RECYCLE_FLOW"},
        {"id": "XMEAS_20", "label": "Sensor", "name": "Compressor Work", "tag": "COMP_PWR"},
        # UNIT_STRIPPER sensors
        {"id": "XMEAS_15", "label": "Sensor", "name": "Stripper Level", "tag": "STRIP_LVL"},
        {"id": "XMEAS_16", "label": "Sensor", "name": "Stripper Pressure", "tag": "STRIP_PRESS"},
        {"id": "XMEAS_17", "label": "Sensor", "name": "Product Flow Rate", "tag": "PROD_FLOW"},
        {"id": "XMEAS_18", "label": "Sensor", "name": "Stripper Temperature", "tag": "STRIP_TEMP"},
        {"id": "XMEAS_19", "label": "Sensor", "name": "Stripper Steam Flow", "tag": "STEAM_FLOW"},
        # Failure Modes
        {"id": "IDV_4", "label": "FailureMode", "name": "Cooling Water Loss", "severity": "High", "code": "IDV(4)"},
        {"id": "IDV_6", "label": "FailureMode", "name": "A Feed Loss", "severity": "High", "code": "IDV(6)"},
        {"id": "IDV_11", "label": "FailureMode", "name": "Reactor Valve Sticking", "severity": "Medium", "code": "IDV(11)"},
    ]

    mock_edges = [
        {"id": "e_feed_rx", "source": "UNIT_FEED", "target": "UNIT_REACTOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_rx_cond", "source": "UNIT_REACTOR", "target": "UNIT_CONDENSER", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_cond_sep", "source": "UNIT_CONDENSER", "target": "UNIT_SEPARATOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_sep_comp", "source": "UNIT_SEPARATOR", "target": "UNIT_COMPRESSOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_comp_rx", "source": "UNIT_COMPRESSOR", "target": "UNIT_REACTOR", "type": "FEEDS", "label": "FEEDS"},
        {"id": "e_sep_strip", "source": "UNIT_SEPARATOR", "target": "UNIT_STRIPPER", "type": "FEEDS", "label": "FEEDS"},
        # UNIT_FEED sensors
        {"id": "e_s1", "source": "XMEAS_1", "target": "UNIT_FEED", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s2", "source": "XMEAS_2", "target": "UNIT_FEED", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s3", "source": "XMEAS_3", "target": "UNIT_FEED", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s4", "source": "XMEAS_4", "target": "UNIT_FEED", "type": "MEASURES", "label": "MEASURES"},
        # UNIT_REACTOR sensors
        {"id": "e_s6", "source": "XMEAS_6", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s7", "source": "XMEAS_7", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s8", "source": "XMEAS_8", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s9", "source": "XMEAS_9", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s21", "source": "XMEAS_21", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_mv10", "source": "XMV_10", "target": "UNIT_REACTOR", "type": "MEASURES", "label": "MEASURES"},
        # UNIT_CONDENSER sensors
        {"id": "e_s22", "source": "XMEAS_22", "target": "UNIT_CONDENSER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_mv11", "source": "XMV_11", "target": "UNIT_CONDENSER", "type": "MEASURES", "label": "MEASURES"},
        # UNIT_SEPARATOR sensors
        {"id": "e_s10", "source": "XMEAS_10", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s11", "source": "XMEAS_11", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s12", "source": "XMEAS_12", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s13", "source": "XMEAS_13", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s14", "source": "XMEAS_14", "target": "UNIT_SEPARATOR", "type": "MEASURES", "label": "MEASURES"},
        # UNIT_COMPRESSOR sensors
        {"id": "e_s5", "source": "XMEAS_5", "target": "UNIT_COMPRESSOR", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s20", "source": "XMEAS_20", "target": "UNIT_COMPRESSOR", "type": "MEASURES", "label": "MEASURES"},
        # UNIT_STRIPPER sensors
        {"id": "e_s15", "source": "XMEAS_15", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s16", "source": "XMEAS_16", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s17", "source": "XMEAS_17", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s18", "source": "XMEAS_18", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        {"id": "e_s19", "source": "XMEAS_19", "target": "UNIT_STRIPPER", "type": "MEASURES", "label": "MEASURES"},
        # Failure Modes
        {"id": "e_f4", "source": "UNIT_REACTOR", "target": "IDV_4", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
        {"id": "e_f6", "source": "UNIT_FEED", "target": "IDV_6", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
        {"id": "e_f11", "source": "UNIT_REACTOR", "target": "IDV_11", "type": "SUSCEPTIBLE_TO", "label": "SUSCEPTIBLE_TO"},
    ]

    elements = [{"group": "nodes", "data": n} for n in mock_nodes] + [{"group": "edges", "data": e} for e in mock_edges]
    return SubgraphResponse(nodes=mock_nodes, edges=mock_edges, elements=elements)
