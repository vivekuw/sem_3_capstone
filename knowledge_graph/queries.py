"""Knowledge Graph Query API for Tennessee Eastman Process (TEP).

Provides functions to traverse plant flowsheet topology and inspect failure modes:
- get_neighbors(unit, hops)
- get_upstream_units(unit)
- get_failure_modes(unit)
- get_shortest_path(a, b)
- get_sensors(unit)
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from neo4j import Driver

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from knowledge_graph.loader import get_driver


def get_neighbors(unit: str, hops: int = 1, driver: Optional[Driver] = None) -> List[Dict[str, Any]]:
    """Retrieve adjacent plant units within a specified hop distance.

    Args:
        unit: Unit identifier (e.g., 'UNIT_REACTOR').
        hops: Maximum graph traversal hops (default 1).
        driver: Optional active Neo4j driver.

    Returns:
        List[Dict[str, Any]]: Neighbor units with id, name, and type/role.
    """
    query = f"""
    MATCH (start {{id: $unit_id}})-[:FEEDS*1..{max(1, hops)}]-(neighbor)
    WHERE (start:Unit OR start:Equipment)
      AND (neighbor:Unit OR neighbor:Equipment)
      AND start <> neighbor
    RETURN DISTINCT neighbor.id AS id,
                    neighbor.name AS name,
                    coalesce(neighbor.type, labels(neighbor)[0]) AS type
    ORDER BY neighbor.id ASC;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            result = session.run(query, unit_id=unit)
            return [dict(record) for record in result]
    finally:
        if owns_driver:
            drv.close()


def get_upstream_units(unit: str, driver: Optional[Driver] = None) -> List[Dict[str, Any]]:
    """Retrieve all physical units that feed into the target unit along directed FEEDS streams.

    Ordered by hop distance from closest upstream unit to furthest.

    Args:
        unit: Target unit identifier (e.g., 'UNIT_SEPARATOR' or 'R-103').
        driver: Optional active Neo4j driver.

    Returns:
        List[Dict[str, Any]]: Upstream units with id, name, type, and hop_distance.
    """
    query = """
    MATCH p = (upstream)-[:FEEDS*1..]->(target {id: $unit_id})
    WHERE (upstream:Unit OR upstream:Equipment)
      AND (target:Unit OR target:Equipment)
      AND upstream <> target
    RETURN upstream.id AS id,
           upstream.name AS name,
           coalesce(upstream.type, labels(upstream)[0]) AS type,
           min(length(p)) AS hop_distance
    ORDER BY hop_distance ASC, id ASC;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            result = session.run(query, unit_id=unit)
            return [dict(record) for record in result]
    finally:
        if owns_driver:
            drv.close()


def get_downstream(unit: str, driver: Optional[Driver] = None) -> List[Dict[str, Any]]:
    """Retrieve all units located downstream from the specified unit along directed FEEDS streams.

    Args:
        unit: Source unit identifier (e.g., 'UNIT_REACTOR').
        driver: Optional active Neo4j driver.

    Returns:
        List[Dict[str, Any]]: Downstream units with id, name, type, and hop_distance.
    """
    query = """
    MATCH p = (source {id: $unit_id})-[:FEEDS*1..]->(downstream)
    WHERE (source:Unit OR source:Equipment)
      AND (downstream:Unit OR downstream:Equipment)
      AND source <> downstream
    RETURN downstream.id AS id,
           downstream.name AS name,
           coalesce(downstream.type, labels(downstream)[0]) AS type,
           min(length(p)) AS hop_distance
    ORDER BY hop_distance ASC, id ASC;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            result = session.run(query, unit_id=unit)
            return [dict(record) for record in result]
    finally:
        if owns_driver:
            drv.close()


