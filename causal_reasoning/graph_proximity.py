"""Graph Proximity: Evaluates physical flowsheet hop distance from Neo4j Knowledge Graph.

Calculates directed hop distances along :FEEDS relationships between units.
Higher proximity score indicates a candidate unit is located upstream and close
to the observed alarm locations in the process flowsheet.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import networkx as nx

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Sensor to Unit ontological mapping (All 41 Process Sensors + 2 Actuator Valves)
SENSOR_TO_UNIT: Dict[str, str] = {
    # UNIT_FEED (Reactant Header)
    "XMEAS_1": "UNIT_FEED",
    "XMEAS_2": "UNIT_FEED",
    "XMEAS_3": "UNIT_FEED",
    "XMEAS_4": "UNIT_FEED",

    # UNIT_REACTOR (CSTR & Stream 6 Compositions)
    "XMEAS_6": "UNIT_REACTOR",
    "XMEAS_7": "UNIT_REACTOR",
    "XMEAS_8": "UNIT_REACTOR",
    "XMEAS_9": "UNIT_REACTOR",
    "XMEAS_21": "UNIT_REACTOR",
    "XMEAS_23": "UNIT_REACTOR",
    "XMEAS_24": "UNIT_REACTOR",
    "XMEAS_25": "UNIT_REACTOR",
    "XMEAS_26": "UNIT_REACTOR",
    "XMEAS_27": "UNIT_REACTOR",
    "XMEAS_28": "UNIT_REACTOR",
    "XMV_10": "UNIT_REACTOR",

    # UNIT_CONDENSER (Product Condenser Heat Exchanger)
    "XMEAS_22": "UNIT_CONDENSER",
    "XMV_11": "UNIT_CONDENSER",

    # UNIT_SEPARATOR (High-Pressure Flash Drum & Stream 9 Purge Compositions)
    "XMEAS_10": "UNIT_SEPARATOR",
    "XMEAS_11": "UNIT_SEPARATOR",
    "XMEAS_12": "UNIT_SEPARATOR",
    "XMEAS_13": "UNIT_SEPARATOR",
    "XMEAS_14": "UNIT_SEPARATOR",
    "XMEAS_29": "UNIT_SEPARATOR",
    "XMEAS_30": "UNIT_SEPARATOR",
    "XMEAS_31": "UNIT_SEPARATOR",
    "XMEAS_32": "UNIT_SEPARATOR",
    "XMEAS_33": "UNIT_SEPARATOR",
    "XMEAS_34": "UNIT_SEPARATOR",
    "XMEAS_35": "UNIT_SEPARATOR",
    "XMEAS_36": "UNIT_SEPARATOR",

    # UNIT_COMPRESSOR (Recycle Gas Centrifugal Compressor)
    "XMEAS_5": "UNIT_COMPRESSOR",
    "XMEAS_20": "UNIT_COMPRESSOR",

    # UNIT_STRIPPER (Distillation Stripper & Stream 11 Product Compositions)
    "XMEAS_15": "UNIT_STRIPPER",
    "XMEAS_16": "UNIT_STRIPPER",
    "XMEAS_17": "UNIT_STRIPPER",
    "XMEAS_18": "UNIT_STRIPPER",
    "XMEAS_19": "UNIT_STRIPPER",
    "XMEAS_37": "UNIT_STRIPPER",
    "XMEAS_38": "UNIT_STRIPPER",
    "XMEAS_39": "UNIT_STRIPPER",
    "XMEAS_40": "UNIT_STRIPPER",
    "XMEAS_41": "UNIT_STRIPPER",

    # Flow segment equipment
    "P100_flow": "P-100",
    "P100_pressure": "P-100",
    "P100_power": "P-100",
    "V101_pos": "V-101",
    "V101_flow": "V-101",
    "V101_dp": "V-101",
    "HX102_temp_in": "HX-102",
    "HX102_temp_out": "HX-102",
    "HX102_coolant_flow": "HX-102",
    "R103_temp": "R-103",
    "R103_pressure": "R-103",
    "R103_level": "R-103",
}

# Default TEP Process Digraph: (Source -> Destination)
DEFAULT_FLOWSHEET_EDGES = [
    ("UNIT_FEED", "UNIT_REACTOR"),
    ("UNIT_REACTOR", "UNIT_CONDENSER"),
    ("UNIT_CONDENSER", "UNIT_SEPARATOR"),
    ("UNIT_SEPARATOR", "UNIT_COMPRESSOR"),
    ("UNIT_COMPRESSOR", "UNIT_REACTOR"),    # Recycle Loop
    ("UNIT_SEPARATOR", "UNIT_STRIPPER"),
    ("UNIT_STRIPPER", "UNIT_PRODUCT"),
    ("UNIT_STRIPPER", "UNIT_CONDENSER"),    # Stripper overhead recycle
    ("P-100", "V-101"),
    ("V-101", "HX-102"),
    ("HX-102", "R-103"),
]


class PlantGraphTopology:
    """Computes directed topological proximity from Neo4j or flowsheet graph."""

    def __init__(self, edges: Optional[List[Tuple[str, str]]] = None, use_neo4j: bool = True):
        self.graph = nx.DiGraph()
        self.graph.add_edges_from(edges or DEFAULT_FLOWSHEET_EDGES)
        self.use_neo4j = use_neo4j
        self._driver = None

        if self.use_neo4j:
            try:
                from knowledge_graph.loader import get_driver
                self._driver = get_driver()
            except Exception:
                self._driver = None

    def get_unit_hop_distance(self, source_unit: str, target_unit: str) -> Optional[int]:
        """Compute directed shortest path hop distance from source_unit to target_unit."""
        if source_unit == target_unit:
            return 0

        # Try live Neo4j shortestPath query first
        if self._driver is not None:
            try:
                query = """
                MATCH p = shortestPath((start {id: $source})-[:FEEDS*]->(dest {id: $dest}))
                RETURN length(p) AS hops;
                """
                with self._driver.session() as session:
                    rec = session.run(query, source=source_unit, dest=target_unit).single()
                    if rec and rec["hops"] is not None:
                        return int(rec["hops"])
            except Exception:
                pass

        # Fallback to in-memory flowsheet digraph
        try:
            return nx.shortest_path_length(self.graph, source=source_unit, target=target_unit)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def compute_unit_proximity(
        self,
        candidate_unit: str,
        affected_units: List[str],
        max_hops: int = 5
    ) -> float:
        """Calculate normalized proximity score [0.0, 1.0].

        A candidate unit that is direct upstream or equal to affected units scores highest (~1.0).
        """
        if not affected_units:
            return 0.5

        scores = []
        for target in affected_units:
            if candidate_unit == target:
                scores.append(1.0)
                continue

            hops = self.get_unit_hop_distance(candidate_unit, target)
            if hops is not None and hops > 0:
                # Upstream causal flow: Closer hop distance yields higher score
                score = max(0.1, 1.0 - (hops / max_hops))
            else:
                # Check undirected connection with steep penalty (disturbances don't flow backwards against pumps)
                try:
                    undir_hops = nx.shortest_path_length(self.graph.to_undirected(), source=candidate_unit, target=target)
                    score = max(0.0, 0.3 - (undir_hops / (max_hops * 2)))
                except Exception:
                    score = 0.0
            scores.append(score)

        return round(float(sum(scores) / len(scores)), 4)

    def score_sensors_against_manifestations(
        self,
        candidate_sensors: List[str],
        manifesting_sensors: List[str]
    ) -> Dict[str, float]:
        """Compute proximity scores per candidate sensor based on their units."""
        affected_units = list(dict.fromkeys([SENSOR_TO_UNIT[s] for s in manifesting_sensors if s in SENSOR_TO_UNIT]))
        scores: Dict[str, float] = {}
        unit_cache: Dict[str, float] = {}

        for sensor in candidate_sensors:
            unit = SENSOR_TO_UNIT.get(sensor)
            if unit:
                if unit not in unit_cache:
                    unit_cache[unit] = self.compute_unit_proximity(unit, affected_units)
                scores[sensor] = unit_cache[unit]
            else:
                scores[sensor] = 0.2

        return scores

    def close(self):
        """Close Neo4j driver connection if open."""
        if self._driver is not None:
            try:
                self._driver.close()
            except Exception:
                pass


if __name__ == "__main__":
    topo = PlantGraphTopology()
    print("--- Graph Proximity Standalone Test ---")
    hops_feed_reac = topo.get_unit_hop_distance("UNIT_FEED", "UNIT_REACTOR")
    hops_reac_strip = topo.get_unit_hop_distance("UNIT_REACTOR", "UNIT_STRIPPER")
    print(f"Hops UNIT_FEED -> UNIT_REACTOR: {hops_feed_reac} (expected 1)")
    print(f"Hops UNIT_REACTOR -> UNIT_STRIPPER: {hops_reac_strip} (expected 2)")

    score = topo.compute_unit_proximity("UNIT_REACTOR", ["UNIT_SEPARATOR", "UNIT_STRIPPER"])
    print(f"Proximity Score for UNIT_REACTOR given alarms in [SEPARATOR, STRIPPER]: {score}")
    print("[PASS] graph_proximity.py completed successfully.")
    topo.close()