def get_failure_modes(unit: str, driver: Optional[Driver] = None) -> List[Dict[str, Any]]:
    """Retrieve all operational disturbances / failure modes (IDVs) that a unit is susceptible to.

    Args:
        unit: Target unit identifier (e.g., 'UNIT_REACTOR' or 'UNIT_FEED').
        driver: Optional active Neo4j driver.

    Returns:
        List[Dict[str, Any]]: FailureMode details including id, code, name, category, and severity.
    """
    query = """
    MATCH (u {id: $unit_id})-[:SUSCEPTIBLE_TO|HAS_FAILURE_MODE]->(f:FailureMode)
    RETURN DISTINCT f.id AS id,
                    f.code AS code,
                    f.name AS name,
                    f.category AS category,
                    f.severity AS severity,
                    f.description AS description
    ORDER BY f.code ASC;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            result = session.run(query, unit_id=unit)
            return [dict(record) for record in result]
    finally:
        if owns_driver:
            drv.close()


def get_shortest_path(a: str, b: str, driver: Optional[Driver] = None) -> List[str]:
    """Find the shortest process flow path between two units.

    Checks directed process flow first, and falls back to undirected flowsheet connectivity.

    Args:
        a: Starting unit ID (e.g., 'UNIT_FEED' or 'P-100').
        b: Destination unit ID (e.g., 'UNIT_STRIPPER' or 'R-103').
        driver: Optional active Neo4j driver.

    Returns:
        List[str]: Sequence of unit IDs forming the path, or empty list if no path exists.
    """
    directed_query = """
    MATCH p = shortestPath((start {id: $a})-[:FEEDS*]->(dest {id: $b}))
    RETURN [n IN nodes(p) | n.id] AS path_ids;
    """
    undirected_query = """
    MATCH p = shortestPath((start {id: $a})-[:FEEDS*]-(dest {id: $b}))
    RETURN [n IN nodes(p) | n.id] AS path_ids;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            rec = session.run(directed_query, a=a, b=b).single()
            if rec and rec["path_ids"]:
                return list(rec["path_ids"])

            rec = session.run(undirected_query, a=a, b=b).single()
            if rec and rec["path_ids"]:
                return list(rec["path_ids"])

            return []
    finally:
        if owns_driver:
            drv.close()


def get_sensors(unit: str, driver: Optional[Driver] = None) -> List[Dict[str, Any]]:
    """Retrieve all physical sensors measuring or monitoring the specified unit.

    Args:
        unit: Unit identifier (e.g., 'UNIT_REACTOR' or 'HX-102').
        driver: Optional active Neo4j driver.

    Returns:
        List[Dict[str, Any]]: List of sensors with id/name, tag, unit, and description.
    """
    query = """
    MATCH (s:Sensor)-[:MEASURES|MONITORS]->(u {id: $unit_id})
    RETURN DISTINCT coalesce(s.id, s.name) AS id,
                    s.name AS name,
                    s.tag AS tag,
                    s.unit AS unit,
                    s.description AS description
    ORDER BY id ASC;
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    try:
        with drv.session() as session:
            result = session.run(query, unit_id=unit)
            return [dict(record) for record in result]
    finally:
        if owns_driver:
            drv.close()


# Compatibility aliases
get_upstream = get_upstream_units
get_path = get_shortest_path


class KnowledgeGraphQueries:
    """Object-oriented interface for querying the chemical process knowledge graph."""

    def __init__(self, driver: Optional[Driver] = None):
        """Initialize query interface with optional Neo4j driver."""
        self.driver = driver

    def get_neighbors(self, unit: str, hops: int = 1) -> List[Dict[str, Any]]:
        """Retrieve neighboring equipment units within hops distance."""
        return get_neighbors(unit, hops=hops, driver=self.driver)

    def get_upstream_units(self, unit: str) -> List[Dict[str, Any]]:
        """Retrieve upstream units feeding into target unit."""
        return get_upstream_units(unit, driver=self.driver)

    get_upstream = get_upstream_units

    def get_downstream(self, unit: str) -> List[Dict[str, Any]]:
        """Retrieve downstream units fed by unit."""
        return get_downstream(unit, driver=self.driver)

    def get_failure_modes(self, unit: str) -> List[Dict[str, Any]]:
        """Retrieve candidate failure modes for unit."""
        return get_failure_modes(unit, driver=self.driver)

    def get_shortest_path(self, a: str, b: str) -> List[str]:
        """Find the flow path between units a and b."""
        return get_shortest_path(a, b, driver=self.driver)

    get_path = get_shortest_path

    def get_sensors(self, unit: str) -> List[Dict[str, Any]]:
        """Retrieve sensors measuring unit."""
        return get_sensors(unit, driver=self.driver)

    def get_unit_for_sensor(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve unit measured by the given sensor."""
        query = """
        MATCH (s:Sensor {id: $sensor_id})-[:MEASURES]->(u:Unit)
        RETURN u.id AS id, u.name AS name, u.description AS description
        """
        with self.driver.session() as session:
            result = session.run(query, sensor_id=sensor_id)
            record = result.single()
            return dict(record) if record else None

    def get_candidate_failure_modes(self, sensor_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve candidate failure modes for units measured by the given sensors."""
        query = """
        MATCH (s:Sensor)-[:MEASURES]->(u:Unit)-[:SUSCEPTIBLE_TO]->(f:FailureMode)
        WHERE s.id IN $sensor_ids
        RETURN DISTINCT f.id AS failure_id, f.code AS code, f.name AS name,
                        f.category AS category, f.severity AS severity,
                        f.description AS description, [s.id] AS matching_sensors,
                        u.id AS unit_id, u.name AS unit_name
        """
        with self.driver.session() as session:
            result = session.run(query, sensor_ids=sensor_ids)
            return [dict(record) for record in result]

    def get_full_subgraph(self) -> Dict[str, Any]:
        """Retrieve full plant topology graph for visualization."""
        return get_full_subgraph(driver=self.driver)


def get_full_subgraph(driver: Optional[Driver] = None) -> Dict[str, Any]:
    """Retrieve all plant units, sensors, and failure modes with relationships for Cytoscape.

    Returns:
        Dict[str, Any]: Structured dictionary with nodes, edges, and Cytoscape elements.
    """
    owns_driver = driver is None
    drv = get_driver() if owns_driver else driver

    nodes_map = {}
    edges = []
    cytoscape_elements = []

    q_nodes = """
    MATCH (n)
    WHERE n:Unit OR n:Sensor OR n:FailureMode OR n:Equipment
    RETURN n.id AS id,
           labels(n)[0] AS label,
           coalesce(n.name, n.id) AS name,
           n.description AS description,
           n.severity AS severity,
           n.category AS category,
           n.code AS code
    """

    q_rels = """
    MATCH (source)-[r]->(target)
    WHERE (source:Unit OR source:Sensor OR source:FailureMode OR source:Equipment)
      AND (target:Unit OR target:Sensor OR target:FailureMode OR target:Equipment)
    RETURN source.id AS source,
           target.id AS target,
           type(r) AS type,
           elementId(r) AS rel_id
    """

    try:
        with drv.session() as session:
            for record in session.run(q_nodes):
                nid = record["id"]
                if not nid:
                    continue
                node_data = {
                    "id": nid,
                    "label": record["label"],
                    "name": record["name"],
                    "description": record["description"] or "",
                    "severity": record["severity"],
                    "category": record["category"],
                    "code": record["code"],
                }
                nodes_map[nid] = node_data
                cytoscape_elements.append({
                    "group": "nodes",
                    "data": node_data
                })

            for record in session.run(q_rels):
                src = record["source"]
                tgt = record["target"]
                rtype = record["type"]
                eid = f"edge_{src}_{tgt}_{rtype}"
                edge_data = {
                    "id": eid,
                    "source": src,
                    "target": tgt,
                    "type": rtype,
                    "label": rtype,
                }
                edges.append(edge_data)
                cytoscape_elements.append({
                    "group": "edges",
                    "data": edge_data
                })

        return {
            "nodes": list(nodes_map.values()),
            "edges": edges,
            "elements": cytoscape_elements,
        }
    finally:
        if owns_driver:
            drv.close()


if __name__ == "__main__":
    print("--- Testing Phase 2 Knowledge Graph Queries Standalone ---")
    driver = get_driver()
    try:
        # Test 1: get_neighbors(UNIT_REACTOR, hops=1)
        neighbors = get_neighbors("UNIT_REACTOR", hops=1, driver=driver)
        print(f"1. Neighbors of UNIT_REACTOR (hops=1): {[n['id'] for n in neighbors]}")

        # Test 2: get_upstream_units(UNIT_SEPARATOR)
        upstream = get_upstream_units("UNIT_SEPARATOR", driver=driver)
        print(f"2. Upstream units of UNIT_SEPARATOR: {[u['id'] for u in upstream]}")

        # Test 3: get_failure_modes(UNIT_REACTOR)
        failures = get_failure_modes("UNIT_REACTOR", driver=driver)
        print(f"3. Failure modes for UNIT_REACTOR: {[f['code'] + ' (' + f['name'] + ')' for f in failures]}")

        # Test 4: get_shortest_path(UNIT_FEED, UNIT_STRIPPER)
        path = get_shortest_path("UNIT_FEED", "UNIT_STRIPPER", driver=driver)
        print(f"4. Shortest path from UNIT_FEED to UNIT_STRIPPER: {path}")

        # Test 5: get_sensors(UNIT_REACTOR)
        sensors = get_sensors("UNIT_REACTOR", driver=driver)
        print(f"5. Sensors on UNIT_REACTOR: {[s['id'] for s in sensors]}")

        print("\n[PASS] All Phase 2 queries executed successfully.")
    except Exception as err:
        print(f"[FAIL] Query test failed: {err}")
        sys.exit(1)
    finally:
        driver.close()
